"""Read-only authored mesh inspection. bpy is imported only inside snapshot().

Fingerprints intentionally separate geometry, UV, transform, assignments/graphs,
and image bytes. The bake merge signature is unsuitable: it rounds scalars and
does not recursively protect groups or packed content. No approval hash changes.
"""
import hashlib
import math
from pathlib import Path
import struct

from .common import PipelineError, sha256_file
from .preservation import FIELDS, LIMITS, digest, names, validate_snapshot


def floats(values):
    """Exact Blender float32 bytes, without decimal quantization."""
    result = hashlib.sha256()
    for value in values:
        if not math.isfinite(value):
            raise PipelineError('nonfinite authored coordinate/UV')
        result.update(struct.pack('<f', value))
    return result.hexdigest()


def field(value, issues=()):
    return {'status': 'unsupported' if issues else 'ok', 'hash': digest(value),
            'issues': sorted(set(issues))}


def scalar(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, (set, frozenset)):
        return [scalar(x) for x in sorted(value)]
    try:
        return [scalar(x) for x in value]
    except TypeError as exc:
        raise PipelineError('unsupported RNA value') from exc


def settings(owner):
    """Only scalar RNA settings; pointer dependencies are handled explicitly."""
    ignored = {'rna_type', 'session_uid', 'name', 'label', 'location', 'width', 'height', 'dimensions',
               'select', 'show_options', 'show_preview', 'show_texture', 'hide', 'color',
               'use_custom_color', 'warning_propagation', 'bl_description', 'bl_label',
               'bl_icon', 'bl_idname', 'bl_static_type'}
    result = {}
    for prop in owner.bl_rna.properties:
        if prop.identifier in ignored or prop.identifier.startswith('bl_') or prop.type in ('POINTER', 'COLLECTION'):
            continue
        result[prop.identifier] = scalar(getattr(owner, prop.identifier))
    return result


def image_record(image, allowed):
    issues = []
    content = []
    # Image RNA does not support animation_data in every Blender version.
    # Absence is a capability difference, not an unresolved animation dependency.
    if getattr(image, 'animation_data', None):
        issues.append('animated/driven image')
    if image.source not in ('FILE', 'GENERATED'):
        issues.append('unsupported image source: ' + image.source)
    packed = list(image.packed_files)
    if packed:
        for item in packed:
            data = bytes(item.packed_file.data)
            content.append({'hash': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    elif image.packed_file:
        data = bytes(image.packed_file.data)
        content.append({'hash': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    else:
        # Generated pixels are not a portable byte-backed dependency until packed.
        import bpy
        path = Path(bpy.path.abspath(image.filepath, library=image.library)).resolve() if image.filepath else None
        if path is not None and path in allowed and image.source == 'FILE':
            try:
                content.append({'hash': sha256_file(path), 'bytes': path.stat().st_size})
            except OSError as exc:
                issues.append('external image read failed: ' + str(exc))
        else:
            issues.append('image bytes unresolved (external reads require exact allowlist or pack image)')
    if image.is_dirty:
        issues.append('image has unsaved pixel edits; encoded bytes may be stale')
    return dict(name=image.name, source=image.source, size=list(image.size), channels=image.channels,
                colorspace=image.colorspace_settings.name, alpha_mode=image.alpha_mode,
                content=content, packed=bool(packed or image.packed_file)), issues


def graph(tree, images, issues, stack=()):
    if tree is None:
        return None
    if tree.as_pointer() in stack:
        issues.append('recursive node group')
        return None
    stack = (*stack, tree.as_pointer())
    if tree.animation_data:
        issues.append('animated/driven node tree')
    nodes = []
    for node in sorted(tree.nodes, key=lambda n: n.name):
        entry = dict(name=node.name, type=node.bl_idname, settings=settings(node), inputs=[])
        for attr in ('object', 'texture', 'script'):
            if getattr(node, attr, None):
                issues.append('unresolved node dependency: ' + node.name + '.' + attr)
        for socket in node.inputs:
            if hasattr(socket, 'default_value'):
                try:
                    entry['inputs'].append([socket.identifier, scalar(socket.default_value)])
                except PipelineError:
                    issues.append('unresolved socket dependency: ' + node.name)
        if getattr(node, 'image', None):
            images[node.image.as_pointer()] = node.image
            entry['image'] = node.image.name
        if getattr(node, 'node_tree', None):
            entry['group'] = graph(node.node_tree, images, issues, stack)
        if hasattr(node, 'color_ramp'):
            ramp = node.color_ramp
            entry['ramp'] = [settings(ramp), [[e.position, list(e.color)] for e in ramp.elements]]
        if getattr(node, 'mapping', None):
            issues.append('curve mapping dependency not implemented: ' + node.name)
        if getattr(node, 'texture_mapping', None):
            entry['texture_mapping'] = settings(node.texture_mapping)
        if getattr(node, 'color_mapping', None):
            mapping = node.color_mapping
            entry['color_mapping'] = settings(mapping)
            ramp = mapping.color_ramp
            entry['color_mapping_ramp'] = [settings(ramp), [[e.position, list(e.color)] for e in ramp.elements]]
        # Only the following graph families have bounded local dependencies.
        safe = ('BSDF_', 'MIX', 'ADD_SHADER', 'OUTPUT_MATERIAL', 'VALUE', 'RGB',
                'MATH', 'VECT_MATH', 'VECTOR_MATH', 'NORMAL', 'BUMP', 'NORMAL_MAP',
                'TEX_IMAGE', 'TEX_COORD', 'UVMAP', 'MAPPING', 'VALTORGB',
                'GROUP', 'GROUP_INPUT', 'GROUP_OUTPUT', 'REROUTE', 'FRAME',
                'SEPRGB', 'COMBRGB', 'SEPXYZ', 'COMBXYZ', 'EMISSION')
        if not any(node.type == s or (s == 'BSDF_' and node.type.startswith(s)) for s in safe):
            issues.append('unverified procedural/context node: ' + node.bl_idname)
        nodes.append(entry)
    links = sorted([l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier] for l in tree.links)
    return {'nodes': nodes, 'links': links}


def material_record(material, images, issues):
    if material is None:
        return None
    if material.animation_data:
        issues.append('animated/driven material')
    if material.library:
        issues.append('linked material library dependency not verified')
    return {'name': material.name, 'settings': settings(material),
            'graph': graph(material.node_tree, images, issues)}


def mesh_counts(mesh):
    # Polygon fan triangle count is exact for triangle count, without mutating caches.
    return dict(vertices=len(mesh.vertices), edges=len(mesh.edges), polygons=len(mesh.polygons),
                triangles=sum(max(0, p.loop_total - 2) for p in mesh.polygons))


def cost_report(objects, images):
    import bpy
    unique = {o.data.as_pointer(): o.data for o in objects}
    mats = {m.as_pointer(): m for o in objects for m in (s.material for s in o.material_slots) if m}
    def node_count(tree, seen=None):
        seen = set() if seen is None else seen
        if tree is None or tree.as_pointer() in seen:
            return 0
        seen.add(tree.as_pointer())
        return len(tree.nodes) + sum(node_count(getattr(n, 'node_tree', None), seen) for n in tree.nodes)
    result = dict(status='ok', authored_unique_meshes=len(unique),
                  authored_unique_triangles=sum(mesh_counts(m)['triangles'] for m in unique.values()),
                  authored_per_object={o.name: mesh_counts(o.data) for o in objects},
                  authored_object_triangles=sum(mesh_counts(o.data)['triangles'] for o in objects),
                  unique_materials=len(mats), material_node_counts={m.name: node_count(m.node_tree) for m in mats.values()},
                  viewport={'linked_instances': 0, 'direct_objects': 0, 'triangles': 0}, errors=[],
                  limits=['Current VIEWPORT depsgraph only, not render-visible triangles, GPU cost or draw calls.',
                          'Render modifier settings can differ. Realized geometry is inside evaluated meshes.',
                          'Instance ownership uses original object or immediate original parent; nested ownership can be unresolved.',
                          'RGBA8 base-level estimate excludes mipmaps/compression/precision; not actual GPU memory.',
                          'Content duplicates are informational, not deletion recommendations.'])
    selected = {o.as_pointer() for o in objects}
    try:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for instance in depsgraph.object_instances:
            obj = instance.object
            owner = instance.parent if instance.is_instance else obj
            owned = owner and owner.original.as_pointer() in selected
            if not owned:
                continue
            if obj.type != 'MESH':
                result['errors'].append('owned nonmesh instance unsupported: ' + obj.name)
                continue
            mesh = None
            try:
                mesh = obj.to_mesh()
                result['viewport']['triangles'] += mesh_counts(mesh)['triangles']
                result['viewport']['linked_instances' if instance.is_instance else 'direct_objects'] += 1
            finally:
                if mesh is not None:
                    obj.to_mesh_clear()
    except Exception as exc:
        result['errors'].append('viewport evaluation failed: ' + str(exc))
    result['status'] = 'error' if result['errors'] else 'limited'
    result['images'] = list(images.values())
    result['unique_image_datablocks'] = len(images)
    content = {c['hash']: c['bytes'] for im in images.values() for c in im['content'] if im['packed']}
    result['packed_unique_content_bytes'] = sum(content.values())
    result['packed_unique_content_count'] = len(content)
    result['rgba8_base_level_estimate_bytes'] = sum(im['size'][0] * im['size'][1] * 4 for im in images.values())
    return result


def snapshot(object_names, external_images=()):
    """Inspect explicit named mesh objects without opening files or changing scene state."""
    import bpy
    names(object_names, True)
    objects = []
    for name in object_names:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != 'MESH' or bpy.context.view_layer.objects.get(name) is not obj:
            raise PipelineError('missing/nonmesh/not current view-layer object: ' + name)
        objects.append(obj)
    allowed = {Path(p).resolve() for p in external_images}
    result = dict(version=1, context=dict(frame=bpy.context.scene.frame_current,
                  view_layer=bpy.context.view_layer.name, source_path=bpy.data.filepath),
                  objects={}, cost={}, limits=list(LIMITS) + ['Node renames can change graph hashes; UI node positions do not.',
                  'Authored base meshes only. Modifier/shape-key state is not protected.'])
    all_images = {}
    for obj in objects:
        mesh = obj.data
        geometry = dict(coordinates=floats(v for vert in mesh.vertices for v in vert.co),
                        edges=[list(e.vertices) for e in mesh.edges],
                        polygons=[list(p.vertices) for p in mesh.polygons])
        uv = [dict(name=layer.name, active_render=layer.active_render,
                   values=floats(v for loop in layer.data for v in loop.uv)) for layer in mesh.uv_layers]
        transforms = dict(local=[list(r) for r in obj.matrix_local], world=[list(r) for r in obj.matrix_world],
                          parent_inverse=[list(r) for r in obj.matrix_parent_inverse],
                          parent=obj.parent.name if obj.parent else None, parent_type=obj.parent_type,
                          parent_bone=obj.parent_bone, parent_vertices=list(obj.parent_vertices))
        issues, references = [], {}
        materials = [dict(link=s.link, material=material_record(s.material, references, issues)) for s in obj.material_slots]
        image_records, image_issues = [], []
        for pointer, image in references.items():
            record, unresolved = image_record(image, allowed)
            image_records.append(record)
            image_issues.extend(unresolved)
            all_images[pointer] = record
        # Geometry/UV modifier effects are intentionally outside base-data fingerprints.
        fields = dict(geometry=field(geometry), uv=field({'layers': uv, 'active_index': mesh.uv_layers.active_index}),
                      transforms=field(transforms),
                      materials=field({'slots': materials, 'polygon_slots': [p.material_index for p in mesh.polygons]}, issues),
                      images=field(sorted(image_records, key=lambda r: r['name']), image_issues))
        fields['geometry']['components'] = {'coordinates': geometry['coordinates'],
            'topology': digest({'edges': geometry['edges'], 'polygons': geometry['polygons']})}
        result['objects'][obj.name] = dict(counts=mesh_counts(mesh), fields=fields)
    result['cost'] = cost_report(objects, all_images)
    return validate_snapshot(result)
