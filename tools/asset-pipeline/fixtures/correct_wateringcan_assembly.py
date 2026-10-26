"""Bounded correction 1 for the watering-can attachments.

Edits ONLY CF_Spout_Path and CF_Handle_Path Bezier points/radii, keeping both
parented to Model_Control with identity local matrices. Saves a new-name
checkpoint before any render. Reuses build_wateringcan_assembly helpers.

Modes:
    apply()  - edit, save assembly_corrected_01.blend, residual/preservation JSON
    shots()  - side alpha overlay, neutral side, 3/4 from both sides
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

FIXTURES = Path("/Users/hydraxon/Documents/GitHub/AssetWorkshop/tools/asset-pipeline/fixtures")
if str(FIXTURES) not in sys.path:
    sys.path.insert(0, str(FIXTURES))

import build_wateringcan_assembly as A  # noqa: E402

B = A.B
ASSET = A.ASSET
REVIEW = ASSET / "assembly_review_01.blend"
CORRECTED = ASSET / "assembly_corrected_01.blend"
RECORDS = ASSET / "assembly_corrected_01_records.json"
TEMP_CAM = "CF_Cam_Temp_ThreeQuarter_Spout"
TOL = A.TOL  # 0.01 mm in metres

SIDE_FULL = ASSET / "assembly_corrected_01_side_full.png"
SIDE_OVERLAY = ASSET / "assembly_corrected_01_side_alpha_overlay.png"
SIDE_NEUTRAL = ASSET / "assembly_corrected_01_side_neutral.png"
TQ_HANDLE = ASSET / "assembly_corrected_01_threequarter_handle.png"
TQ_HANDLE_N = ASSET / "assembly_corrected_01_threequarter_handle_neutral.png"
TQ_SPOUT = ASSET / "assembly_corrected_01_threequarter_spout.png"
TQ_SPOUT_N = ASSET / "assembly_corrected_01_threequarter_spout_neutral.png"

# (u, v, radius_mm) in the shared side reference frame; image-left is +Y.
# Spout: 11-point trumpet, root lowered ~10 mm, slight waist, widening neck,
# then a short flared head with a three-point rolled rim and +11 mm length.
SPOUT_NEW = [
    (150, 264, 26.0),   # 0 root inside body (lowered)
    (141, 243, 22.5),   # 1 shaft exit, narrower
    (125, 209, 19.5),   # 2 waist
    (105, 174, 20.0),
    (88, 145, 21.0),
    (79, 131, 22.5),    # 5 neck (wider than waist)
    (70, 123, 27.5),    # 6 head flare
    (61, 114, 31.0),    # 7 rim maximum
    (54, 107, 30.0),    # 8 rim shoulder
    (50, 104, 25.5),    # 9 rim roll-over
    (45, 100, 21.0),    # 10 end face (rounded rim, +11 mm axial)
]

# Handle: flatter top leg, outer reach u 365 -> 360, lower attachment centreline
# z ~86.3 mm (bbox bottom ~73.8 mm), steeper inner/lower leg, cap embedded deeper.
HANDLE_NEW = [
    (290, 88, 13.0),    # 0 top root (unchanged attachment)
    (300, 94, 12.5),
    (316, 99, 12.0),    # flat top leg
    (334, 107, 11.5),
    (349, 121, 11.0),
    (359, 142, 11.0),
    (360, 168, 11.0),   # outer reach, y = -154.0 mm
    (357, 194, 11.0),
    (348, 215, 11.5),
    (335, 228, 12.0),   # steeper inner leg
    (323, 234, 12.5),
    (309, 236.5, 12.5),  # 11 embedded lower cap; bbox bottom ~73.8 mm
]


def _r(value, nd=3):
    return None if value is None else round(float(value), nd)


def _diff(a, b):
    return max(abs(float(a[i][j]) - float(b[i][j])) for i in range(4) for j in range(4))


def _vis3(obj):
    v = A.visibility(obj)
    return {k: bool(v[k]) for k in ("hide_viewport", "hide_render", "hide_select")}


def _slots(obj):
    data = getattr(obj, "data", None)
    mats = getattr(data, "materials", None) if data is not None else None
    if mats is None:
        return []
    return [m.name if m else None for m in mats]


def _local_identity_max(obj):
    m = obj.matrix_local
    return max(abs(float(m[i][j]) - (1.0 if i == j else 0.0)) for i in range(4) for j in range(4))


def _set_points(obj, specs):
    """Replace this curve's Bezier path; object transform/parenting untouched."""
    data = obj.data
    while len(data.splines):
        data.splines.remove(data.splines[0])
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(specs) - 1)
    inv = bpy.data.objects[A.ROOT].matrix_world.inverted()
    for bp, (u, v, radius_mm) in zip(spline.bezier_points, specs):
        bp.co = inv @ A.world_mm(u, v)
        bp.radius = radius_mm / 1000.0
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    data.dimensions = "3D"
    data.resolution_u = 12
    data.bevel_depth = 1.0
    data.bevel_resolution = 4
    data.fill_mode = "FULL"
    data.use_fill_caps = True


def _snap(obj):
    return {
        "parent": obj.parent.name if obj.parent else None,
        "matrix_world": A.mat_list(obj.matrix_world),
        "matrix_local": A.mat_list(obj.matrix_local),
        "local_identity_max": _local_identity_max(obj),
        "visibility": _vis3(obj),
        "materials": _slots(obj),
        "points_local_m": [[float(c) for c in bp.co] for bp in obj.data.splines[0].bezier_points],
        "radii_mm": [1000.0 * float(bp.radius) for bp in obj.data.splines[0].bezier_points],
    }


def _path_world(obj):
    return [obj.matrix_world @ bp.co for bp in obj.data.splines[0].bezier_points]


def _head_len_mm(obj, neck_idx=5):
    pts = _path_world(obj)
    return (pts[-1] - pts[neck_idx]).length * 1000.0


def _median_profile(ev, step=0.002, n=150):
    """Max +Y silhouette of an evaluated part near the X=0 median plane."""
    p = ev["pts"]
    if len(p) == 0:
        return np.full(n, np.nan)
    sel = np.abs(p[:, 0]) < 0.003
    z = p[sel, 2]
    y = p[sel, 1]
    if len(z) < 2:
        return np.full(n, np.nan)
    idx = np.clip((z / step).astype(np.int64), 0, n - 1)
    prof = np.full(n, -np.inf)
    np.maximum.at(prof, idx, y)
    good = np.isfinite(prof)
    if good.sum() < 2:
        return np.full(n, np.nan)
    return np.interp(np.arange(n), np.nonzero(good)[0], prof[good])


def _lower_junction_z_mm(part_ev, body_ev, step_mm=2.0):
    """Lowest z where the part's median silhouette protrudes past the body's."""
    bp = _median_profile(body_ev)
    sp = _median_profile(part_ev)
    ok = np.isfinite(bp) & np.isfinite(sp)
    prot = ok & (sp > bp + 0.0005)
    if not prot.any():
        return None
    return float(np.argmax(prot)) * step_mm


def _min_to_body_mm(ev, tree):
    return 1000.0 * min(
        float(tree.find_nearest(Vector((float(p[0]), float(p[1]), float(p[2]))))[3])
        for p in ev["pts"])


def _metrics(ev, body_tree):
    out = {k: (float(v) if isinstance(v, float) else v)
           for k, v in ev.items() if k not in ("pts", "tri")}
    out["world_bbox_min_mm"] = [_r(1000.0 * v) for v in ev["bbox_min"]]
    out["world_bbox_max_mm"] = [_r(1000.0 * v) for v in ev["bbox_max"]]
    out["min_vertex_to_body_mm"] = _r(_min_to_body_mm(ev, body_tree))
    return out


def apply():
    live = Path(bpy.data.filepath) if bpy.data.filepath else None
    if live is None or live.resolve() != REVIEW.resolve():
        raise SystemExit("BLOCKED: live file is not assembly_review_01.blend: %s" % live)
    if bpy.data.is_dirty:
        raise SystemExit("BLOCKED: live scene is dirty; checkpoint is authoritative, not overwriting")
    if CORRECTED.exists():
        raise SystemExit("BLOCKED: corrected checkpoint already exists: " + str(CORRECTED))
    if RECORDS.exists():
        raise SystemExit("BLOCKED: correction records already exist: " + str(RECORDS))
    if bpy.data.objects.get(TEMP_CAM) is not None:
        raise SystemExit("BLOCKED: temporary camera object already present")

    ctrl = bpy.data.objects.get(A.ROOT)
    body = bpy.data.objects.get("CF_Body_A")
    ref = bpy.data.objects.get("CF_Ref_Plane")
    if ctrl is None or body is None or ref is None:
        raise SystemExit("BLOCKED: Model_Control, CF_Body_A or CF_Ref_Plane missing")
    missing = [n for n in A.TARGETS if bpy.data.objects.get(n) is None]
    if missing:
        raise SystemExit("BLOCKED: protected targets missing: " + ", ".join(missing))
    spout = bpy.data.objects.get("CF_Spout_Path")
    handle = bpy.data.objects.get("CF_Handle_Path")
    if spout is None or handle is None:
        raise SystemExit("BLOCKED: attachment paths missing")
    if sorted(o.name for o in ctrl.children) != sorted(A.TARGETS[:3] + [
            "CF_Cutter_A", "CF_Cutter_B", "CF_Cutter_C", "CF_Profile_A",
            "CF_Profile_B", "CF_Profile_C", "CF_Spout_Path", "CF_Handle_Path"]):
        raise SystemExit("BLOCKED: Model_Control child set changed")
    for name, obj in (("spout", spout), ("handle", handle)):
        if obj.parent != ctrl or obj.parent_type != "OBJECT":
            raise SystemExit("BLOCKED: %s is not parented to Model_Control" % name)
        if _local_identity_max(obj) > 1e-9:
            raise SystemExit("BLOCKED: %s local matrix is not identity" % name)
        if obj.type != "CURVE" or len(obj.data.splines) != 1 or obj.data.splines[0].type != "BEZIER":
            raise SystemExit("BLOCKED: %s is not a single editable Bezier curve" % name)
        if _slots(obj) != ["CF_Clay"]:
            raise SystemExit("BLOCKED: %s material set changed: %s" % (name, _slots(obj)))
    if _vis3(body)["hide_render"] or _vis3(body)["hide_viewport"]:
        raise SystemExit("BLOCKED: CF_Body_A is not visible")
    for key in "BC":
        if not bpy.data.objects["CF_Body_" + key].hide_render:
            raise SystemExit("BLOCKED: CF_Body_%s is not render-hidden" % key)
    if not _vis3(ref)["hide_render"] or _vis3(ref)["hide_viewport"] or not ref.hide_select:
        raise SystemExit("BLOCKED: reference plane presentation changed")
    if not all(all(v) for v in A.locks(ref).values()):
        raise SystemExit("BLOCKED: reference plane is not fully locked")

    dg = bpy.context.evaluated_depsgraph_get()
    before = {
        "live": {"filepath": str(live), "dirty": bool(bpy.data.is_dirty),
                 "sha256": A.sha256_file(REVIEW)},
        "root": {"matrix": A.mat_list(ctrl.matrix_world),
                 "children": sorted(o.name for o in ctrl.children)},
        "matrices": {n: A.mat_list(bpy.data.objects[n].matrix_world) for n in A.TARGETS},
        "mesh_hash": {n: A.mesh_source_hash(bpy.data.objects[n].data)
                      for n in A.TARGETS if bpy.data.objects[n].type == "MESH"},
        "materials": {n: _slots(bpy.data.objects[n]) for n in A.TARGETS},
        "vis": {n: _vis3(bpy.data.objects[n]) for n in ("CF_Body_A", "CF_Body_B", "CF_Body_C")},
        "ref": {"matrix": A.mat_list(ref.matrix_world), "vis": _vis3(ref),
                "locks": A.locks(ref), "materials": _slots(ref)},
        "objects": sorted(o.name for o in bpy.data.objects),
        "a_eval": A.eval_world(body, dg),
        "ref_eval": A.eval_world(ref, dg),
        "parts": {name: _snap(obj) for name, obj in
                  (("CF_Spout_Path", spout), ("CF_Handle_Path", handle))},
        "spout_eval": A.eval_world(spout, dg),
        "handle_eval": A.eval_world(handle, dg),
        "spout_head_mm": _head_len_mm(spout),
        "spout_root_z_mm": _path_world(spout)[0].z * 1000.0,
        "root_matrix_max": A.mat_list(ctrl.matrix_world),
    }
    body_tree_before = A.bvh_body(before["a_eval"])
    before["handle_bottom_mm"] = 1000.0 * before["handle_eval"]["bbox_min"][2]
    before["handle_outer_mm"] = -1000.0 * before["handle_eval"]["bbox_min"][1]
    before["handle_top_mm"] = 1000.0 * before["handle_eval"]["bbox_max"][2]
    before["spout_junction_mm"] = _lower_junction_z_mm(before["spout_eval"], before["a_eval"])
    before["spout_bbox_min_z_mm"] = 1000.0 * before["spout_eval"]["bbox_min"][2]
    before["rose_diameter_mm"] = 2000.0 * max(bp.radius for bp in spout.data.splines[0].bezier_points)

    _set_points(spout, SPOUT_NEW)
    _set_points(handle, HANDLE_NEW)
    for name, specs in (("CF_Spout_Path", SPOUT_NEW), ("CF_Handle_Path", HANDLE_NEW)):
        bpy.data.objects[name]["reference_px"] = json.dumps(specs)
        bpy.data.objects[name]["construction"] = (
            "editable Bezier path, round bevelled sweep, per-point radius; caps; "
            "no holes/bore/shell; correction_01")
    bpy.context.view_layer.update()

    bpy.ops.wm.save_as_mainfile(filepath=str(CORRECTED), check_existing=False, copy=False)
    checkpoint_sha = A.sha256_file(CORRECTED)

    dg = bpy.context.evaluated_depsgraph_get()
    a_after = A.eval_world(body, dg)
    ref_after = A.eval_world(ref, dg)
    spout_ev = A.eval_world(spout, dg)
    handle_ev = A.eval_world(handle, dg)
    body_tree = A.bvh_body(a_after)

    matrices_after = {n: A.mat_list(bpy.data.objects[n].matrix_world) for n in A.TARGETS}
    prot = {n: _diff(matrices_after[n], before["matrices"][n]) for n in A.TARGETS}
    mesh_hash_after = {n: A.mesh_source_hash(bpy.data.objects[n].data)
                       for n in A.TARGETS if bpy.data.objects[n].type == "MESH"}
    a_src_equal = all(mesh_hash_after[n] == before["mesh_hash"][n] for n in before["mesh_hash"])
    a_cong = A.kd_bidir(a_after["pts"], before["a_eval"]["pts"])
    ref_cong = A.kd_bidir(ref_after["pts"], before["ref_eval"]["pts"])

    after = {
        "handle_bottom_mm": 1000.0 * handle_ev["bbox_min"][2],
        "handle_outer_mm": -1000.0 * handle_ev["bbox_min"][1],
        "handle_top_mm": 1000.0 * handle_ev["bbox_max"][2],
        "spout_head_mm": _head_len_mm(spout),
        "spout_root_z_mm": _path_world(spout)[0].z * 1000.0,
        "spout_junction_mm": _lower_junction_z_mm(spout_ev, a_after),
        "spout_bbox_min_z_mm": 1000.0 * spout_ev["bbox_min"][2],
        "rose_diameter_mm": 2000.0 * max(bp.radius for bp in spout.data.splines[0].bezier_points),
    }

    residuals = {
        "handle_bbox_bottom_z_mm": {"before": _r(before["handle_bottom_mm"]),
                                    "after": _r(after["handle_bottom_mm"]),
                                    "delta": _r(after["handle_bottom_mm"] - before["handle_bottom_mm"])},
        "handle_outer_reach_mm": {"before": _r(before["handle_outer_mm"]),
                                  "after": _r(after["handle_outer_mm"]),
                                  "delta": _r(after["handle_outer_mm"] - before["handle_outer_mm"])},
        "rose_head_axial_length_mm": {"before": _r(before["spout_head_mm"]),
                                      "after": _r(after["spout_head_mm"]),
                                      "delta": _r(after["spout_head_mm"] - before["spout_head_mm"])},
        "shaft_root_control_z_mm": {"before": _r(before["spout_root_z_mm"]),
                                    "after": _r(after["spout_root_z_mm"]),
                                    "delta": _r(after["spout_root_z_mm"] - before["spout_root_z_mm"])},
        "spout_lower_junction_z_mm_estimate": {
            "before": _r(before["spout_junction_mm"]), "after": _r(after["spout_junction_mm"]),
            "delta": _r(None if (before["spout_junction_mm"] is None or after["spout_junction_mm"] is None)
                        else after["spout_junction_mm"] - before["spout_junction_mm"])},
        "supporting": {
            "handle_bbox_top_z_mm": {"before": _r(before["handle_top_mm"]),
                                     "after": _r(after["handle_top_mm"])},
            "spout_bbox_min_z_mm": {"before": _r(before["spout_bbox_min_z_mm"]),
                                    "after": _r(after["spout_bbox_min_z_mm"])},
            "rose_max_diameter_mm": {"before": _r(before["rose_diameter_mm"]),
                                     "after": _r(after["rose_diameter_mm"])},
        },
    }

    parts_after = {}
    for name, obj, ev in (("CF_Spout_Path", spout, spout_ev),
                          ("CF_Handle_Path", handle, handle_ev)):
        parts_after[name] = {
            "parent": obj.parent.name if obj.parent else None,
            "type": obj.type,
            "local_identity_max": _local_identity_max(obj),
            "materials": _slots(obj),
            "points_local_m": [[float(c) for c in bp.co] for bp in obj.data.splines[0].bezier_points],
            "radii_mm": [1000.0 * float(bp.radius) for bp in obj.data.splines[0].bezier_points],
            "reference_px": json.loads(obj["reference_px"]),
            "metrics": _metrics(ev, body_tree),
        }

    checks = {
        "live_file_is_review_checkpoint": True,
        "A_source_unchanged": a_src_equal,
        "A_evaluated_congruent_0p01mm": a_cong <= TOL and a_after["nt"] == before["a_eval"]["nt"],
        "protected_transforms_unchanged_0p01mm": max(prot.values()) <= TOL,
        "root_matrix_unchanged": _diff(ctrl.matrix_world, before["root"]["matrix"]) == 0.0,
        "root_children_unchanged": sorted(o.name for o in ctrl.children) == before["root"]["children"],
        "reference_matrix_unchanged_0p01mm": _diff(ref.matrix_world, before["ref"]["matrix"]) <= TOL,
        "reference_evaluated_congruent_0p01mm": ref_cong <= TOL,
        "reference_visibility_and_locks_unchanged": (
            _vis3(ref) == before["ref"]["vis"] and A.locks(ref) == before["ref"]["locks"]),
        "body_visibility_unchanged": all(_vis3(bpy.data.objects[n]) == before["vis"][n]
                                         for n in ("CF_Body_A", "CF_Body_B", "CF_Body_C")),
        "materials_unchanged": (
            {n: _slots(bpy.data.objects[n]) for n in A.TARGETS} == before["materials"]
            and _slots(ref) == before["ref"]["materials"]),
        "no_objects_added_or_removed": sorted(o.name for o in bpy.data.objects) == before["objects"],
        "spout_parented_identity": (spout.parent == ctrl and _local_identity_max(spout) <= 1e-9),
        "handle_parented_identity": (handle.parent == ctrl and _local_identity_max(handle) <= 1e-9),
        "parts_finite": all(parts_after[n]["metrics"]["finite"] for n in parts_after),
        "parts_no_zero_area": all(parts_after[n]["metrics"]["zero_area_tris"] == 0 for n in parts_after),
        "parts_no_loose": all(parts_after[n]["metrics"]["loose_verts"] == 0 for n in parts_after),
        "parts_contact_body": all(parts_after[n]["metrics"]["min_vertex_to_body_mm"] <= 0.5
                                  for n in parts_after),
    }

    result = {
        "stage": "assembly_corrected_01",
        "checkpoint": {"path": str(CORRECTED), "sha256": checkpoint_sha,
                       "live_filepath_after_save": bpy.data.filepath,
                       "dirty_after_save": bool(bpy.data.is_dirty)},
        "live_before": before["live"],
        "root": {"matrix": A.mat_list(ctrl.matrix_world),
                 "euler_deg": [float(np.degrees(v)) for v in ctrl.rotation_euler],
                 "children": sorted(o.name for o in ctrl.children),
                 "matrix_maxdiff_vs_before": _diff(ctrl.matrix_world, before["root"]["matrix"])},
        "preservation": {
            "A_source_hash_equal": a_src_equal,
            "A_eval_bidir_mm": _r(a_cong * 1000.0, 6),
            "A_eval_counts": {"before": [before["a_eval"]["nv"], before["a_eval"]["nt"]],
                              "after": [a_after["nv"], a_after["nt"]]},
            "protected_matrix_maxdiff_mm": {n: _r(prot[n] * 1000.0, 6) for n in A.TARGETS},
            "reference_matrix_maxdiff_mm": _r(_diff(ref.matrix_world, before["ref"]["matrix"]) * 1000.0, 6),
            "reference_eval_bidir_mm": _r(ref_cong * 1000.0, 6),
            "reference_object": "CF_Ref_Plane",
        },
        "residuals": residuals,
        "checks": {k: bool(v) for k, v in checks.items()},
        "checks_all_pass": all(checks.values()),
        "parts": parts_after,
        "body_A_eval": _metrics(a_after, A.bvh_body(a_after)),
        "reference": {"material": _slots(ref), "visibility": _vis3(ref),
                      "locks": A.locks(ref), "hide_select": bool(ref.hide_select)},
        "classification": {
            "hard": ["root transform and pose", "body/profile/cutter geometry and transforms",
                     "reference plane pose/presentation", "attachment parenting and identity local matrices"],
            "provisional": ["spout path points/radii", "handle path points/radii",
                            "inferred circular sections on X=0 median plane"],
        },
        "changed": ["CF_Spout_Path Bezier points/radii (7 -> 11)",
                    "CF_Handle_Path Bezier points/radii (12 -> 12)",
                    "those two objects' reference_px/construction metadata"],
        "limitations": [
            "one stylized elevated side reference; hidden depth inferred as circular sections",
            "evaluated triangle counts are not final topology",
            "no shell, thickness, bore, sprinkler holes, union, UVs or export",
        ],
    }
    RECORDS.write_text(json.dumps(result, indent=2, sort_keys=True))

    summary = {
        "checkpoint": str(CORRECTED), "sha256": checkpoint_sha,
        "records": str(RECORDS),
        "live": {"filepath": bpy.data.filepath, "dirty": bool(bpy.data.is_dirty)},
        "residuals": residuals,
        "checks": result["checks"], "checks_all_pass": result["checks_all_pass"],
        "preservation": result["preservation"],
        "tri_counts": {
            "CF_Body_A": {"nv": a_after["nv"], "nt": a_after["nt"]},
            "CF_Spout_Path": {k: parts_after["CF_Spout_Path"]["metrics"][k]
                              for k in ("nv", "nt", "zero_area_tris", "loose_verts", "finite")},
            "CF_Handle_Path": {k: parts_after["CF_Handle_Path"]["metrics"][k]
                               for k in ("nv", "nt", "zero_area_tris", "loose_verts", "finite")},
        },
    }
    print("CORRECTION_APPLY_OK " + json.dumps(summary, sort_keys=True))
    return summary


def _temp_camera():
    ref_cam = bpy.data.objects.get("CF_Cam_ThreeQuarter")
    if ref_cam is None:
        raise SystemExit("BLOCKED: CF_Cam_ThreeQuarter missing")
    cd = bpy.data.cameras.new(TEMP_CAM)
    cd.type = ref_cam.data.type
    cd.ortho_scale = ref_cam.data.ortho_scale
    cd.lens = ref_cam.data.lens
    cd.sensor_width = ref_cam.data.sensor_width
    cd.sensor_height = ref_cam.data.sensor_height
    cd.shift_x = ref_cam.data.shift_x
    cd.shift_y = ref_cam.data.shift_y
    cd.clip_start = ref_cam.data.clip_start
    cd.clip_end = ref_cam.data.clip_end
    cam = bpy.data.objects.new(TEMP_CAM, cd)
    bpy.context.scene.collection.objects.link(cam)
    mw = ref_cam.matrix_world
    direction = (mw.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    origin = mw.translation
    if abs(direction.x) > 1e-6:
        target = origin + direction * (-origin.x / direction.x)
    else:
        target = origin + direction * 5.0
    position = Vector((0.55, 0.55, 0.42))
    cam.location = position
    cam.rotation_euler = (target - position).to_track_quat("-Z", "Y").to_euler()
    return cam, cd


def shots():
    if not CORRECTED.exists():
        raise SystemExit("BLOCKED: corrected checkpoint missing; run apply() first")
    scene = bpy.context.scene
    saved_hide = {o.name: bool(o.hide_render) for o in bpy.data.objects}
    saved_scene = (scene.camera, scene.render.resolution_x, scene.render.resolution_y,
                   scene.render.resolution_percentage, scene.render.film_transparent,
                   scene.render.image_settings.file_format,
                   scene.render.image_settings.color_mode, scene.render.filepath)
    cam = cd = None
    try:
        cam, cd = _temp_camera()
        full = A.render_view(SIDE_FULL, "CF_Cam_Side", (402, 327), True, True, False, True)
        reference = B.load_rgba(A.REF)
        B.save_rgba(SIDE_OVERLAY, A.contour_overlay(reference, full[:, :, 3]))
        B.save_rgba(SIDE_NEUTRAL, B.neutral_composite(full))
        handle_rgba = A.render_view(TQ_HANDLE, "CF_Cam_ThreeQuarter", (512, 512),
                                    True, True, False, True)
        B.save_rgba(TQ_HANDLE_N, B.neutral_composite(handle_rgba))
        spout_rgba = A.render_view(TQ_SPOUT, TEMP_CAM, (512, 512),
                                   True, True, False, True)
        B.save_rgba(TQ_SPOUT_N, B.neutral_composite(spout_rgba))
    finally:
        if cam is not None:
            try:
                bpy.data.objects.remove(cam, do_unlink=True)
            except Exception:
                pass
        if cd is not None:
            try:
                bpy.data.cameras.remove(cd)
            except Exception:
                pass
        for o in bpy.data.objects:
            if o.name in saved_hide:
                o.hide_render = saved_hide[o.name]
        (scene.camera, scene.render.resolution_x, scene.render.resolution_y,
         scene.render.resolution_percentage, scene.render.film_transparent,
         scene.render.image_settings.file_format,
         scene.render.image_settings.color_mode, scene.render.filepath) = saved_scene
        bpy.context.view_layer.update()

    captures = {p.name: A.sha256_file(p) for p in
                (SIDE_FULL, SIDE_OVERLAY, SIDE_NEUTRAL,
                 TQ_HANDLE, TQ_HANDLE_N, TQ_SPOUT, TQ_SPOUT_N)}
    result = {"checkpoint": str(CORRECTED), "sha256": A.sha256_file(CORRECTED),
              "captures": captures,
              "live": {"filepath": bpy.data.filepath, "dirty": bool(bpy.data.is_dirty)},
              "temp_camera_removed": bpy.data.objects.get(TEMP_CAM) is None}
    print("CORRECTION_SHOTS_OK " + json.dumps(result, sort_keys=True))
    return result
