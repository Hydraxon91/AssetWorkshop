"""Bounded attachment correction v2, staged headless.

stage1: assert the loaded review checkpoint, capture pre-edit fingerprints,
        rewrite CF_Spout_Path (axis + new editable taper profile CF_Spout_Taper),
        save assembly_corrected_01_pre_handle.blend, then rewrite the handle and
        save assembly_corrected_01.blend. No renders.
stage2: open the saved corrected checkpoint, recompute preservation against the
        stage1 baseline, report residuals and render side/overlay/3-quarter views.

Only CF_Spout_Path, CF_Handle_Path and the new CF_Spout_Taper change. Body,
profiles, cutters, root, reference, materials and visibility are preserved.
Reuses build_wateringcan_assembly helpers; no new framework.
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

FIXTURES = Path(__file__).resolve().parent
if str(FIXTURES) not in sys.path:
    sys.path.insert(0, str(FIXTURES))

import build_wateringcan_assembly as A  # noqa: E402
from reference_compare import contour_overlay  # noqa: E402

B = A.B
ASSET = A.ASSET
REVIEW = ASSET / "assembly_review_01.blend"
PRE_HANDLE = ASSET / "assembly_corrected_01_pre_handle.blend"
CORRECTED = ASSET / "assembly_corrected_01.blend"
BASELINE = ASSET / "assembly_corrected_01_stage1_baseline.json"
PROOF = ASSET / "assembly_corrected_01_proof.json"

SIDE_FULL = ASSET / "assembly_corrected_01_side_full.png"
SIDE_OVERLAY = ASSET / "assembly_corrected_01_side_alpha_overlay.png"
SIDE_NEUTRAL = ASSET / "assembly_corrected_01_side_neutral.png"
TQ_HANDLE = ASSET / "assembly_corrected_01_threequarter_handle.png"
TQ_HANDLE_N = ASSET / "assembly_corrected_01_threequarter_handle_neutral.png"
TQ_SPOUT = ASSET / "assembly_corrected_01_threequarter_spout.png"
TQ_SPOUT_N = ASSET / "assembly_corrected_01_threequarter_spout_neutral.png"

TAPER = "CF_Spout_Taper"
TEMP_CAM = "CF_Cam_Temp_ThreeQuarter_Spout"
COLL = "CF_Assembly_01"
TOL = A.TOL  # 0.01 mm in metres
SPOUT = "CF_Spout_Path"
HANDLE = "CF_Handle_Path"

# (u, v) reference px, root -> tip.
SPOUT_AXIS_PX = [
    (150.0, 262.0), (141.0, 247.0), (130.0, 228.0), (118.0, 206.0),
    (106.0, 184.0), (94.0, 162.0), (84.0, 143.0), (76.0, 128.0),
    (70.0, 119.0), (65.0, 112.0), (61.0, 106.5), (58.0, 102.0),
    (56.0, 99.0), (53.5, 96.0), (51.0, 93.5), (48.0, 92.0),
]
# Aligned radii mm, root -> tip (47.6 rim rolling to a 39.0 face disc).
SPOUT_RADII_MM = [
    26.0, 22.5, 19.0, 16.8, 15.6, 15.2, 15.2, 15.6,
    17.5, 20.0, 22.3, 23.6, 23.8, 23.2, 21.0, 19.5,
]
# (u, v, radius_mm) reference px, top -> tail.
HANDLE_PX_R = [
    (292.0, 90.0, 13.0), (301.0, 95.0, 12.2), (313.0, 101.0, 11.6),
    (327.0, 109.0, 11.2), (341.0, 121.0, 11.0), (351.0, 137.0, 10.8),
    (357.0, 156.0, 10.8), (358.0, 176.0, 10.8), (355.0, 196.0, 11.0),
    (348.0, 213.0, 11.2), (338.0, 226.0, 11.6), (326.0, 233.0, 12.0),
    (315.0, 236.0, 12.5), (305.0, 238.0, 13.0),
]
TARGETS_MM = {
    "rose_max_diameter_mm": 47.6,
    "rose_face_disc_mm": 39.0,
    "handle_bbox_bottom_z_mm": 71.7,
    "handle_outer_minus_y_mm": 161.0,
    "handle_bbox_top_z_mm": 260.0,
    "spout_face_centre_z_mm": 245.0,
}


def _req(cond, msg):
    if not cond:
        raise RuntimeError(msg)


def _ensure_open(path):
    """Open the stage source file in this fresh headless process.

    The permitted command launches Blender with --python before any file
    argument, so the stage source is opened here; no live scene is reloaded.
    """
    current = Path(bpy.data.filepath) if bpy.data.filepath else None
    if current is not None and current.resolve() == path.resolve():
        return
    _req(current is None or not bpy.data.is_dirty,
         "refusing to open over a dirty scene: %s" % current)
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.view_layer.update()


def _r(value, nd=4):
    return None if value is None else round(float(value), nd)


def _vis(obj):
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
    return max(abs(float(m[i][j]) - (1.0 if i == j else 0.0))
               for i in range(4) for j in range(4))


def _diff(a, b):
    return max(abs(float(a[i][j]) - float(b[i][j])) for i in range(4) for j in range(4))


def _flat_diff(matrix, flat):
    return max(abs(float(matrix[i][j]) - float(flat[i * 4 + j]))
               for i in range(4) for j in range(4))


def _set_bezier(data, points, radii_m=None, radius_uniform=None):
    while len(data.splines):
        data.splines.remove(data.splines[0])
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for i, bp in enumerate(spline.bezier_points):
        bp.co = Vector(points[i])
        bp.radius = radius_uniform if radius_uniform is not None else radii_m[i]
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    data.dimensions = "3D"
    data.resolution_u = 12
    data.bevel_depth = 1.0
    data.bevel_resolution = 4
    data.fill_mode = "FULL"
    data.use_fill_caps = True


def _chord_fractions(points):
    cum = [0.0]
    for a, b in zip(points, points[1:]):
        cum.append(cum[-1] + (b - a).length)
    total = cum[-1]
    _req(total > 0.0, "zero-length spout axis")
    return [c / total for c in cum]


def _axis_world(obj):
    return [obj.matrix_world @ bp.co for bp in obj.data.splines[0].bezier_points]


def _axis_projection(p, axis_world):
    """Radial distance and normalised chord fraction to the axis polyline."""
    best_d = None
    best_t = 0.0
    lengths = [(b - a).length for a, b in zip(axis_world, axis_world[1:])]
    total = sum(lengths)
    _req(total > 0.0, "zero-length axis for projection")
    cum = 0.0
    p = Vector((float(p[0]), float(p[1]), float(p[2])))
    for a, b, length in zip(axis_world, axis_world[1:], lengths):
        if length <= 0.0:
            continue
        ab = b - a
        f = max(0.0, min(1.0, (p - a).dot(ab) / (length * length)))
        d = (p - (a + ab * f)).length
        t = (cum + f * length) / total
        if best_d is None or d < best_d:
            best_d, best_t = d, t
        cum += length
    return float(best_d), float(best_t)


def _spout_radial_metrics(ev, axis_world, t_split=0.80):
    pts = ev["pts"]
    if len(pts) == 0:
        return {"rose_max_diameter_mm": None, "rose_face_disc_mm": None,
                "rose_vertices": 0, "face_vertices": 0}
    vals = [_axis_projection(p, axis_world) for p in pts]
    rose = [d for d, t in vals if t >= t_split]
    face = [d for d, t in vals if t >= 0.9995]
    if len(face) < 3:
        face = [d for d, t in vals if t >= 0.995]
    return {
        "rose_max_diameter_mm": _r(2000.0 * max(rose)) if rose else None,
        "rose_face_disc_mm": _r(2000.0 * max(face)) if face else None,
        "rose_vertices": len(rose),
        "face_vertices": len(face),
    }


def _min_to_body_mm(ev, tree):
    pts = ev["pts"]
    if len(pts) == 0:
        return None
    return _r(1000.0 * min(
        float(tree.find_nearest(Vector((float(p[0]), float(p[1]), float(p[2]))))[3])
        for p in pts), 6)


def _part_metrics(ev, body_tree):
    return {
        "nv": int(ev["nv"]), "nt": int(ev["nt"]),
        "area_m2": _r(ev["area_m2"], 9),
        "zero_area_tris": int(ev["zero_area_tris"]),
        "loose_verts": int(ev["loose_verts"]),
        "finite": bool(ev["finite"]),
        "bbox_min_mm": [_r(1000.0 * v) for v in ev["bbox_min"]] if ev["bbox_min"] else None,
        "bbox_max_mm": [_r(1000.0 * v) for v in ev["bbox_max"]] if ev["bbox_max"] else None,
        "min_vertex_to_body_mm": _min_to_body_mm(ev, body_tree),
    }


def _handle_metrics(ev, body_tree):
    m = _part_metrics(ev, body_tree)
    m.update({
        "bbox_bottom_z_mm": _r(1000.0 * ev["bbox_min"][2], 6),
        "bbox_outer_minus_y_mm": _r(-1000.0 * ev["bbox_min"][1], 6),
        "bbox_top_z_mm": _r(1000.0 * ev["bbox_max"][2], 6),
    })
    return m


def _local_axis_points(inv):
    return [inv @ A.world_mm(u, v) for u, v in SPOUT_AXIS_PX]


def _handle_local_points(inv):
    return [inv @ A.world_mm(u, v) for u, v, _r_mm in HANDLE_PX_R]


def _taper_local_points(axis_local, radii_mm):
    ts = _chord_fractions(axis_local)
    return ts, [Vector((t, radius_mm / 1000.0, 0.0))
                for t, radius_mm in zip(ts, radii_mm)]


def _make_taper(ctrl, taper_points):
    coll = bpy.data.collections.get(COLL)
    _req(coll is not None, "collection %s missing" % COLL)
    data = bpy.data.curves.new(TAPER, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 12
    data.bevel_depth = 0.0
    data.fill_mode = "FULL"
    data.use_fill_caps = False
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(taper_points) - 1)
    for bp, co in zip(spline.bezier_points, taper_points):
        bp.co = co
        bp.radius = 1.0
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(TAPER, data)
    coll.objects.link(obj)
    obj.parent = ctrl
    obj.parent_type = "OBJECT"
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_world = ctrl.matrix_world
    obj.hide_render = True
    obj.hide_viewport = False
    obj["role"] = "spout_taper_profile"
    obj["construction"] = ("editable taper profile: X = normalised chord fraction, "
                           "Y = radius (m), AUTO handles; no material")
    return obj


def _before_snapshot(ctrl, body, ref, spout, handle, spout_local, taper_points):
    dg = bpy.context.evaluated_depsgraph_get()
    a_ev = A.eval_world(body, dg)
    spout_ev = A.eval_world(spout, dg)
    handle_ev = A.eval_world(handle, dg)
    tree = A.bvh_body(a_ev)
    spout_axis = _axis_world(spout)
    handle_axis = _axis_world(handle)
    snap = {
        "stage": "assembly_corrected_01_stage1_baseline",
        "review": {"path": str(REVIEW), "sha256": A.sha256_file(REVIEW),
                   "filepath": str(bpy.data.filepath), "dirty": bool(bpy.data.is_dirty)},
        "root": {"matrix": A.mat_list(ctrl.matrix_world),
                 "children": sorted(o.name for o in ctrl.children)},
        "targets": {n: {"matrix": A.mat_list(bpy.data.objects[n].matrix_world),
                        "source_hash": A.mesh_source_hash(bpy.data.objects[n].data)
                        if bpy.data.objects[n].type == "MESH" else None,
                        "materials": _slots(bpy.data.objects[n]),
                        "visibility": _vis(bpy.data.objects[n])}
                    for n in A.TARGETS},
        "reference": {"matrix": A.mat_list(ref.matrix_world), "vis": _vis(ref),
                      "locks": A.locks(ref), "materials": _slots(ref)},
        "materials": sorted(m.name for m in bpy.data.materials),
        "objects": sorted(o.name for o in bpy.data.objects),
        "body_A": {"source_hash": A.mesh_source_hash(body.data),
                   "eval": {k: v for k, v in a_ev.items() if k not in ("pts", "tri")},
                   "eval_bbox_mm": [[_r(1000.0 * v) for v in a_ev["bbox_min"]],
                                    [_r(1000.0 * v) for v in a_ev["bbox_max"]]],
                   "eval_points": [[round(float(x), 9) for x in p] for p in a_ev["pts"]]},
        "parts_before": {
            SPOUT: {"points_local_m": [[float(c) for c in bp.co]
                                       for bp in spout.data.splines[0].bezier_points],
                    "radii_mm": [1000.0 * float(bp.radius)
                                 for bp in spout.data.splines[0].bezier_points],
                    "metrics": _part_metrics(spout_ev, tree),
                    "radial": _spout_radial_metrics(spout_ev, spout_axis),
                    "face_centre_z_mm": _r(1000.0 * spout_axis[-1].z, 6),
                    "root_z_mm": _r(1000.0 * spout_axis[0].z, 6)},
            HANDLE: {"points_local_m": [[float(c) for c in bp.co]
                                        for bp in handle.data.splines[0].bezier_points],
                     "radii_mm": [1000.0 * float(bp.radius)
                                  for bp in handle.data.splines[0].bezier_points],
                     "metrics": _handle_metrics(handle_ev, tree),
                     "bbox_bottom_z_mm": _r(1000.0 * handle_ev["bbox_min"][2], 6),
                     "bbox_outer_minus_y_mm": _r(-1000.0 * handle_ev["bbox_min"][1], 6),
                     "bbox_top_z_mm": _r(1000.0 * handle_ev["bbox_max"][2], 6)},
        },
        "planned": {"spout_axis_px": SPOUT_AXIS_PX, "spout_radii_mm": SPOUT_RADII_MM,
                    "handle_px_r": HANDLE_PX_R,
                    "taper_points_local_m": [[float(c) for c in p] for p in taper_points],
                    "spout_points_local_m": [[float(c) for c in p] for p in spout_local]},
    }
    return snap


def _spout_temp_camera():
    ref_cam = bpy.data.objects.get("CF_Cam_ThreeQuarter")
    _req(ref_cam is not None, "CF_Cam_ThreeQuarter missing")
    cd = bpy.data.cameras.new(TEMP_CAM)
    cd.type = ref_cam.data.type
    cd.lens = ref_cam.data.lens
    cd.sensor_width = ref_cam.data.sensor_width
    cd.sensor_height = ref_cam.data.sensor_height
    cd.sensor_fit = ref_cam.data.sensor_fit
    cd.shift_x = ref_cam.data.shift_x
    cd.shift_y = ref_cam.data.shift_y
    cd.clip_start = ref_cam.data.clip_start
    cd.clip_end = ref_cam.data.clip_end
    if cd.type == "ORTHO":
        cd.ortho_scale = ref_cam.data.ortho_scale
    cam = bpy.data.objects.new(TEMP_CAM, cd)
    bpy.context.scene.collection.objects.link(cam)
    mw = ref_cam.matrix_world
    direction = (mw.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    origin = mw.translation.copy()
    if abs(direction.x) > 1e-6:
        target = origin + direction * (-origin.x / direction.x)
    else:
        target = origin + direction * 5.0
    position = Vector((-origin.x, -origin.y, origin.z))
    cam.location = position
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (target - position).to_track_quat("-Z", "Y")
    return cam, cd


def stage1():
    _ensure_open(REVIEW)
    live = Path(bpy.data.filepath) if bpy.data.filepath else None
    _req(live is not None and live.resolve() == REVIEW.resolve(),
         "live file is not assembly_review_01.blend: %s" % live)
    _req(not bpy.data.is_dirty, "live scene is dirty; checkpoint is not authoritative")
    _req(not PRE_HANDLE.exists(), "pre-handle checkpoint already exists: %s" % PRE_HANDLE)
    _req(not CORRECTED.exists(), "corrected checkpoint already exists: %s" % CORRECTED)
    _req(not BASELINE.exists(), "stage1 baseline already exists: %s" % BASELINE)
    _req(not PROOF.exists(), "proof already exists: %s" % PROOF)
    _req(bpy.data.objects.get(TAPER) is None, "taper object already exists")

    ctrl = bpy.data.objects.get(A.ROOT)
    body = bpy.data.objects.get("CF_Body_A")
    ref = bpy.data.objects.get("CF_Ref_Plane")
    _req(ctrl is not None and body is not None and ref is not None,
         "Model_Control, CF_Body_A or CF_Ref_Plane missing")
    missing = [n for n in A.TARGETS if bpy.data.objects.get(n) is None]
    _req(not missing, "protected targets missing: " + ", ".join(missing))
    spout = bpy.data.objects.get(SPOUT)
    handle = bpy.data.objects.get(HANDLE)
    _req(spout is not None and handle is not None, "attachment paths missing")
    expected = sorted(A.TARGETS + [SPOUT, HANDLE])
    _req(sorted(o.name for o in ctrl.children) == expected,
         "Model_Control child set changed")
    for name, obj in ((SPOUT, spout), (HANDLE, handle)):
        _req(obj.parent == ctrl and obj.parent_type == "OBJECT",
             "%s is not parented to Model_Control" % name)
        _req(_local_identity_max(obj) <= 1e-9, "%s local matrix is not identity" % name)
        _req(obj.type == "CURVE" and len(obj.data.splines) == 1
             and obj.data.splines[0].type == "BEZIER",
             "%s is not a single editable Bezier curve" % name)
        _req(_slots(obj) == ["CF_Clay"], "%s material set changed: %s" % (name, _slots(obj)))
    _req(spout.data.taper_object is None, "spout already has a taper object")
    _req(bpy.data.collections.get(COLL) is not None, "assembly collection missing")

    inv = ctrl.matrix_world.inverted()
    spout_local = _local_axis_points(inv)
    ts, taper_points = _taper_local_points(spout_local, SPOUT_RADII_MM)
    handle_local = _handle_local_points(inv)

    baseline = _before_snapshot(ctrl, body, ref, spout, handle, spout_local, taper_points)
    baseline["chord_fractions"] = [_r(t, 9) for t in ts]
    baseline["plan"] = {
        "spout_points": len(SPOUT_AXIS_PX),
        "taper_points": len(taper_points),
        "handle_points": len(HANDLE_PX_R),
        "pre_handle": str(PRE_HANDLE),
        "final": str(CORRECTED),
    }
    BASELINE.write_text(json.dumps(baseline, indent=2, sort_keys=True), encoding="utf-8")

    taper = _make_taper(ctrl, taper_points)
    spout.data.taper_object = taper
    _set_bezier(spout.data, spout_local, radius_uniform=1.0)
    spout.data.use_fill_caps = True
    spout["reference_px"] = json.dumps(SPOUT_AXIS_PX)
    spout["construction"] = ("editable Bezier axis (radius 1.0, bevel_depth 1.0) with separate "
                             "editable taper profile CF_Spout_Taper; round sweep, caps; "
                             "no holes/bore/shell; correction_v2")
    bpy.context.view_layer.update()

    bpy.ops.wm.save_as_mainfile(filepath=str(PRE_HANDLE), check_existing=False, copy=False)
    pre_sha = A.sha256_file(PRE_HANDLE)
    _req(PRE_HANDLE.exists() and PRE_HANDLE.stat().st_size > 0, "pre-handle save failed")

    _set_bezier(handle.data, handle_local,
                radii_m=[r_mm / 1000.0 for _u, _v, r_mm in HANDLE_PX_R])
    handle.data.taper_object = None
    handle["reference_px"] = json.dumps(HANDLE_PX_R)
    handle["construction"] = ("editable Bezier path, round bevelled sweep, per-point radius; "
                              "caps; no holes/bore/shell; correction_v2")
    bpy.context.view_layer.update()

    bpy.ops.wm.save_as_mainfile(filepath=str(CORRECTED), check_existing=False, copy=False)
    corrected_sha = A.sha256_file(CORRECTED)
    _req(CORRECTED.exists() and CORRECTED.stat().st_size > 0, "final save failed")

    dg = bpy.context.evaluated_depsgraph_get()
    a_ev = A.eval_world(body, dg)
    spout_ev = A.eval_world(spout, dg)
    handle_ev = A.eval_world(handle, dg)
    tree = A.bvh_body(a_ev)
    spout_axis = _axis_world(spout)
    radial = _spout_radial_metrics(spout_ev, spout_axis)

    checks = {
        "taper_parented_identity": (taper.parent == ctrl
                                    and _local_identity_max(taper) <= 1e-6),
        "taper_in_assembly_collection": any(o == taper for o in
                                            bpy.data.collections[COLL].objects),
        "taper_no_material": len(taper.data.materials) == 0,
        "taper_render_hidden": bool(taper.hide_render),
        "spout_taper_object_set": spout.data.taper_object == taper,
        "spout_radii_unity": all(abs(float(bp.radius) - 1.0) <= 1e-7
                                 for bp in spout.data.splines[0].bezier_points),
        "spout_bevel_depth_one": abs(float(spout.data.bevel_depth) - 1.0) <= 1e-7,
        "spout_fill_caps": bool(spout.data.use_fill_caps),
        "handle_points_14": len(handle.data.splines[0].bezier_points) == len(HANDLE_PX_R),
        "handle_radii_match": max(abs(1000.0 * float(bp.radius) - r_mm)
                                  for bp, (_u, _v, r_mm) in
                                  zip(handle.data.splines[0].bezier_points, HANDLE_PX_R)) <= 1e-6,
        "parts_finite": all(ev["finite"] for ev in (spout_ev, handle_ev)),
        "parts_no_zero_area": all(ev["zero_area_tris"] == 0 for ev in (spout_ev, handle_ev)),
        "parts_no_loose": all(ev["loose_verts"] == 0 for ev in (spout_ev, handle_ev)),
    }

    # Record the run's checkpoint hashes in the baseline sidecar.
    baseline["checkpoints"] = {
        "pre_handle": {"path": str(PRE_HANDLE), "sha256": pre_sha,
                       "bytes": PRE_HANDLE.stat().st_size},
        "final": {"path": str(CORRECTED), "sha256": corrected_sha,
                  "bytes": CORRECTED.stat().st_size},
    }
    BASELINE.write_text(json.dumps(baseline, indent=2, sort_keys=True), encoding="utf-8")

    result = {
        "stage": "stage1",
        "review": baseline["review"],
        "checkpoints": baseline["checkpoints"],
        "live": {"filepath": bpy.data.filepath, "dirty": bool(bpy.data.is_dirty)},
        "spout": {
            "points_local_m": [[float(c) for c in bp.co]
                               for bp in spout.data.splines[0].bezier_points],
            "px": SPOUT_AXIS_PX,
            "radii_mm": [1000.0 * float(bp.radius)
                         for bp in spout.data.splines[0].bezier_points],
            "taper_object": spout.data.taper_object.name,
            "bevel_depth": float(spout.data.bevel_depth),
            "use_fill_caps": bool(spout.data.use_fill_caps),
        },
        "handle": {
            "points_local_m": [[float(c) for c in bp.co]
                               for bp in handle.data.splines[0].bezier_points],
            "px_r": HANDLE_PX_R,
            "radii_mm": [1000.0 * float(bp.radius)
                         for bp in handle.data.splines[0].bezier_points],
            "bevel_depth": float(handle.data.bevel_depth),
        },
        "taper": {
            "points_t_radius_mm": [[_r(t, 6), _r(1000.0 * p.y, 4)]
                                   for t, p in zip(ts, taper_points)],
            "points_local_m": [[float(c) for c in p] for p in taper_points],
            "parent": taper.parent.name,
            "local_identity_max": _local_identity_max(taper),
            "materials": _slots(taper),
            "hide_render": bool(taper.hide_render),
            "collection": COLL,
        },
        "eval": {
            "nt": {"CF_Body_A": int(a_ev["nt"]), SPOUT: int(spout_ev["nt"]),
                   HANDLE: int(handle_ev["nt"])},
            "nv": {"CF_Body_A": int(a_ev["nv"]), SPOUT: int(spout_ev["nv"]),
                   HANDLE: int(handle_ev["nv"])},
            "spout": _part_metrics(spout_ev, tree),
            "handle": _handle_metrics(handle_ev, tree),
        },
        "rose_max_diameter_mm": radial["rose_max_diameter_mm"],
        "rose_max_diameter_design_mm": 2.0 * max(SPOUT_RADII_MM),
        "rose_face_disc_mm": radial["rose_face_disc_mm"],
        "rose_face_disc_design_mm": 2.0 * SPOUT_RADII_MM[-1],
        "spout_face_centre_z_mm": _r(1000.0 * spout_axis[-1].z, 4),
        "checks": {k: bool(v) for k, v in checks.items()},
        "checks_all_pass": all(checks.values()),
        "before": {
            "spout": baseline["parts_before"][SPOUT],
            "handle": baseline["parts_before"][HANDLE],
            "handle_bbox_bottom_z_mm": baseline["parts_before"][HANDLE]["bbox_bottom_z_mm"],
            "handle_outer_minus_y_mm": baseline["parts_before"][HANDLE]["bbox_outer_minus_y_mm"],
            "handle_bbox_top_z_mm": baseline["parts_before"][HANDLE]["bbox_top_z_mm"],
            "rose_max_diameter_mm": baseline["parts_before"][SPOUT]["radial"]["rose_max_diameter_mm"],
            "spout_face_centre_z_mm": baseline["parts_before"][SPOUT]["face_centre_z_mm"],
        },
        "baseline": {"path": str(BASELINE), "sha256": A.sha256_file(BASELINE)},
        "note": "No renders in stage1. Stage2 opens the saved final checkpoint.",
    }
    print("STAGE1_OK " + json.dumps(result, sort_keys=True))
    return result


def stage2():
    _ensure_open(CORRECTED)
    live = Path(bpy.data.filepath) if bpy.data.filepath else None
    _req(live is not None and live.resolve() == CORRECTED.resolve(),
         "live file is not assembly_corrected_01.blend: %s" % live)
    _req(not bpy.data.is_dirty, "corrected checkpoint opened dirty")
    _req(BASELINE.exists(), "stage1 baseline missing: %s" % BASELINE)
    _req(not PROOF.exists(), "proof already exists: %s" % PROOF)
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    corrected_sha_at_load = A.sha256_file(CORRECTED)

    ctrl = bpy.data.objects.get(A.ROOT)
    body = bpy.data.objects.get("CF_Body_A")
    ref = bpy.data.objects.get("CF_Ref_Plane")
    spout = bpy.data.objects.get(SPOUT)
    handle = bpy.data.objects.get(HANDLE)
    taper = bpy.data.objects.get(TAPER)
    _req(all(o is not None for o in (ctrl, body, ref, spout, handle, taper)),
         "one of root/body/reference/spout/handle/taper is missing")

    dg = bpy.context.evaluated_depsgraph_get()
    a_ev = A.eval_world(body, dg)
    spout_ev = A.eval_world(spout, dg)
    handle_ev = A.eval_world(handle, dg)
    tree = A.bvh_body(a_ev)
    spout_axis = _axis_world(spout)
    handle_axis = _axis_world(handle)
    radial = _spout_radial_metrics(spout_ev, spout_axis)

    before_pts = np.asarray(base["body_A"]["eval_points"], dtype=np.float64)
    a_cong = A.kd_bidir(a_ev["pts"], before_pts)
    a_src_now = A.mesh_source_hash(body.data)
    a_src_eq = a_src_now == base["body_A"]["source_hash"]

    now_targets = {n: {"matrix": A.mat_list(bpy.data.objects[n].matrix_world),
                       "source_hash": A.mesh_source_hash(bpy.data.objects[n].data)
                       if bpy.data.objects[n].type == "MESH" else None,
                       "materials": _slots(bpy.data.objects[n]),
                       "visibility": _vis(bpy.data.objects[n])}
                   for n in A.TARGETS}
    prot = {n: _flat_diff(bpy.data.objects[n].matrix_world, base["targets"][n]["matrix"])
            for n in A.TARGETS}
    source_hash_equal = {n: now_targets[n]["source_hash"] == base["targets"][n]["source_hash"]
                         for n in A.TARGETS}
    materials_targets_same = all(now_targets[n]["materials"] == base["targets"][n]["materials"]
                                 for n in A.TARGETS)
    vis_targets_same = all(now_targets[n]["visibility"] == base["targets"][n]["visibility"]
                           for n in A.TARGETS)

    root_bit = all(float(ctrl.matrix_world[i][j]) == float(base["root"]["matrix"][i * 4 + j])
                   for i in range(4) for j in range(4))
    root_max = _flat_diff(ctrl.matrix_world, base["root"]["matrix"])
    children = sorted(o.name for o in ctrl.children)
    children_expected = sorted(base["root"]["children"] + [TAPER])
    ref_max = _flat_diff(ref.matrix_world, base["reference"]["matrix"])
    ref_vis_same = _vis(ref) == base["reference"]["vis"]
    ref_locks_same = A.locks(ref) == base["reference"]["locks"]
    ref_mat_same = _slots(ref) == base["reference"]["materials"]
    ref_fixed = (ref_max <= TOL and ref_vis_same and ref_locks_same and ref_mat_same)

    objects_now = sorted(o.name for o in bpy.data.objects)
    removed = [n for n in base["objects"] if n not in objects_now]
    added = [n for n in objects_now if n not in base["objects"]]
    materials_now = sorted(m.name for m in bpy.data.materials)
    materials_same = materials_now == base["materials"]

    taper_local_max = _local_identity_max(taper)
    taper_in_coll = any(o == taper for o in bpy.data.collections[COLL].objects)
    taper_points_now = [[float(c) for c in bp.co]
                        for bp in taper.data.splines[0].bezier_points]
    taper_points_base = base["planned"]["taper_points_local_m"]
    taper_points_max = (max(abs(x - y) for p, q in zip(taper_points_now, taper_points_base)
                            for x, y in zip(p, q))
                        if len(taper_points_now) == len(taper_points_base) else None)
    spout_radii = [float(bp.radius) for bp in spout.data.splines[0].bezier_points]
    handle_radii = [1000.0 * float(bp.radius)
                    for bp in handle.data.splines[0].bezier_points]
    handle_radius_max = (max(abs(r - s) for r, s in zip(handle_radii, HANDLE_PX_R_COL))
                         if len(handle_radii) == len(HANDLE_PX_R) else None)
    spout_axis_max = max((spout_axis[i] - A.world_mm(u, v)).length
                         for i, (u, v) in enumerate(SPOUT_AXIS_PX))
    handle_axis_max = max((handle_axis[i] - A.world_mm(u, v)).length
                          for i, (u, v, _r_mm) in enumerate(HANDLE_PX_R))
    spout_face_z = 1000.0 * spout_axis[-1].z
    handle_bbox_bottom = 1000.0 * handle_ev["bbox_min"][2]
    handle_outer = -1000.0 * handle_ev["bbox_min"][1]
    handle_top = 1000.0 * handle_ev["bbox_max"][2]
    spout_min = _min_to_body_mm(spout_ev, tree)
    handle_min = _min_to_body_mm(handle_ev, tree)

    after = {
        "rose_max_diameter_mm": radial["rose_max_diameter_mm"],
        "rose_face_disc_mm": radial["rose_face_disc_mm"],
        "rose_max_diameter_design_mm": 2.0 * max(SPOUT_RADII_MM),
        "rose_face_disc_design_mm": 2.0 * SPOUT_RADII_MM[-1],
        "handle_bbox_bottom_z_mm": _r(handle_bbox_bottom, 6),
        "handle_outer_minus_y_mm": _r(handle_outer, 6),
        "handle_bbox_top_z_mm": _r(handle_top, 6),
        "spout_face_centre_z_mm": _r(spout_face_z, 6),
        "min_vertex_to_body_mm": {SPOUT: spout_min, HANDLE: handle_min},
        "spout": _part_metrics(spout_ev, tree),
        "handle": _handle_metrics(handle_ev, tree),
    }
    before = {
        "rose_max_diameter_mm": base["parts_before"][SPOUT]["radial"]["rose_max_diameter_mm"],
        "rose_face_disc_mm": base["parts_before"][SPOUT]["radial"]["rose_face_disc_mm"],
        "handle_bbox_bottom_z_mm": base["parts_before"][HANDLE]["bbox_bottom_z_mm"],
        "handle_outer_minus_y_mm": base["parts_before"][HANDLE]["bbox_outer_minus_y_mm"],
        "handle_bbox_top_z_mm": base["parts_before"][HANDLE]["bbox_top_z_mm"],
        "spout_face_centre_z_mm": base["parts_before"][SPOUT]["face_centre_z_mm"],
        "min_vertex_to_body_mm": {
            SPOUT: base["parts_before"][SPOUT]["metrics"]["min_vertex_to_body_mm"],
            HANDLE: base["parts_before"][HANDLE]["metrics"]["min_vertex_to_body_mm"]},
        "counts": {SPOUT: {k: base["parts_before"][SPOUT]["metrics"][k]
                           for k in ("nv", "nt", "zero_area_tris", "loose_verts", "finite")},
                   HANDLE: {k: base["parts_before"][HANDLE]["metrics"][k]
                            for k in ("nv", "nt", "zero_area_tris", "loose_verts", "finite")},
                   "CF_Body_A": {k: base["body_A"]["eval"][k]
                                 for k in ("nv", "nt", "zero_area_tris", "loose_verts", "finite")}},
    }
    residuals = {}
    for key in TARGETS_MM:
        residuals[key] = {"before": before[key], "after": after[key],
                          "target": TARGETS_MM[key],
                          "delta_vs_target": _r(after[key] - TARGETS_MM[key], 4),
                          "delta_vs_before": _r(after[key] - before[key], 4)}
    residuals["min_vertex_to_body_mm"] = {
        SPOUT: {"before": before["min_vertex_to_body_mm"][SPOUT],
                "after": after["min_vertex_to_body_mm"][SPOUT]},
        HANDLE: {"before": before["min_vertex_to_body_mm"][HANDLE],
                 "after": after["min_vertex_to_body_mm"][HANDLE]},
    }
    residuals["counts"] = {
        "before": before["counts"],
        "after": {SPOUT: {k: after["spout"][k] for k in
                          ("nv", "nt", "zero_area_tris", "loose_verts", "finite")},
                  HANDLE: {k: after["handle"][k] for k in
                           ("nv", "nt", "zero_area_tris", "loose_verts", "finite")},
                  "CF_Body_A": {k: a_ev[k] for k in
                                ("nv", "nt", "zero_area_tris", "loose_verts", "finite")}},
    }

    checks = {
        "live_file_is_corrected_checkpoint": True,
        "A_source_hash_equal": bool(a_src_eq),
        "A_evaluated_bidir_0p01mm": bool(a_cong <= TOL
                                         and int(a_ev["nt"]) == int(base["body_A"]["eval"]["nt"])),
        "protected_matrices_0p01mm": bool(max(prot.values()) <= TOL),
        "root_matrix_bit_identical": bool(root_bit),
        "root_children_include_only_taper": bool(children == children_expected),
        "reference_matrix_0p01mm": bool(ref_max <= TOL),
        "reference_visibility_locks_unchanged": bool(ref_vis_same and ref_locks_same),
        "body_visibility_unchanged": bool(vis_targets_same),
        "materials_unchanged": bool(materials_targets_same and ref_mat_same and materials_same),
        "no_objects_removed": bool(not removed),
        "only_taper_added": bool(added == [TAPER]),
        "taper_parented_identity": bool(taper.parent == ctrl
                                        and taper_local_max <= 1e-6),
        "taper_in_assembly_collection": bool(taper_in_coll),
        "taper_no_material_render_hidden": bool(len(taper.data.materials) == 0
                                                and taper.hide_render),
        "taper_points_match_stage1": bool(taper_points_max is not None
                                          and taper_points_max <= 1e-6),
        "spout_taper_object_set": bool(spout.data.taper_object == taper),
        "spout_radii_unity": bool(all(abs(r - 1.0) <= 1e-7 for r in spout_radii)),
        "spout_bevel_depth_one": bool(abs(float(spout.data.bevel_depth) - 1.0) <= 1e-7),
        "spout_fill_caps": bool(spout.data.use_fill_caps),
        "spout_axis_matches_px_0p001mm": bool(spout_axis_max <= 1e-6),
        "handle_radii_match_table": bool(handle_radius_max is not None
                                         and handle_radius_max <= 1e-6),
        "handle_axis_matches_px_0p001mm": bool(handle_axis_max <= 1e-6),
        "parts_finite": bool(spout_ev["finite"] and handle_ev["finite"]),
        "parts_no_zero_area": bool(spout_ev["zero_area_tris"] == 0
                                   and handle_ev["zero_area_tris"] == 0),
        "parts_no_loose": bool(spout_ev["loose_verts"] == 0 and handle_ev["loose_verts"] == 0),
        "parts_contact_body": bool(spout_min is not None and handle_min is not None
                                   and spout_min <= 0.5 and handle_min <= 0.5),
    }

    scene = bpy.context.scene
    saved_hide = {o.name: bool(o.hide_render) for o in bpy.data.objects}
    saved_scene = (scene.camera, scene.render.resolution_x, scene.render.resolution_y,
                   scene.render.resolution_percentage, scene.render.film_transparent,
                   scene.render.image_settings.file_format,
                   scene.render.image_settings.color_mode, scene.render.filepath)
    pre_render_objects = sorted(o.name for o in bpy.data.objects)
    cam = cd = None
    try:
        cam, cd = _spout_temp_camera()
        full = A.render_view(SIDE_FULL, "CF_Cam_Side", (402, 327), True, True, False, True)
        B.save_rgba(SIDE_OVERLAY, contour_overlay(B.load_rgba(A.REF), full[:, :, 3]))
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
         scene.render.image_settings.file_format, scene.render.image_settings.color_mode,
         scene.render.filepath) = saved_scene
        bpy.context.view_layer.update()

    paths = (SIDE_FULL, SIDE_OVERLAY, SIDE_NEUTRAL, TQ_HANDLE, TQ_HANDLE_N,
             TQ_SPOUT, TQ_SPOUT_N)
    objects_restored = sorted(o.name for o in bpy.data.objects) == pre_render_objects
    hide_restored = all(bool(bpy.data.objects[n].hide_render) == v
                        for n, v in saved_hide.items() if n in bpy.data.objects)
    proof = {
        "stage": "stage2",
        "checkpoint": {"path": str(CORRECTED), "sha256": corrected_sha_at_load,
                       "sha256_after_verification": A.sha256_file(CORRECTED),
                       "live_filepath": bpy.data.filepath,
                       "dirty_at_load": False,
                       "saved_by_this_stage": False},
        "baseline": {"path": str(BASELINE), "sha256": A.sha256_file(BASELINE),
                     "review": base["review"]},
        "preservation": {
            "A_source_hash_equal": bool(a_src_eq),
            "A_source_hash_before": base["body_A"]["source_hash"],
            "A_source_hash_after": a_src_now,
            "A_eval_bidir_mm": _r(1000.0 * a_cong, 6),
            "A_eval_counts": {"before": [base["body_A"]["eval"]["nv"],
                                          base["body_A"]["eval"]["nt"]],
                               "after": [int(a_ev["nv"]), int(a_ev["nt"])]},
            "protected_matrix_maxdiff_mm": {n: _r(1000.0 * prot[n], 6) for n in A.TARGETS},
            "all_target_source_hashes_equal": all(source_hash_equal.values()),
            "root_matrix_maxdiff": root_max,
            "root_matrix_bit_identical": bool(root_bit),
            "root_children": children,
            "root_children_expected": children_expected,
            "reference_matrix_maxdiff_mm": _r(1000.0 * ref_max, 6),
            "reference_visibility_unchanged": bool(ref_vis_same),
            "reference_locks_unchanged": bool(ref_locks_same),
            "reference_materials_unchanged": bool(ref_mat_same),
            "materials_list_unchanged": bool(materials_same),
            "target_materials_unchanged": bool(materials_targets_same),
            "target_visibility_unchanged": bool(vis_targets_same),
            "objects_removed": removed,
            "objects_added": added,
        },
        "residuals": residuals,
        "targets_mm": TARGETS_MM,
        "structure": {
            "taper": {"parent": taper.parent.name if taper.parent else None,
                       "local_identity_max": taper_local_max,
                       "in_assembly_collection": bool(taper_in_coll),
                       "materials": _slots(taper),
                       "hide_render": bool(taper.hide_render),
                       "points_t_radius_mm": [[_r(bp.co.x, 6), _r(1000.0 * bp.co.y, 4)]
                                              for bp in taper.data.splines[0].bezier_points],
                       "points_match_stage1_max": taper_points_max},
            "spout": {"taper_object": spout.data.taper_object.name
                      if spout.data.taper_object else None,
                      "point_count": len(spout.data.splines[0].bezier_points),
                      "radii": spout_radii,
                      "bevel_depth": float(spout.data.bevel_depth),
                      "use_fill_caps": bool(spout.data.use_fill_caps),
                      "axis_px_maxdiff_mm": _r(1000.0 * spout_axis_max, 6)},
            "handle": {"point_count": len(handle.data.splines[0].bezier_points),
                        "radii_mm": handle_radii,
                        "radii_maxdiff_mm": _r(handle_radius_max, 6)
                        if handle_radius_max is not None else None,
                        "bevel_depth": float(handle.data.bevel_depth),
                        "axis_px_maxdiff_mm": _r(1000.0 * handle_axis_max, 6)},
        },
        "checks": {k: bool(v) for k, v in checks.items()},
        "checks_all_pass": all(checks.values()),
        "captures": {p.name: A.sha256_file(p) for p in paths},
        "cleanup": {"temp_camera_removed": bpy.data.objects.get(TEMP_CAM) is None,
                    "objects_restored": bool(objects_restored),
                    "hide_render_restored": bool(hide_restored),
                    "saved_by_stage2": False},
        "measurement": {
            "rose": "max radial distance to the axis polyline for evaluated spout "
                    "vertices at normalised chord fraction >= 0.80, doubled",
            "face_disc": "max radial distance for vertices with axis fraction >= 0.9995, "
                         "doubled (fallback 0.995)",
            "design_values_from_taper_table": True,
        },
        "limitations": [
            "one stylized elevated side reference; hidden depth inferred as circular sections",
            "rose/face measured on bevel-sampled evaluated geometry; design radii reported separately",
            "evaluated triangle counts are not final topology",
            "no shell, thickness, bore, sprinkler holes, union, UVs or export",
            "stage2 saves nothing; the checkpoint hash is re-read after rendering",
        ],
    }
    PROOF.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print("STAGE2_OK " + json.dumps(proof, sort_keys=True))
    return proof


# Handle radii column helper used by the stage2 table check.
HANDLE_PX_R_COL = [r for _u, _v, r in HANDLE_PX_R]

if __name__ == "__main__":
    stage = sys.argv[-1] if sys.argv and sys.argv[-1] in ("stage1", "stage2") else ""
    try:
        if stage == "stage1":
            stage1()
        elif stage == "stage2":
            stage2()
        else:
            raise RuntimeError("usage: -- stage1 | stage2")
    except Exception:
        traceback.print_exc()
        raise
