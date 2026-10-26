"""Bounded spout + open-handle blockout for the selected CF_Body_A watering can.

User approved one assembly-shape pass. Body/cutters/root are protected; reference
plane and cameras stay outside Model_Control. New visible parts are editable Bezier
path sweeps parented to Model_Control in the current authored pose. No shell, bore,
holes, union, UV, bake or export. Stages: baseline, build, evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
import traceback
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector, kdtree
from mathutils.bvhtree import BVHTree

BASE = Path("/Users/hydraxon/Documents/GitHub/AssetWorkshop")
TOOLS = BASE / "tools" / "asset-pipeline" / "scripts"
FIXTURES = BASE / "tools" / "asset-pipeline" / "fixtures"
ASSET = BASE / ".dev-shots" / "asset-pipeline" / "wateringcan_v2" / "curve_fit_01" / "assembly_01"
BASELINE = ASSET / "assembly_baseline_01.blend"
BASELINE_JSON = ASSET / "assembly_baseline_01_records.json"
BLOCKOUT = ASSET / "assembly_blockout_01.blend"
PROOF = ASSET / "assembly_proof.json"
REF = (BASE / ".dev-shots" / "asset-pipeline" / "wateringcan_body_trial" /
       "reference" / "derived" / "plane_profile.png")
ROOT = "Model_Control"
PARTS = ("CF_Spout_Path", "CF_Handle_Path")
TARGETS = ["CF_Body_A", "CF_Body_B", "CF_Body_C", "CF_Profile_A", "CF_Profile_B",
           "CF_Profile_C", "CF_Cutter_A", "CF_Cutter_B", "CF_Cutter_C"]
TOL = 1e-5       # 0.01 mm
EXACT = 1e-9

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from reference_compare import contour_overlay  # noqa: E402

spec = __import__("importlib.util", fromlist=["util"]).spec_from_file_location(
    "build_wateringcan_profile", FIXTURES / "build_wateringcan_profile.py")
B = __import__("importlib.util", fromlist=["util"]).module_from_spec(spec)
spec.loader.exec_module(B)
FRAME = B.FRAME


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mat_list(m):
    return [float(m[r][c]) for r in range(4) for c in range(4)]


def visibility(obj):
    return {"hide_viewport": bool(obj.hide_viewport),
            "hide_render": bool(obj.hide_render),
            "hide_select": bool(obj.hide_select),
            "hide_get": bool(obj.hide_get())}


def locks(obj):
    return {key: [bool(v) for v in getattr(obj, attr)]
            for key, attr in (("location", "lock_location"), ("rotation", "lock_rotation"),
                              ("rotation_euler", "lock_rotation_euler"),
                              ("rotation_quaternion", "lock_rotation_quaternion"),
                              ("scale", "lock_scale"))
            if getattr(obj, attr, None) is not None}


def mesh_source_hash(me):
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    pv = []
    for p in me.polygons:
        pv.extend(int(v) for v in p.vertices)
    h = hashlib.sha256()
    h.update(struct.pack("<ii", n, len(me.polygons)))
    h.update(np.ascontiguousarray(co).tobytes())
    h.update(np.asarray(pv, dtype=np.int32).tobytes())
    return h.hexdigest()


def obj_record(obj):
    rec = {"type": obj.type, "parent": obj.parent.name if obj.parent else None,
           "parent_type": obj.parent_type,
           "matrix_world": mat_list(obj.matrix_world),
           "location": [float(v) for v in obj.location],
           "rotation_mode": obj.rotation_mode,
           "rotation_euler_deg": [math.degrees(float(v)) for v in obj.rotation_euler],
           "scale": [float(v) for v in obj.scale],
           "visibility": visibility(obj), "locks": locks(obj)}
    if obj.type == "MESH":
        rec.update({"mesh": obj.data.name, "users": int(obj.data.users),
                    "source_hash": mesh_source_hash(obj.data),
                    "materials": [m.name if m else None for m in obj.data.materials]})
    return rec


def eval_world(obj, dg):
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3).astype(np.float64)
    me.calc_loop_triangles()
    nt = len(me.loop_triangles)
    tri = np.empty(nt * 3, dtype=np.int32)
    me.loop_triangles.foreach_get("vertices", tri)
    tri = tri.reshape(-1, 3)
    m = np.array(ev.matrix_world, dtype=np.float64)
    pts = co @ m[:3, :3].T + m[:3, 3]
    area = 0.0
    zero = 0
    if nt:
        e1 = pts[tri[:, 1]] - pts[tri[:, 0]]
        e2 = pts[tri[:, 2]] - pts[tri[:, 0]]
        ar = np.linalg.norm(np.cross(e1, e2), axis=1) * 0.5
        area = float(ar.sum())
        zero = int((ar <= 1e-12).sum())
    used = np.zeros(n, dtype=bool)
    if nt:
        used[np.unique(tri)] = True
    out = {"nv": int(n), "nt": int(nt), "area_m2": area, "zero_area_tris": zero,
           "loose_verts": int((~used).sum()), "finite": bool(np.isfinite(pts).all()),
           "pts": pts, "tri": tri,
           "bbox_min": pts.min(axis=0).tolist() if n else None,
           "bbox_max": pts.max(axis=0).tolist() if n else None}
    ev.to_mesh_clear()
    return out


def bvh_body(part_eval):
    return BVHTree.FromPolygons([tuple(p) for p in part_eval["pts"]],
                                [tuple(int(i) for i in t) for t in part_eval["tri"]],
                                all_triangles=True)


def surface_max(pts, tree):
    worst = 0.0
    for p in pts:
        _loc, _n, _i, d = tree.find_nearest(Vector((float(p[0]), float(p[1]), float(p[2]))))
        worst = max(worst, float(d) if d is not None else 1e9)
    return worst


def kd_bidir(a, b):
    def one(src, dst):
        tree = kdtree.KDTree(len(dst))
        for i, p in enumerate(dst):
            tree.insert(Vector((float(p[0]), float(p[1]), float(p[2]))), i)
        tree.balance()
        return max(tree.find(Vector((float(p[0]), float(p[1]), float(p[2]))))[2]
                   for p in src)
    return max(one(a, b), one(b, a))


def world_mm(u, v):
    return Vector(FRAME.pixel_to_world_mm(u, v)) / 1000.0


# Reference-derived landmarks in the shared side frame (image px, top-left).
SPOUT_PX = [(150, 255, 26), (140, 235, 26), (122, 200, 22), (100, 165, 18),
            (84, 140, 15.5), (78, 132, 15), (49, 111, 31)]
HANDLE_PX = [(290, 88, 12.5), (295, 95, 11.5), (305, 105, 11), (325, 115, 11),
             (348, 140, 11), (362, 170, 11), (365, 200, 11), (357, 230, 11),
             (340, 245, 11), (323, 250, 11.5), (312, 256, 12), (300, 260, 12.5)]
CENTERS = {"spout_rose_face": (49, 111), "spout_neck": (82, 137),
           "spout_root": (140, 235), "handle_top": (293, 95),
           "handle_outer": (365, 200), "handle_bottom": (317, 250)}


def baseline():
    if ASSET.exists():
        raise SystemExit("BLOCKED: asset directory already exists: " + str(ASSET))
    if BASELINE.exists() or BASELINE_JSON.exists():
        raise SystemExit("BLOCKED: baseline artifact exists")
    ASSET.mkdir(parents=True)
    if sha256_file(REF) != "2342335a9b29a3956edf8c987f59583da2200d63237210411ea83d08d96a9639":
        raise SystemExit("BLOCKED: reference image hash mismatch")
    dg = bpy.context.evaluated_depsgraph_get()
    ctrl = bpy.data.objects.get(ROOT)
    if ctrl is None:
        raise SystemExit("BLOCKED: Model_Control missing")
    missing = [n for n in TARGETS if bpy.data.objects.get(n) is None]
    if missing:
        raise SystemExit("BLOCKED: missing targets: " + ", ".join(missing))
    if any(bpy.data.objects.get(n) for n in PARTS):
        raise SystemExit("BLOCKED: assembly part name already exists")
    if bpy.data.collections.get("CF_Assembly_01"):
        raise SystemExit("BLOCKED: assembly collection already exists")
    body = bpy.data.objects["CF_Body_A"]
    ref = bpy.data.objects.get("CF_Ref_Plane")
    live = {"filepath": bpy.data.filepath, "is_dirty": bool(bpy.data.is_dirty),
            "saved_hash_before": sha256_file(bpy.data.filepath)
            if bpy.data.filepath and Path(bpy.data.filepath).exists() else None}
    rec = {
        "stage": "assembly_baseline_01",
        "source": {"reference": str(REF), "reference_sha256": sha256_file(REF),
                   "reference_resolution": [FRAME.width, FRAME.height],
                   "origin_px": list(FRAME.origin_px),
                   "mm_per_px": FRAME.mm_per_px},
        "live_before": live,
        "root": obj_record(ctrl),
        "root_children": sorted(o.name for o in ctrl.children),
        "objects": {o.name: obj_record(o) for o in bpy.data.objects},
        "materials": sorted(m.name for m in bpy.data.materials),
        "scene": {"camera": bpy.context.scene.camera.name
                  if bpy.context.scene.camera else None,
                  "engine": bpy.context.scene.render.engine,
                  "resolution": [bpy.context.scene.render.resolution_x,
                                 bpy.context.scene.render.resolution_y],
                  "frame": bpy.context.scene.frame_current},
        "body_A_eval": {k: v for k, v in eval_world(body, dg).items()
                        if k not in ("pts", "tri")},
        "reference_state": obj_record(ref) if ref else None,
        "object_count": len(bpy.data.objects), "mesh_count": len(bpy.data.meshes),
        "note": "Live state saved unchanged before visibility or geometry edits.",
    }
    bpy.ops.wm.save_as_mainfile(filepath=str(BASELINE), check_existing=False, copy=False)
    rec["saved"] = {"path": str(BASELINE), "sha256": sha256_file(BASELINE),
                    "live_filepath": bpy.data.filepath,
                    "dirty_after_save": bool(bpy.data.is_dirty),
                    "size_bytes": BASELINE.stat().st_size}
    with open(BASELINE_JSON, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
    print("ASSEMBLY_BASELINE_OK " + json.dumps({
        "path": str(BASELINE), "sha256": rec["saved"]["sha256"],
        "records": str(BASELINE_JSON),
        "root_matrix": rec["root"]["matrix_world"],
        "root_euler_deg": rec["root"]["rotation_euler_deg"],
        "root_children": rec["root_children"],
        "body_A_eval": rec["body_A_eval"],
        "A_visibility": rec["objects"]["CF_Body_A"]["visibility"],
        "B_visibility": rec["objects"]["CF_Body_B"]["visibility"],
        "C_visibility": rec["objects"]["CF_Body_C"]["visibility"],
        "reference_visibility": rec["reference_state"]["visibility"] if ref else None,
        "materials": rec["materials"], "engine": rec["scene"]["engine"],
        "live_dirty": rec["saved"]["dirty_after_save"],
    }, sort_keys=True))
    return rec


def make_curve(name, spec_points, ctrl, coll, material):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 12
    data.bevel_depth = 1.0
    data.bevel_resolution = 4
    data.fill_mode = "FULL"
    data.use_fill_caps = True
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(spec_points) - 1)
    inv = ctrl.matrix_world.inverted()
    for bp, (u, v, r_mm) in zip(spline.bezier_points, spec_points):
        bp.co = inv @ world_mm(u, v)
        bp.radius = r_mm / 1000.0
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, data)
    coll.objects.link(obj)
    data.materials.append(material)
    obj.parent = ctrl
    obj.parent_type = "OBJECT"
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_world = ctrl.matrix_world
    obj.hide_viewport = False
    obj.hide_render = False
    obj.hide_select = False
    obj["role"] = name.split("_")[1].lower()
    obj["construction"] = ("editable Bezier path, round bevelled sweep, per-point radius; "
                           "caps; no holes/bore/shell")
    obj["reference_px"] = json.dumps(spec_points)
    obj["depth_note"] = ("circular inferred section, centred on the X=0 reference "
                         "median plane; hidden depth is provisional")
    return obj


def build():
    if not BASELINE.exists() or not BASELINE_JSON.exists():
        raise SystemExit("BLOCKED: run baseline first")
    if BLOCKOUT.exists():
        raise SystemExit("BLOCKED: blockout already exists")
    if any(bpy.data.objects.get(n) for n in PARTS):
        raise SystemExit("BLOCKED: assembly parts already exist")
    ctrl = bpy.data.objects.get(ROOT)
    if ctrl is None or bpy.data.objects.get("CF_Body_A") is None:
        raise SystemExit("BLOCKED: root or selected body missing")
    if len(ctrl.children) != 9:
        raise SystemExit("BLOCKED: root child count changed: %d" % len(ctrl.children))
    rec = json.loads(BASELINE_JSON.read_text())
    current = {n: obj_record(bpy.data.objects[n]) for n in TARGETS}
    drift = {n: max(abs(a - b) for a, b in
                    zip(current[n]["matrix_world"], rec["objects"][n]["matrix_world"]))
             for n in TARGETS}
    if max(drift.values()) > EXACT:
        raise SystemExit("BLOCKED: protected transforms changed since baseline: " + json.dumps(drift))
    M0 = ctrl.matrix_world.copy()
    if abs(M0[2][2] - 1.0) > 1e-6 or abs(M0.to_euler("XYZ").x) > 1e-6:
        raise SystemExit("BLOCKED: root is not a Z-only transform; inspect first")
    inv = M0.inverted()

    # Honor the user's candidate selection in render as well as viewport.
    vis_fix = {}
    for key in "ABC":
        obj = bpy.data.objects["CF_Body_" + key]
        vis_fix[obj.name] = visibility(obj)
        obj.hide_viewport = key != "A"
        obj.hide_render = key != "A"
        obj.hide_set(key != "A")
    plane = bpy.data.objects.get("CF_Ref_Plane")
    if plane:
        plane.hide_render = True
        plane.hide_viewport = False
        plane.hide_set(False)
        plane.hide_select = True
        for arr in (plane.lock_location, plane.lock_rotation, plane.lock_scale):
            for i in range(3):
                arr[i] = True

    coll = bpy.data.collections.new("CF_Assembly_01")
    bpy.context.scene.collection.children.link(coll)
    material = bpy.data.materials.get("CF_Clay") or bpy.data.materials.get("Clay")
    if material is None:
        material = B.clay_material()
    spout = make_curve("CF_Spout_Path", SPOUT_PX, ctrl, coll, material)
    handle = make_curve("CF_Handle_Path", HANDLE_PX, ctrl, coll, material)
    bpy.context.view_layer.update()

    dg = bpy.context.evaluated_depsgraph_get()
    body_eval = eval_world(bpy.data.objects["CF_Body_A"], dg)
    pts_eval = {n: eval_world(bpy.data.objects[n], dg) for n in PARTS}
    tree = bvh_body(body_eval)
    metrics = {}
    for name, ev in pts_eval.items():
        metrics[name] = {
            "world_bbox_min_mm": [round(v * 1000, 3) for v in ev["bbox_min"]],
            "world_bbox_max_mm": [round(v * 1000, 3) for v in ev["bbox_max"]],
            "nv": ev["nv"], "nt": ev["nt"], "zero_area_tris": ev["zero_area_tris"],
            "loose_verts": ev["loose_verts"], "finite": ev["finite"],
            "min_vertex_to_body_mm": round(1000 * min(
                tree.find_nearest(Vector((float(p[0]), float(p[1]), float(p[2]))))[3]
                for p in ev["pts"]), 4),
            "verts_touching_body": int(sum(
                1 for p in ev["pts"] if tree.find_nearest(
                    Vector((float(p[0]), float(p[1]), float(p[2]))))[3] < 1e-4)),
            "parent": bpy.data.objects[name].parent.name,
            "local_matrix_identity": max(abs(float(v)) for row in
                                         (bpy.data.objects[name].matrix_local -
                                          Matrix.Identity(4)) for v in row) < EXACT,
            "path_points": len(bpy.data.objects[name].data.splines[0].bezier_points),
        }
    checks = {
        "spout_parented": bpy.data.objects["CF_Spout_Path"].parent == ctrl,
        "handle_parented": bpy.data.objects["CF_Handle_Path"].parent == ctrl,
        "both_finite": all(m["finite"] for m in metrics.values()),
        "no_zero_area": all(m["zero_area_tris"] == 0 for m in metrics.values()),
        "no_loose": all(m["loose_verts"] == 0 for m in metrics.values()),
        "body_contact": all(m["min_vertex_to_body_mm"] <= 0.5 for m in metrics.values()),
        "A_render_visible": not bpy.data.objects["CF_Body_A"].hide_render,
        "B_C_render_hidden": all(bpy.data.objects["CF_Body_" + k].hide_render
                                 for k in "BC"),
    }
    bpy.ops.wm.save_as_mainfile(filepath=str(BLOCKOUT), check_existing=False, copy=False)
    result = {
        "stage": "assembly_blockout_01", "saved": str(BLOCKOUT),
        "sha256": sha256_file(BLOCKOUT),
        "live_filepath": bpy.data.filepath,
        "live_dirty": bool(bpy.data.is_dirty),
        "root_matrix": mat_list(ctrl.matrix_world),
        "selection": {"active": bpy.context.view_layer.objects.active.name
                      if bpy.context.view_layer.objects.active else None,
                      "selected": [o.name for o in bpy.data.objects if o.select_get()]},
        "visibility_fixed": vis_fix, "metrics": metrics, "checks": checks,
        "part_world_landmarks": {
            "spout_rose_face_mm": [round(v * 1000, 2) for v in
                                   (bpy.data.objects["CF_Spout_Path"].matrix_world @
                                    bpy.data.objects["CF_Spout_Path"].data.splines[0].bezier_points[-1].co)],
            "handle_outer_mm": [round(v * 1000, 2) for v in
                                (bpy.data.objects["CF_Handle_Path"].matrix_world @
                                 bpy.data.objects["CF_Handle_Path"].data.splines[0].bezier_points[6].co)]},
        "material": material.name,
    }
    with open(ASSET / "assembly_build_01_result.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
    print("ASSEMBLY_BUILD_OK " + json.dumps(result, sort_keys=True))
    return result


def render_view(path, cam_name, res, show_body, show_parts, show_plane,
                transparent=True):
    scene = bpy.context.scene
    saved = {o.name: bool(o.hide_render) for o in bpy.data.objects}
    saved_state = (scene.camera, scene.render.resolution_x, scene.render.resolution_y,
                   scene.render.resolution_percentage, scene.render.film_transparent,
                   scene.render.image_settings.file_format,
                   scene.render.image_settings.color_mode, scene.render.filepath)
    try:
        for o in bpy.data.objects:
            if o.type in ("MESH", "CURVE"):
                o.hide_render = True
        for name in ("CF_Sun_Key", "CF_Sun_Fill"):
            light = bpy.data.objects.get(name)
            if light:
                light.hide_render = False
        bpy.data.objects["CF_Body_A"].hide_render = not show_body
        for name in PARTS:
            bpy.data.objects[name].hide_render = not show_parts
        plane = bpy.data.objects.get("CF_Ref_Plane")
        if plane:
            plane.hide_render = not show_plane
        scene.camera = bpy.data.objects[cam_name]
        scene.render.resolution_x, scene.render.resolution_y = res
        scene.render.resolution_percentage = 100
        scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1.0
        scene.render.film_transparent = transparent
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
    finally:
        for o in bpy.data.objects:
            if o.name in saved:
                o.hide_render = saved[o.name]
        (scene.camera, scene.render.resolution_x, scene.render.resolution_y,
         scene.render.resolution_percentage, scene.render.film_transparent,
         scene.render.image_settings.file_format, scene.render.image_settings.color_mode,
         scene.render.filepath) = saved_state
    return B.load_rgba(path)


def root_test(ctrl):
    dg = bpy.context.evaluated_depsgraph_get()
    names = ["CF_Body_A"] + list(PARTS)
    base_mats = {n: bpy.data.objects[n].matrix_world.copy() for n in TARGETS + list(PARTS)}
    base_eval = {n: eval_world(bpy.data.objects[n], dg) for n in names}
    base_root = ctrl.matrix_world.copy()
    base_ref = eval_world(bpy.data.objects["CF_Ref_Plane"], dg)
    base_ref_mat = bpy.data.objects["CF_Ref_Plane"].matrix_world.copy()
    base_vis = {o.name: visibility(o) for o in bpy.data.objects}
    base_points = {n: [tuple(bp.co) for bp in
                       bpy.data.objects[n].data.splines[0].bezier_points] for n in PARTS}
    R = Matrix.Rotation(math.radians(90.0), 4, "Z")
    R3 = np.array(R, dtype=np.float64)[:3, :3]
    out = {"base_root": mat_list(base_root), "applied": mat_list(R)}
    try:
        ctrl.matrix_world = R @ base_root
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        expected_root = R @ base_root
        out["root_matches_expected"] = max(
            abs(float(ctrl.matrix_world[i][j] - expected_root[i][j]))
            for i in range(4) for j in range(4)) <= EXACT
        rigid = {}
        for n in TARGETS + list(PARTS):
            exp = R @ base_mats[n]
            rigid[n] = max(abs(float(bpy.data.objects[n].matrix_world[i][j] - exp[i][j]))
                           for i in range(4) for j in range(4))
        out["rigid_world_matrix_maxdiff"] = rigid
        out["rigid_world_matrix_maxdiff_overall"] = max(rigid.values())
        cong = {}
        for n in names:
            ev = eval_world(bpy.data.objects[n], dg)
            expected_pts = base_eval[n]["pts"] @ R3.T
            cong[n] = {"counts_equal": (ev["nv"], ev["nt"]) ==
                       (base_eval[n]["nv"], base_eval[n]["nt"]),
                       "transformed_vertex_maxdiff_m":
                       float(np.max(np.abs(ev["pts"] - expected_pts)))
                       if ev["pts"].shape == expected_pts.shape else None,
                       "world_bidir_max_m": kd_bidir(ev["pts"], expected_pts)}
        out["congruence"] = cong
        out["root_controls_local_points_unchanged"] = {
            n: [tuple(bp.co) for bp in bpy.data.objects[n].data.splines[0].bezier_points]
               == base_points[n] for n in PARTS}
        ref = bpy.data.objects["CF_Ref_Plane"]
        ref_ev = eval_world(ref, dg)
        out["reference"] = {
            "matrix_maxdiff": max(abs(float(ref.matrix_world[i][j] -
                                            base_ref_mat[i][j]))
                                  for i in range(4) for j in range(4)),
            "eval_bidir_max_m": kd_bidir(ref_ev["pts"], base_ref["pts"])}
        tree = bvh_body(eval_world(bpy.data.objects["CF_Body_A"], dg))
        anchors = {n: bpy.data.objects[n].data.splines[0].bezier_points[0].co
                   for n in PARTS}
        out["attachment_anchor_to_body_mm_after"] = {
            n: 1000 * tree.find_nearest(bpy.data.objects[n].matrix_world @ co)[3]
            for n, co in anchors.items()}
        out["visibility_unchanged"] = all(
            visibility(o) == base_vis[o.name] for o in bpy.data.objects)
    finally:
        ctrl.matrix_world = base_root
        bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    out["restore"] = {
        "root_matrix_maxdiff": max(abs(float(ctrl.matrix_world[i][j] - base_root[i][j]))
                                   for i in range(4) for j in range(4)),
        "child_world_maxdiff": max(
            max(abs(float(bpy.data.objects[n].matrix_world[i][j] -
                          base_mats[n][i][j])) for i in range(4) for j in range(4))
            for n in TARGETS + list(PARTS)),
        "part_eval_bidir_max_m": max(
            kd_bidir(eval_world(bpy.data.objects[n], dg)["pts"], base_eval[n]["pts"])
            for n in PARTS),
        "reference_matrix_maxdiff": max(
            abs(float(bpy.data.objects["CF_Ref_Plane"].matrix_world[i][j] -
                      base_ref_mat[i][j])) for i in range(4) for j in range(4)),
        "reference_eval_bidir_max_m": kd_bidir(
            eval_world(bpy.data.objects["CF_Ref_Plane"], dg)["pts"], base_ref["pts"]),
        "visibility_unchanged": all(visibility(o) == base_vis[o.name]
                                    for o in bpy.data.objects),
        "path_points_unchanged": all(
            [tuple(bp.co) for bp in bpy.data.objects[n].data.splines[0].bezier_points]
            == base_points[n] for n in PARTS),
    }
    out["checks"] = {
        "root_rotated_90": out["root_matches_expected"],
        "rigid_transforms": out["rigid_world_matrix_maxdiff_overall"] <= TOL,
        "attachment_congruence": all(v["world_bidir_max_m"] <= TOL
                                     for v in out["congruence"].values()),
        "reference_fixed": (out["reference"]["matrix_maxdiff"] <= EXACT and
                            out["reference"]["eval_bidir_max_m"] <= TOL),
        "controls_follow_root": all(out["root_controls_local_points_unchanged"].values()),
        "root_restored_exactly": out["restore"]["root_matrix_maxdiff"] <= EXACT,
        "children_restored": out["restore"]["child_world_maxdiff"] <= TOL,
        "parts_restored": out["restore"]["part_eval_bidir_max_m"] <= TOL,
        "reference_restored": out["restore"]["reference_matrix_maxdiff"] <= EXACT,
        "visibility_restored": out["restore"]["visibility_unchanged"],
    }
    return out


def evidence():
    if not BLOCKOUT.exists():
        raise SystemExit("BLOCKED: blockout checkpoint missing")
    ctrl = bpy.data.objects[ROOT]
    dg = bpy.context.evaluated_depsgraph_get()
    a_before = eval_world(bpy.data.objects["CF_Body_A"], dg)
    mats_before = {n: bpy.data.objects[n].matrix_world.copy() for n in TARGETS}
    vis_before = {n: visibility(bpy.data.objects[n]) for n in TARGETS}
    ref_mat_before = bpy.data.objects["CF_Ref_Plane"].matrix_world.copy()
    ref_eval_before = eval_world(bpy.data.objects["CF_Ref_Plane"], dg)
    root_before = ctrl.matrix_world.copy()

    rt = root_test(ctrl)

    side = ASSET / "side_before_body_only.png"
    full = ASSET / "side_after_assembly.png"
    threeq = ASSET / "assembly_threequarter.png"
    refonly = ASSET / "reference_only_verify.png"
    overlay_path = ASSET / "assembly_side_alpha_overlay.png"
    body_only = render_view(side, "CF_Cam_Side", (402, 327), True, False, False, True)
    full_rgba = render_view(full, "CF_Cam_Side", (402, 327), True, True, False, True)
    threeq_rgba = render_view(threeq, "CF_Cam_ThreeQuarter", (512, 512),
                              True, True, False, True)
    render_view(refonly, "CF_Cam_Side", (402, 327), False, False, True, False)
    B.save_rgba(ASSET / "side_before_body_only_neutral.png", B.neutral_composite(body_only))
    B.save_rgba(ASSET / "side_after_assembly_neutral.png", B.neutral_composite(full_rgba))
    B.save_rgba(ASSET / "assembly_threequarter_neutral.png", B.neutral_composite(threeq_rgba))
    reference = B.load_rgba(REF)
    B.save_rgba(overlay_path, contour_overlay(reference, full_rgba[:, :, 3]))

    dg = bpy.context.evaluated_depsgraph_get()
    a_after = eval_world(bpy.data.objects["CF_Body_A"], dg)
    mats_after = {n: bpy.data.objects[n].matrix_world.copy() for n in TARGETS}
    ref_eval_after = eval_world(bpy.data.objects["CF_Ref_Plane"], dg)
    metrics = {n: {k: v for k, v in eval_world(bpy.data.objects[n], dg).items()
                   if k not in ("pts", "tri")} for n in PARTS}
    tree = bvh_body(a_after)
    for n in PARTS:
        metrics[n]["min_vertex_to_body_mm"] = round(1000 * min(
            tree.find_nearest(Vector((float(p[0]), float(p[1]), float(p[2]))))[3]
            for p in eval_world(bpy.data.objects[n], dg)["pts"]), 4)
    checks = {
        "A_source_and_eval_unchanged": (kd_bidir(a_after["pts"], a_before["pts"]) <= TOL
                                        and a_after["nt"] == a_before["nt"]),
        "protected_transforms_unchanged": all(
            max(abs(float(mats_after[n][i][j] - mats_before[n][i][j]))
                for i in range(4) for j in range(4)) <= EXACT for n in TARGETS),
        "reference_unchanged": (max(abs(float(
            bpy.data.objects["CF_Ref_Plane"].matrix_world[i][j] - ref_mat_before[i][j]))
            for i in range(4) for j in range(4)) <= EXACT and
            kd_bidir(ref_eval_after["pts"], ref_eval_before["pts"]) <= TOL),
        "root_restored": max(abs(float(ctrl.matrix_world[i][j] - root_before[i][j]))
                             for i in range(4) for j in range(4)) <= EXACT,
        "parts_finite": all(m["finite"] for m in metrics.values()),
        "parts_no_zero_area": all(m["zero_area_tris"] == 0 for m in metrics.values()),
        "parts_no_loose": all(m["loose_verts"] == 0 for m in metrics.values()),
        "parts_contact_body": all(m["min_vertex_to_body_mm"] <= 0.5
                                  for m in metrics.values()),
        "A_render_visible": not bpy.data.objects["CF_Body_A"].hide_render,
        "B_C_render_hidden": all(bpy.data.objects["CF_Body_" + k].hide_render
                                 for k in "BC"),
        "reference_visible_locked_render_hidden": (
            not bpy.data.objects["CF_Ref_Plane"].hide_viewport and
            bpy.data.objects["CF_Ref_Plane"].hide_render and
            bpy.data.objects["CF_Ref_Plane"].hide_select and
            all(all(v) for v in locks(bpy.data.objects["CF_Ref_Plane"]).values())),
    }
    bpy.ops.wm.save_as_mainfile(filepath=str(BLOCKOUT), check_existing=False, copy=False)
    proof = {
        "stage": "assembly_blockout_01_evidence",
        "baseline": str(BASELINE), "baseline_sha256": sha256_file(BASELINE),
        "checkpoint": str(BLOCKOUT), "checkpoint_sha256": sha256_file(BLOCKOUT),
        "root": {"matrix_world": mat_list(ctrl.matrix_world),
                 "euler_deg": [math.degrees(float(v)) for v in ctrl.rotation_euler],
                 "children": sorted(o.name for o in ctrl.children)},
        "parts": {n: {
            "parent": bpy.data.objects[n].parent.name if bpy.data.objects[n].parent else None,
            "type": bpy.data.objects[n].type,
            "points_local_m": [list(bp.co) for bp in
                               bpy.data.objects[n].data.splines[0].bezier_points],
            "radii_mm": [1000 * bp.radius for bp in
                         bpy.data.objects[n].data.splines[0].bezier_points],
            "reference_px": json.loads(bpy.data.objects[n]["reference_px"]),
            "construction": bpy.data.objects[n]["construction"],
            "depth_note": bpy.data.objects[n]["depth_note"],
        } for n in PARTS},
        "metrics": metrics,
        "checks": checks,
        "root_rotation_test": rt,
        "reference": {"object": "CF_Ref_Plane",
                      "path": str(REF), "sha256": sha256_file(REF)},
        "captures": {p.name: sha256_file(p) for p in
                     (side, full, threeq, refonly, overlay_path,
                      ASSET / "side_before_body_only_neutral.png",
                      ASSET / "side_after_assembly_neutral.png",
                      ASSET / "assembly_threequarter_neutral.png")},
        "visibility": {n: visibility(bpy.data.objects[n]) for n in
                       ("CF_Body_A", "CF_Body_B", "CF_Body_C", "CF_Ref_Plane")},
        "live": {"filepath": bpy.data.filepath, "dirty": bool(bpy.data.is_dirty)},
        "limitations": [
            "one stylized elevated side reference; hidden depth/cross-sections inferred "
            "as circular sections on the X=0 median plane",
            "root rotation test is a diagnostic, not an approved reposing",
            "curves are editable sweeps; evaluated triangles are not final topology",
            "intentional body penetration at attachment roots; no shell, bore, "
            "sprinkling holes, union or thickness",
            "B/C are hidden not deleted; A opening and cutter pose unchanged",
        ],
    }
    with open(PROOF, "w", encoding="utf-8") as fh:
        json.dump(proof, fh, indent=2, sort_keys=True)
    print("ASSEMBLY_EVIDENCE " + json.dumps({
        "proof": str(PROOF), "checkpoint": str(BLOCKOUT),
        "sha256": proof["checkpoint_sha256"], "checks": checks,
        "root_rotation_checks": rt["checks"],
        "root_rotation_restore": rt["restore"],
        "metrics": metrics, "live": proof["live"],
        "captures": proof["captures"],
    }, sort_keys=True))
    return proof


if __name__ == "__main__":
    stage = sys.argv[-1] if sys.argv[-1] in ("baseline", "build", "evidence") else "baseline"
    try:
        {"baseline": baseline, "build": build, "evidence": evidence}[stage]()
    except Exception:
        traceback.print_exc()
        raise
