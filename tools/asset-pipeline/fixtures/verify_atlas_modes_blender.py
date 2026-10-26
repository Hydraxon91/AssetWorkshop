"""Read-only fresh-process check of saved integration fixture."""
import json, sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline.atlas_layout import corner_snapshot, validate
out=Path(sys.argv[-1]).resolve()
objects=sorted((o for o in bpy.data.objects if o.name.startswith('Fixture_')),key=lambda o:o.name)
assert len(objects)==2
for index in range(2):
    material=bpy.data.materials.get(f'FixtureMaterial_{index}')
    assert material is not None and material.use_fake_user, 'original material not retained'
assert json.loads(json.dumps(corner_snapshot(objects,'AtlasUV'))) == json.loads((out/'before_corners.json').read_text())
assert validate(objects,'AtlasUV',128,8)['ok']
for obj in objects:
    mat=obj.material_slots[0].material
    assert any(n.type=='NORMAL_MAP' and n.uv_map=='AtlasUV' for n in mat.node_tree.nodes)
    for n in mat.node_tree.nodes:
        if n.type=='TEX_IMAGE':
            assert Path(bpy.path.abspath(n.image.filepath)).is_file()
assert not any(o.get('pipeline_source_object') for o in bpy.data.objects)
(out/'REOPEN_PASS.json').write_text(json.dumps({'saved_corner_correspondence':True,
    'global_layout':True,'texture_files_exist':True,'no_duplicate_baked_objects':True},indent=2))
print('ATLAS_REOPEN_PASS')
