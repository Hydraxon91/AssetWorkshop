"""Versioned box recipes and bake-copy preparation; bpy is imported lazily.

Development adapter, not a general modeller. Recipes are data, never Python.
Existing packing, baking, health and capture implementations remain authoritative.
"""
import hashlib
import json
import math
import re
from pathlib import Path

from .common import PipelineError

VERSION = 1
BAKE_PREFIX = 'Bake__'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False,
                                    separators=(',', ':')).encode()).hexdigest()


def material_content(record):
    """Fixed-recipe material content, excluding nonvisual ID ownership metadata.

    Copy creation changes users; preserved baking adds a fake user to retain
    originals. Neither changes shading. Node graphs/inputs remain exact.
    """
    if record is None:
        return None
    return {**record, 'settings': {k: v for k, v in record['settings'].items()
                                 if k not in ('users', 'use_fake_user')}}


def fields(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= set(value) or set(value) - set(required) - set(optional):
        raise PipelineError('missing or unsupported recipe fields')


def number(value, low, high):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise PipelineError(f'expected finite number in [{low}, {high}]')
    return float(value)


def vector(value, low, high):
    if not isinstance(value, list) or len(value) != 3:
        raise PipelineError('expected three numbers')
    return [number(v, low, high) for v in value]


def name(value):
    if (not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,47}', value)
            or value.startswith(BAKE_PREFIX)):
        raise PipelineError('names must be simple, <=48 characters, and not start Bake__')
    return value


def validate(recipe):
    """Return a canonical recipe, before importing bpy or changing a scene."""
    fields(recipe, ('version', 'root', 'parts'), ('material',))
    if type(recipe['version']) is not int or recipe['version'] != VERSION:
        raise PipelineError('unsupported recipe version')
    root = name(recipe['root'])
    parts = recipe['parts']
    if not isinstance(parts, list) or not 1 <= len(parts) <= 16:
        raise PipelineError('recipe requires 1..16 parts')
    seen, result = {root}, []
    for part in parts:
        fields(part, ('name', 'dimensions', 'location'), ('rotation', 'bevel'))
        part_name = name(part['name'])
        if part_name in seen:
            raise PipelineError('duplicate part/root name')
        seen.add(part_name)
        dims = vector(part['dimensions'], .001, 10)
        bevel = part.get('bevel', {'width': 0, 'segments': 1})
        fields(bevel, ('width', 'segments'))
        width = number(bevel['width'], 0, min(dims) / 4)
        segments = bevel['segments']
        if type(segments) is not int or not 1 <= segments <= 4:
            raise PipelineError('bevel segments must be integer 1..4')
        result.append(dict(name=part_name, dimensions=dims,
                           location=vector(part['location'], -100, 100),
                           rotation=vector(part.get('rotation', [0, 0, 0]), -360, 360),
                           bevel=dict(width=width, segments=segments)))
    material = recipe.get('material', {'scale': 25, 'bump': .0005})
    fields(material, ('scale', 'bump'))
    return dict(version=VERSION, root=root, parts=result,
                material=dict(scale=number(material['scale'], .1, 1000),
                              bump=number(material['bump'], 0, .002)))


def load(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise PipelineError('duplicate JSON key: ' + key)
            out[key] = value
        return out
    return validate(json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique))


def part_names(recipe, baked=False):
    return [(BAKE_PREFIX if baked else '') + p['name'] for p in recipe['parts']]


def stage_plan(recipe_path, directory, blender, phase='geometry', source=None):
    """Data-only preset generator for the EXISTING review_worker runner.

    Return plan + companion jobs. Never starts a process or edits a scene.
    """
    from .common import REPO_ROOT
    recipe = load(recipe_path)
    directory = Path(directory).resolve()
    if not directory.is_relative_to(REPO_ROOT / '.dev-shots'):
        raise PipelineError('preset output must be under project .dev-shots')
    def rel(p):
        p = Path(p).resolve()
        if not p.is_relative_to(REPO_ROOT):
            raise PipelineError('preset inputs must remain in project')
        return p.relative_to(REPO_ROOT).as_posix()
    recipe_path = rel(recipe_path)
    def target(s):
        return rel(directory / s)
    adapter = 'tools/asset-pipeline/scripts/primitive_recipe.py'
    save = 'tools/asset-pipeline/scripts/review_blender.py'
    stages, jobs, previous = [], {}, []
    def add(id, kind, role, source, script, args, outputs, evidence=None):
        nonlocal previous
        stages.append(dict(id=id, kind=kind, role=role, source=source, script=script,
                           args=args, outputs=outputs, requires=previous[:], evidence=evidence or {}))
        previous = [id]
    if phase == 'geometry':
        definitions = [('before', 'master', None, adapter,
                        ['build', '--recipe', recipe_path, '--empty-startup', '--out', target('master_work.blend')],
                        target('master_work.blend')),
                       ('after', 'prepared', target('master.blend'), adapter,
                        ['prepare', '--recipe', recipe_path, '--out', target('prepared_work.blend')],
                        target('prepared_work.blend'))]
    elif phase == 'appearance' and source:
        source = rel(source)
        copies = part_names(recipe, True)
        jobs['uv-job.json'] = dict(objects=copies, out_dir=target('uv'),
            unwrap=True, pack=True, gap_margin=12/256, overlap_resolution=256,
            min_gap_px=10, require_disjoint=True, blend='packed.blend')
        jobs['bake-job.json'] = dict(objects=copies, out_dir=target('bake'),
            preserve_layout=True, resolution=256, margin=4, samples=4,
            alpha=False, export=False, blend='baked.blend')
        definitions = [('before', 'uv', source, 'tools/asset-pipeline/pipeline.py',
                        ['uv', '--job', target('uv-job.json')], target('uv/packed.blend')),
                       ('after', 'baked', target('uv.blend'), 'tools/asset-pipeline/pipeline.py',
                        ['bake', '--job', target('bake-job.json')], target('bake/baked.blend'))]
    else:
        raise PipelineError('need geometry, or appearance with an existing prepared source')
    for role, stage, src, script, arguments, work in definitions:
        checkpoint, report = target(stage+'.blend'), target(stage+'_check.json')
        image, meta = target(stage+'.png'), target(stage+'_capture.json')
        add(role+'_build', 'construct', role, src, script, arguments, [work])
        add(role+'_save', 'save', role, work, save, ['save', '--out', checkpoint], [checkpoint], {'file': checkpoint})
        add(role+'_check', 'check', role, checkpoint, adapter,
            ['check', '--recipe', recipe_path, '--stage', stage, '--out', report], [report], {'file': report})
        add(role+'_capture', 'capture', role, checkpoint, adapter,
            ['capture', '--recipe', recipe_path, '--report', report, '--out', image, '--metadata', meta],
            [image, meta], {'file': image, 'metadata': meta, 'view': 'three_quarter'})
    # No sheet: master and prepared inventories intentionally differ. Keep actual
    # visibility metadata; do not falsify it to satisfy matched-sheet equality.
    return dict(version=1, goal='Primitive recipe '+phase+' technical fixture',
                views=['three_quarter'], construction_stop=5, deadline=12,
                execution_mode='scripted-disposable',
                blender=str(Path(blender).resolve()), stages=stages), jobs


def _background():
    import bpy
    if not bpy.app.background or bpy.context.mode != 'OBJECT':
        raise PipelineError('background Blender in Object Mode required')


def _root(recipe):
    import bpy
    obj = bpy.data.objects.get(recipe['root'])
    if obj is None or obj.type != 'EMPTY' or obj.get('recipe_digest') != digest(recipe):
        raise PipelineError('missing root or recipe/checkpoint mismatch')
    return obj


def _sources(recipe):
    import bpy
    return [bpy.data.objects[n] for n in part_names(recipe)]


def _evaluated(obj):
    import bpy
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    try:
        return dict(vertices=[list(v.co) for v in mesh.vertices],
                    faces=[list(p.vertices) for p in mesh.polygons],
                    matrix=[list(row) for row in ev.matrix_world])
    finally:
        ev.to_mesh_clear()


def _source_state(recipe):
    from .inspection import snapshot, material_record
    sources = _sources(recipe)
    fields_by_name = snapshot(part_names(recipe))['objects']
    for obj in sources:
        slots = [material_content(material_record(s.material, {}, [])) for s in obj.material_slots]
        fields_by_name[obj.name]['fields']['materials'] = dict(
            hash=digest(dict(slots=slots, face_slots=[p.material_index for p in obj.data.polygons])),
            scope='fixed recipe graph/settings; excludes users/use_fake_user only')
    # Preserve geometry, corner UVs, hierarchy/transforms, shader graphs and images.
    # Visibility is intentionally excluded: prepared checkpoints hide the master.
    return {obj.name: dict(fields=fields_by_name[obj.name]['fields'],
                           evaluated=digest(_evaluated(obj)),
                           modifiers=[dict(type=m.type, name=m.name,
                                           bevel=([m.width, m.segments, m.limit_method]
                                                  if m.type == 'BEVEL' else None),
                                           viewport=m.show_viewport, render=m.show_render)
                                      for m in obj.modifiers]) for obj in sources}


def _material(recipe):
    import bpy
    mat = bpy.data.materials.new(recipe['root'] + '_Material')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.get('Principled BSDF')
    coords = nodes.new('ShaderNodeTexCoord')
    checker = nodes.new('ShaderNodeTexChecker')
    checker.inputs['Scale'].default_value = recipe['material']['scale']
    checker.inputs['Color1'].default_value = (.08, .18, .32, 1)
    checker.inputs['Color2'].default_value = (.65, .42, .12, 1)
    links.new(coords.outputs['Object'], checker.inputs['Vector'])
    links.new(checker.outputs['Color'], shader.inputs['Base Color'])
    remap = nodes.new('ShaderNodeMapRange')
    remap.inputs['To Min'].default_value = .28
    remap.inputs['To Max'].default_value = .72
    links.new(checker.outputs['Fac'], remap.inputs['Value'])
    links.new(remap.outputs['Result'], shader.inputs['Roughness'])
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = recipe['material']['scale'] * 3
    links.new(coords.outputs['Object'], noise.inputs['Vector'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = recipe['material']['bump']
    bump.inputs['Strength'].default_value = .3
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], shader.inputs['Normal'])
    shader.inputs['Metallic'].default_value = 0
    return mat


def build(recipe, empty_startup=False):
    import bpy
    _background()
    # Only an explicitly authorized unsaved disposable startup may be reset.
    if bpy.data.filepath:
        raise PipelineError('build refuses a loaded .blend')
    if bpy.data.objects and not empty_startup:
        raise PipelineError('nonempty startup: explicit --empty-startup required')
    if empty_startup:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    root = bpy.data.objects.new(recipe['root'], None)
    scene.collection.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = .05
    mat = _material(recipe)
    for part in recipe['parts']:
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.object
        obj.name = part['name']
        obj.data.name = part['name'] + '_Mesh'
        obj.scale = part['dimensions']
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obj.location = part['location']
        obj.rotation_euler = [math.radians(v) for v in part['rotation']]
        obj.parent = root
        obj.data.materials.append(mat)
        if part['bevel']['width']:
            mod = obj.modifiers.new('Recipe_Bevel', 'BEVEL')
            mod.width = part['bevel']['width']
            mod.segments = part['bevel']['segments']
            mod.limit_method = 'ANGLE'
    bpy.context.view_layer.update()
    root['recipe_digest'] = digest(recipe)
    root['source_state'] = json.dumps(_source_state(recipe), sort_keys=True, allow_nan=False)
    root['stage'] = 'master'
    return dict(parts=part_names(recipe), root=root.name)


def prepare(recipe):
    import bpy
    _background()
    root = _root(recipe)
    if root.get('stage') != 'master':
        raise PipelineError('prepare requires a master, not an already prepared checkpoint')
    before = _source_state(recipe)
    if before != json.loads(root['source_state']):
        raise PipelineError('master changed since construction')
    new_names = [BAKE_PREFIX + recipe['root'], *part_names(recipe, True)]
    if any(bpy.data.objects.get(n) for n in new_names):
        raise PipelineError('bake object name collision')
    copies_root = bpy.data.objects.new(new_names[0], None)
    bpy.context.scene.collection.objects.link(copies_root)
    copies_root.empty_display_size = .05
    expected = {}
    deps = bpy.context.evaluated_depsgraph_get()
    for src, new_name in zip(_sources(recipe), part_names(recipe, True)):
        ev = src.evaluated_get(deps)
        mesh = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=deps)
        # Copy transform channels exactly: assigning matrix_world decomposes and
        # recomposes Euler rotations, changing float32 bits on rotated parts.
        obj = src.copy()
        obj.name = new_name
        obj.data = mesh
        obj.modifiers.clear()
        bpy.context.scene.collection.objects.link(obj)
        obj.parent = copies_root
        # Own local coordinates and world transform retain Object-space materials.
        obj['recipe_source'] = src.name
        expected[new_name] = digest(_evaluated(src))
    bpy.context.view_layer.update()
    for n, signature in expected.items():
        if digest(_evaluated(bpy.data.objects[n])) != signature:
            raise PipelineError('evaluated copy mismatch: ' + n)
    for src, n in zip(_sources(recipe), part_names(recipe, True)):
        if list(bpy.data.objects[n].data.materials) != list(src.data.materials):
            raise PipelineError('copy material mismatch: ' + n)
    if _source_state(recipe) != before:
        raise PipelineError('preparation altered master')
    root['copy_geometry'] = json.dumps(expected, sort_keys=True)
    root['stage'] = 'prepared'
    for src in _sources(recipe):
        src.hide_set(True)
        src.hide_render = True
    bpy.ops.object.select_all(action='DESELECT')
    for n in part_names(recipe, True):
        bpy.data.objects[n].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[part_names(recipe, True)[0]]
    return dict(parts=part_names(recipe, True), source_preserved=True)


def check(recipe, stage):
    """Runner-compatible report; no acceptance or UI usability assertion."""
    import bpy
    from mesh_diagnostics import health
    from .atlas_layout import validate as layout_validate
    _background()
    root = _root(recipe)
    failures, reports = [], {}
    expected_names = {recipe['root'], *part_names(recipe)}
    prepared = stage != 'master'
    if prepared:
        expected_names.update([BAKE_PREFIX + recipe['root'], *part_names(recipe, True)])
    if set(bpy.data.objects.keys()) != expected_names:
        failures.append('unexpected_or_missing_objects')
    if root.get('stage') != ('prepared' if prepared else 'master'):
        failures.append('stage_mismatch')
    actual_sources = set(part_names(recipe)) <= set(bpy.data.objects.keys())
    if actual_sources:
        try:
            if _source_state(recipe) != json.loads(root['source_state']):
                failures.append('master_preservation')
        except (AttributeError, KeyError, PipelineError) as exc:
            failures.append('master_snapshot: ' + str(exc))
    for n in sorted(expected_names):
        obj = bpy.data.objects.get(n)
        if obj is None or obj.type != 'MESH':
            continue
        r = reports[n] = health(obj)
        for mode in ('base', 'evaluated'):
            m = r[mode]
            if (any(m[k] for k in ('boundary_edges', 'nonmanifold_edges', 'wire_edges',
                                  'loose_verts', 'winding_conflicts', 'degenerate_faces'))
                    or m['islands'] != 1 or not all(c['closed'] for c in m['components'])):
                failures.append(n + ':' + mode + ':health')
        if obj.data.users != 1 or obj.hide_select or any(obj.lock_location) or any(obj.lock_rotation) or any(obj.lock_scale):
            failures.append(n + ':not_independently_editable')
    if prepared and set(part_names(recipe, True)) <= set(reports):
        expected = json.loads(root['copy_geometry'])
        for n in part_names(recipe, True):
            obj = bpy.data.objects[n]
            if obj.modifiers or digest(_evaluated(obj)) != expected.get(n):
                failures.append(n + ':copy_geometry')
            if obj.hide_get() or obj.hide_render:
                failures.append(n + ':copy_hidden')
        if stage != 'baked':
            for src, n in zip(_sources(recipe), part_names(recipe, True)):
                if list(bpy.data.objects[n].data.materials) != list(src.data.materials):
                    failures.append(n + ':copy_materials')
        for src in _sources(recipe):
            if not src.hide_get() or not src.hide_render:
                failures.append(src.name + ':source_not_isolated')
    layout = None
    if stage in ('uv', 'baked') and set(part_names(recipe, True)) <= set(reports):
        layout = layout_validate([bpy.data.objects[n] for n in part_names(recipe, True)], 'AtlasUV')
        failures.extend(layout['failures'])
    return dict(status='fail' if failures else 'pass', failures=failures,
                recipe_digest=digest(recipe), stage=stage, health=reports, layout=layout,
                limits=['No UI responsiveness or user acceptance claim.',
                        'Health/layout are not shader transfer or mip certification.'])
