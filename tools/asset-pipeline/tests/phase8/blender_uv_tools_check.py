"""Blender-side regression tests for round69 UV tooling. Disposable, no save.

    blender -b --factory-startup --python-exit-code 1 \
      --python tools/asset-pipeline/tests/phase8/blender_uv_tools_check.py

Builds a two-island mesh, then checks:
  * measured island gap is reported (not assumed);
  * ensure_island_gaps widens the gap and reports it;
  * pack_islands_checked raises when the packer adds overlaps (fake packer,
    so the test does not depend on Blender's own bug);
  * overlap report counts identical islands, separates objects, and reports truncation;
  * a packer that leaves Edit Mode or an empty mesh fails predictably.
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pipeline import uv  # noqa: E402

errors = []


def check(name, condition, detail=None):
    print(("PASS " if condition else "FAIL ") + name + ("" if detail is None else " %r" % (detail,)))
    if not condition:
        errors.append(name)


def make_two_island_object(name, offset=0.0):
    mesh = bpy.data.meshes.new(name + "_mesh")
    # Two separate quads, each its own UV island.
    verts = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
             (2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)]
    faces = [(0, 1, 2, 3), (4, 5, 6, 7)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    layer = mesh.uv_layers.new(name="AtlasUV")
    coords = [(0.1 + offset, 0.1), (0.4 + offset, 0.1), (0.4 + offset, 0.4), (0.1 + offset, 0.4),
              (0.60 + offset, 0.1), (0.90 + offset, 0.1), (0.90 + offset, 0.4), (0.60 + offset, 0.4)]
    for loop, coordinate in zip(mesh.loops, coords):
        layer.data[loop.index].uv = coordinate
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


obj = make_two_island_object("UVTest_A")
bpy.context.view_layer.update()

gap = uv.min_island_gap([obj], "AtlasUV", step_uv=0.005)
check("gap_reported", gap["min_gap_uv"] is not None, gap)
check("gap_is_positive", (gap["min_gap_uv"] or 0) > 0.0, gap["min_gap_uv"])
before = gap["min_gap_uv"]

gaps = uv.ensure_island_gaps(obj, "AtlasUV", margin=0.02)
check("ensure_gaps_measures", gaps["measured_gap_uv"] is not None, gaps["measured_gap_uv"])
check("ensure_gaps_widens", (gaps["measured_gap_uv"] or 0) >= before - 1e-9,
      [before, gaps["measured_gap_uv"]])
check("ensure_gaps_factor_bounded", 0.5 <= gaps["min_factor"] <= 1.0, gaps["min_factor"])

# A fake packer that collapses both islands onto the same box: the guard must fail.
def collapsing_pack():
    layer = obj.data.uv_layers["AtlasUV"]
    for loop in obj.data.loops:
        u, v = layer.data[loop.index].uv
        layer.data[loop.index].uv = (u - 0.3 if u > 0.5 else u, v)
    bpy.context.view_layer.update()
    return {"FINISHED"}


try:
    uv.pack_islands_checked(obj, "AtlasUV", margin=0.02, pack=collapsing_pack)
    check("pack_guard_raises", False, "no exception")
except Exception as exc:  # noqa: BLE001 - the guard is the point
    check("pack_guard_raises", "introduced island overlaps" in str(exc), str(exc)[:120])

# Overlap report on identical islands (both quads moved onto the same UV square).
clone = make_two_island_object("UVTest_B")
for loop in clone.data.loops:
    uv_data = clone.data.uv_layers["AtlasUV"].data[loop.index]
    uv_data.uv = (uv_data.uv.x - 0.5 if uv_data.uv.x > 0.5 else uv_data.uv.x, uv_data.uv.y)
bpy.context.view_layer.update()
overlap = uv.island_overlap_report([clone], "AtlasUV", resolution=1024)
check("overlap_detected", overlap["total_pairs"] > 0, overlap["total_pairs"])
check("overlap_has_area", overlap["total_px2"] > 0, overlap["total_px2"])
check("overlap_truncation_reported", "truncated" in overlap and overlap["truncated"] is False,
      overlap.get("truncated"))

# Cross-object separation: two different objects must not be compared with each other.
far = make_two_island_object("UVTest_Far")
for loop in far.data.loops:
    uv_data = far.data.uv_layers["AtlasUV"].data[loop.index]
    uv_data.uv = (uv_data.uv.x, uv_data.uv.y + 0.5)
bpy.context.view_layer.update()
mixed = uv.island_overlap_report([clone, far], "AtlasUV", resolution=1024)
check("overlap_kept_per_object", len(mixed["objects"]) == 2, [o["object"] for o in mixed["objects"]])

# Truncation must be visible when the cap is hit.
capped = uv.island_overlap_report([clone], "AtlasUV", resolution=1024, max_pairs=1)
check("overlap_truncation_true", capped["truncated"] is True, capped["truncated"])

# A packer that leaves Edit Mode must fail as PipelineError and restore Object mode.
def edit_mode_pack():
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    return {"FINISHED"}


try:
    uv.pack_islands_checked(obj, "AtlasUV", margin=0.02, pack=edit_mode_pack)
    check("pack_packer_mode_raises", False, "no exception")
except Exception as exc:  # noqa: BLE001
    check("pack_packer_mode_raises", type(exc).__name__ == "PipelineError", type(exc).__name__)
check("pack_packer_mode_restored", obj.mode == "OBJECT", obj.mode)

# Default packer must succeed from Object mode and leave Object mode.
clean = make_two_island_object("UVTest_Clean")
bpy.context.view_layer.update()
try:
    default_report = uv.pack_islands_checked(clean, "AtlasUV", margin=0.02)
    check("default_pack_succeeds", "box_overlaps_before" in default_report, default_report)
except Exception as exc:  # noqa: BLE001
    check("default_pack_succeeds", False, "%s: %s" % (type(exc).__name__, exc))
check("default_pack_object_mode", clean.mode == "OBJECT", clean.mode)

# Starting in Edit mode must not crash before the guard runs.
edit_start = make_two_island_object("UVTest_EditStart")
bpy.context.view_layer.objects.active = edit_start
edit_start.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
try:
    uv.pack_islands_checked(edit_start, "AtlasUV", margin=0.02)
    check("edit_start_handled", True)
except Exception as exc:  # noqa: BLE001
    check("edit_start_handled", False, "%s: %s" % (type(exc).__name__, exc))
check("edit_start_object_mode", edit_start.mode == "OBJECT", edit_start.mode)

# Injected errors must surface as PipelineError, and active must be restored.
def raising_pack(kind):
    def inner():
        raise kind("probe")
    return inner


for kind in (RuntimeError, IndexError, ValueError):
    probe = make_two_island_object("UVTest_" + kind.__name__)
    bpy.context.view_layer.objects.active = probe
    probe.select_set(True)
    try:
        uv.pack_islands_checked(probe, "AtlasUV", margin=0.02, pack=raising_pack(kind))
        check("pack_%s_becomes_pipeline_error" % kind.__name__, False, "no exception")
    except Exception as exc:  # noqa: BLE001
        check("pack_%s_becomes_pipeline_error" % kind.__name__,
              type(exc).__name__ == "PipelineError", type(exc).__name__)
    check("pack_%s_mode_object" % kind.__name__, probe.mode == "OBJECT", probe.mode)

# Packer that hands active away must not leave the target in Edit mode silently.
swapper = make_two_island_object("UVTest_Swapper")
other = make_two_island_object("UVTest_Other")
bpy.context.view_layer.objects.active = swapper
swapper.select_set(True)


def swap_pack():
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.context.view_layer.objects.active = other
    return {"FINISHED"}


try:
    uv.pack_islands_checked(swapper, "AtlasUV", margin=0.02, pack=swap_pack)
    check("active_swap_reported", False, "no exception")
except Exception as exc:  # noqa: BLE001
    check("active_swap_reported", type(exc).__name__ == "PipelineError", type(exc).__name__)
check("active_swap_mode_object", swapper.mode == "OBJECT", swapper.mode)

# Empty mesh: structured result, not ValueError.
empty_mesh = bpy.data.meshes.new("UVTest_Empty_mesh")
empty = bpy.data.objects.new("UVTest_Empty", empty_mesh)
bpy.context.scene.collection.objects.link(empty)
empty_mesh.uv_layers.new(name="AtlasUV")
bpy.context.view_layer.update()
empty_result = uv.ensure_island_gaps(empty, "AtlasUV", margin=0.02)
check("empty_mesh_structured", empty_result["islands"] == 0 and empty_result["min_factor"] is None,
      empty_result)
try:
    uv.ensure_island_gaps(obj, "MissingLayer", margin=0.02)
    check("missing_layer_raises", False, "no exception")
except Exception as exc:  # noqa: BLE001
    check("missing_layer_raises", type(exc).__name__ == "PipelineError", type(exc).__name__)

print("ROUND69_UV_TESTS", "PASS" if not errors else "FAIL", errors)
if errors:
    raise SystemExit(1)
