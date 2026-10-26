"""Disposable Blender-only synthetic regression. Parent executes, never on source assets.

blender --background --factory-startup --disable-autoexec --python fixtures/check_preservation.py
Creates new prefixed datablocks, never deletes existing data, opens/saves/renders nothing.
Raises on regression. Prints JSON summary. No source-file writes.
"""
import json
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.inspection import snapshot, floats
from pipeline.preservation import FIELDS, compare


def main():
    import bpy
    prefix = 'PreservationFixture_' + uuid.uuid4().hex[:8]
    scene = bpy.context.scene
    def existing_state():
        return {o.name: (floats(v for p in o.data.vertices for v in p.co),
                         tuple(s.material.name if s.material else None for s in o.material_slots))
                for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith(prefix)}
    protected = existing_state()
    state = (scene.frame_current, tuple(o.name for o in bpy.context.selected_objects),
             bpy.context.view_layer.objects.active)
    mesh = bpy.data.meshes.new(prefix + 'Mesh')
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)], [],
                     [(0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)])
    mesh.uv_layers.new(name='UV')
    objects = []
    for part in ('Trunk', 'Canopy', 'Shared'):
        obj = bpy.data.objects.new(prefix + part, mesh if part != 'Canopy' else mesh.copy())
        scene.collection.objects.link(obj)
        objects.append(obj)
    trunk, canopy, shared = objects
    material = bpy.data.materials.new(prefix + 'Material')
    material.use_nodes = True
    canopy.data.materials.append(material)
    image = bpy.data.images.new(prefix + 'Image', width=2, height=2)
    image.pixels[:] = [1, 0, 0, 1] * 4
    image.pack()
    texture = material.node_tree.nodes.new('ShaderNodeTexImage')
    texture.image = image
    unused = bpy.data.images.new(prefix + 'Unused', width=8, height=8)
    unrelated = bpy.data.objects.new(prefix + 'Unrelated', mesh.copy())
    scene.collection.objects.link(unrelated)
    names = [o.name for o in objects]
    bpy.context.view_layer.update()
    def capture():
        return snapshot(names)
    base = capture()
    assert compare(base, base, {'version': 1, 'objects': {}})['status'] == 'pass'
    assert base['cost']['authored_unique_meshes'] == 2
    assert base['cost']['authored_unique_triangles'] == 8
    assert base['cost']['authored_object_triangles'] == 12
    assert base['cost']['unique_image_datablocks'] == 1
    assert base['cost']['images'][0]['name'] != unused.name
    assert base['cost']['viewport']['direct_objects'] == 3
    assert base['objects'] == capture()['objects'], 'inspection mutated authored data'
    def detects(field, mutate, restore):
        mutate()
        bpy.context.view_layer.update()
        changed = capture()
        assert base['objects'][canopy.name]['fields'][field]['hash'] != changed['objects'][canopy.name]['fields'][field]['hash'], field
        assert compare(base, changed, {'version': 1, 'objects': {}})['status'] == 'fail'
        restore()
        bpy.context.view_layer.update()
        assert base['objects'] == capture()['objects'], 'restore or read-only regression: ' + field
    detects('geometry', lambda: setattr(canopy.data.vertices[0].co, 'x', .0000001), lambda: setattr(canopy.data.vertices[0].co, 'x', 0))
    detects('geometry', lambda: setattr(canopy.data.loops[1], 'vertex_index', 2), lambda: setattr(canopy.data.loops[1], 'vertex_index', 1))
    detects('uv', lambda: setattr(canopy.data.uv_layers[0].data[0].uv, 'x', .25), lambda: setattr(canopy.data.uv_layers[0].data[0].uv, 'x', 0))
    canopy.data.uv_layers[0].data[0].uv.x = .25
    uv_task = {'version': 1, 'objects': {canopy.name: {'preserve': [f for f in FIELDS if f != 'uv'], 'require_changes': ['uv']}}}
    assert compare(base, capture(), uv_task)['status'] == 'pass'
    canopy.data.uv_layers[0].data[0].uv.x = 0
    detects('transforms', lambda: setattr(canopy.location, 'x', 2), lambda: setattr(canopy.location, 'x', 0))
    bsdf = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    socket = bsdf.inputs['Roughness']
    original = socket.default_value
    detects('materials', lambda: setattr(socket, 'default_value', .123), lambda: setattr(socket, 'default_value', original))
    detects('materials', lambda: setattr(canopy.data.polygons[0], 'material_index', 1), lambda: setattr(canopy.data.polygons[0], 'material_index', 0))
    old_name = texture.name
    detects('materials', lambda: setattr(texture, 'name', old_name + '_changed'), lambda: setattr(texture, 'name', old_name))
    # Image content: separate packed datablock avoids relying on repack overwriting old packed data.
    alternate = bpy.data.images.new(prefix + 'Alternate', width=2, height=2)
    alternate.pixels[:] = [0, 1, 0, 1] * 4
    alternate.pack()
    assert bytes(image.packed_file.data) != bytes(alternate.packed_file.data)
    detects('images', lambda: setattr(texture, 'image', alternate), lambda: setattr(texture, 'image', image))
    # Evaluated output is distinct from authored triangles.
    modifier = canopy.modifiers.new(prefix + 'Subdiv', 'SUBSURF')
    modifier.levels = 1
    bpy.context.view_layer.update()
    evaluated = capture()
    assert evaluated['cost']['authored_object_triangles'] == 12
    assert evaluated['cost']['viewport']['triangles'] > base['cost']['viewport']['triangles']
    modifier.show_viewport = False
    # Mesh owners support vertex/face instancing, not collection instancing.
    # A parented source child exercises actual repeated depsgraph instances while
    # keeping the inspected owner an explicitly named mesh (no scope widening).
    instance_child = bpy.data.objects.new(prefix + 'InstanceChild', mesh.copy())
    scene.collection.objects.link(instance_child)
    instance_child.parent = shared
    vertex_mode = next(item.identifier for item in shared.bl_rna.properties['instance_type'].enum_items
                       if item.identifier == 'VERTS')
    shared.instance_type = vertex_mode
    bpy.context.view_layer.update()
    instanced = capture()
    assert instanced['cost']['viewport']['linked_instances'] >= 1
    assert state == (scene.frame_current, tuple(o.name for o in bpy.context.selected_objects), bpy.context.view_layer.objects.active)
    assert protected == existing_state(), 'unrelated mesh/material mutation'
    print(json.dumps({'status': 'pass', 'fixture': prefix, 'fields': list(FIELDS),
                      'cost': instanced['cost'], 'limits': 'Synthetic only; no asset acceptance.'}, allow_nan=False))


if __name__ == '__main__':
    main()
