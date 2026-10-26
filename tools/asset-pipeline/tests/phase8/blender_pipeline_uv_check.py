"""Blender check for the wired `pipeline.py uv` verb. Disposable, writes only to temp.

    blender -b --factory-startup --python-exit-code 1 \
      --python tools/asset-pipeline/tests/phase8/blender_pipeline_uv_check.py

Verifies the verb applies measured gutters, reports overlaps/spacing, and fails
predictably when a job demands disjoint islands but the layout overlaps.
"""
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import bpy

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "tools" / "asset-pipeline"))
import importlib.util  # noqa: E402

# `import pipeline` resolves to the package directory, not the entry script.
spec = importlib.util.spec_from_file_location(
    "pipeline_entry", REPO / "tools" / "asset-pipeline" / "pipeline.py")
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)

errors = []


def check(name, condition, detail=None):
    print(("PASS " if condition else "FAIL ") + name + ("" if detail is None else " %r" % (detail,)))
    if not condition:
        errors.append(name)


def make_object(name):
    mesh = bpy.data.meshes.new(name + "_mesh")
    verts = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
             (2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3), (4, 5, 6, 7)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


obj = make_object("Wired")
bpy.context.view_layer.update()

tmp = Path(tempfile.mkdtemp(prefix="pipeline_uv_check_"))
job = {
    "objects": ["Wired"],
    "out_dir": str(tmp / "out"),
    "uv_layer": "AtlasUV",
    "unwrap": True,
    "unwrap_margin": 0.02,
    "gap_margin": 0.02,
    "overlap_resolution": 1024,
}
args = SimpleNamespace(report=str(tmp / "uv.json"))

code = pipeline.verb_uv(job, args)
payload = json.loads((tmp / "uv.json").read_text())
check("verb_exit_zero", code == 0, code)
check("report_has_overlaps", "overlaps" in payload and "total_pairs" in payload["overlaps"])
check("report_has_spacing", payload["spacing"]["min_gap_uv"] is not None,
      payload["spacing"]["min_gap_uv"])
check("gaps_applied", payload["gaps"] and payload["gaps"][0]["measured_gap_uv"] is not None,
      payload["gaps"])
check("truncation_visible", payload["overlaps"]["truncated"] is False,
      payload["overlaps"]["truncated"])
check("no_failures", payload["failures"] == [], payload["failures"])

# A job that requires disjoint islands must fail when overlaps exist.
# Force both quads onto the same UV square so the strict job must fail.
layer = obj.data.uv_layers["AtlasUV"]
square = [(0.10, 0.10), (0.40, 0.10), (0.40, 0.40), (0.10, 0.40)]
for polygon in obj.data.polygons:
    for position, loop_index in enumerate(polygon.loop_indices):
        layer.data[loop_index].uv = square[position]
bpy.context.view_layer.update()
strict_job = dict(job, unwrap=False, gaps=False, require_disjoint=True)
strict_args = SimpleNamespace(report=str(tmp / "uv_strict.json"))
strict_code = pipeline.verb_uv(strict_job, strict_args)
strict = json.loads((tmp / "uv_strict.json").read_text())
check("strict_job_fails", strict_code != 0, strict_code)
check("strict_job_reason", "overlaps_present" in strict["failures"], strict["failures"])
check("strict_job_counts", strict["overlaps"]["total_pairs"] > 0, strict["overlaps"]["total_pairs"])

print("PIPELINE_UV_WIRING", "PASS" if not errors else "FAIL", errors)
if errors:
    raise SystemExit(1)
