"""Disposable CLI integration fixture; run factory-startup background Blender.

Usage: blender -b --factory-startup --python-exit-code 1 --python THIS -- OUT
OUT must not exist. Does not open or modify authoring checkpoints.
"""
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
import bpy

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/asset-pipeline'))
from pipeline import atlas_layout
from pipeline.common import PipelineError
from pipeline.job import validate
from pipeline.bake import bake_preserved_atlas

out = Path(sys.argv[-1]).resolve()
assert bpy.app.background and not out.exists(), 'new disposable output required'
out.mkdir(parents=True)
spec = importlib.util.spec_from_file_location('entry', ROOT/'tools/asset-pipeline/pipeline.py')
entry = importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)
objects=[]
for index in range(2):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(index*2,0,0))
    obj=bpy.context.object; obj.name=f'Fixture_{index}'
    obj.data.uv_layers.active.name='AtlasUV'
    mat=bpy.data.materials.new(f'FixtureMaterial_{index}'); mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(0.12 if index==0 else 0.6, .2, .3,1)
    shader.inputs['Roughness'].default_value=.25 if index==0 else .75
    shader.inputs['Metallic'].default_value=float(index)
    obj.data.materials.append(mat); objects.append(obj)
assert not atlas_layout.validate(objects)['ok'], 'must catch cross-object overlap'
names=[o.name for o in objects]
job={'objects':names,'out_dir':str(out/'uv'),'pack':True,'unwrap':False,
     'gap_margin':9/128,'overlap_resolution':128,'min_gap_px':8,'require_disjoint':True,
     'blend':'packed.blend'}
validate(job,'uv')
assert entry.verb_uv(job,SimpleNamespace(report=None))==0
report=json.loads((out/'uv/uv.json').read_text())
assert report['global_layout']['ok']
assert report['global_layout']['gap_lower_bound_px'] >= 8
before=atlas_layout.corner_snapshot(objects,'AtlasUV')
(out/'before_corners.json').write_text(json.dumps(before))
# Same bounds, different correspondence must NOT compare equal.
layer=objects[0].data.uv_layers['AtlasUV']
old=[tuple(v.uv) for v in layer.data]
layer.data[0].uv,layer.data[1].uv=old[1],old[0]
assert atlas_layout.corner_snapshot(objects,'AtlasUV') != before
for item,p in zip(layer.data,old): item.uv=p
try:
    bake_preserved_atlas(objects,out/'unsafe',resolution=128,margin=5,samples=1)
    raise AssertionError('unsafe dilation should fail')
except PipelineError:
    pass
assert not (out/'unsafe/textures').exists()
job={'objects':names,'out_dir':str(out/'bake'),'preserve_layout':True,
     'resolution':128,'margin':4,'samples':1,'alpha':False}
validate(job,'bake')
assert entry.verb_bake(job,SimpleNamespace(report=None))==0
assert atlas_layout.corner_snapshot(objects,'AtlasUV')==before
assert all(len(o.material_slots)==1 for o in objects)
assert len([o for o in bpy.data.objects if o.type=='MESH'])==3, 'no bake duplicates'
# Sample data channels at each chart's interior from images reloaded from disk.
for channel,expected in [('roughness',[.25,.75]),('metallic',[0,1])]:
    image=bpy.data.images.load(str(out/f'bake/textures/atlas_{channel}.png'),check_existing=False)
    image.colorspace_settings.name='Non-Color'
    for obj,value in zip(objects,expected):
        coords=[v.uv for v in obj.data.uv_layers['AtlasUV'].data]
        x=int(sum(p.x for p in coords)/len(coords)*128)
        y=int(sum(p.y for p in coords)/len(coords)*128)
        actual=image.pixels[(y*128+x)*4]
        assert abs(actual-value)<.015,(channel,obj.name,actual,value)
(out/'PASS.json').write_text(json.dumps({'uv_cli_global_pack':True,
    'preserve_bake_cli':True,'unsafe_margin_rejected':True,
    'bounds_only_false_positive_rejected':True,'data_channel_interior_samples':True,
    'saved_blend':str(out/'bake/atlas_source_001.blend')} ,indent=2))
print('ATLAS_MODES_PASS',out)
