"""Reopen source/UV/bake fixture independently; no source save or live use."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / 'scripts'))
from pipeline import primitive_recipe as tool
from pipeline.atlas_layout import corner_snapshot
from pipeline.common import sha256_file

parser = argparse.ArgumentParser()
for arg in ('recipe', 'uv', 'baked', 'textures', 'out'):
    parser.add_argument('--' + arg, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
out = Path(args.out)
assert bpy.app.background and not out.exists()
recipe = tool.load(args.recipe)
inputs = {str(Path(p).resolve()): sha256_file(p) for p in (args.uv, args.baked)}
bpy.ops.wm.open_mainfile(filepath=str(Path(args.uv).resolve()))
before_sources = tool._source_state(recipe)
before_corners = corner_snapshot([bpy.data.objects[n] for n in tool.part_names(recipe, True)], 'AtlasUV')
bpy.ops.wm.open_mainfile(filepath=str(Path(args.baked).resolve()))
after_sources = tool._source_state(recipe)
after_corners = corner_snapshot([bpy.data.objects[n] for n in tool.part_names(recipe, True)], 'AtlasUV')
assert before_sources == after_sources, 'master source changed across bake'
assert before_corners == after_corners, 'indexed geometry/corner UV changed across bake'
checked = tool.check(recipe, 'baked')
assert checked['status'] == 'pass', checked['failures']
images = {}
for channel in ('basecolor', 'roughness', 'metallic', 'normal', 'orm'):
    path = Path(args.textures) / ('atlas_' + channel + '.png')
    image = bpy.data.images.load(str(path.resolve()), check_existing=False)
    image.colorspace_settings.name = 'sRGB' if channel == 'basecolor' else 'Non-Color'
    values = np.asarray(image.pixels[:], dtype=np.float32).reshape(-1, 4)
    assert tuple(image.size) == (256, 256) and np.isfinite(values).all()
    images[channel] = dict(sha256=sha256_file(path), resolution=list(image.size),
                           min_rgb=values[:, :3].min(axis=0).tolist(),
                           max_rgb=values[:, :3].max(axis=0).tolist())
# Confirm actual assigned baked graphs read the intended, correctly tagged maps.
for n in tool.part_names(recipe, True):
    for material in bpy.data.objects[n].data.materials:
        textures = [node.image for node in material.node_tree.nodes if node.type == 'TEX_IMAGE']
        got = {Path(image.filepath).name: image.colorspace_settings.name for image in textures}
        assert got == {'atlas_basecolor.png': 'sRGB', 'atlas_normal.png': 'Non-Color',
                       'atlas_orm.png': 'Non-Color'}, got
assert all(sha256_file(p) == h for p, h in inputs.items()), 'input checkpoint bytes changed'
report = dict(status='pass', inputs=inputs, exact_source_state=True,
              exact_indexed_geometry_and_uv_corners=True, baked_shader_images=True,
              decoded_maps=images, saved_during_verification=False,
              limits=['No quantitative shader-transfer, mip or UI responsiveness certification.'])
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('x') as stream:
    json.dump(report, stream, indent=2, allow_nan=False)
