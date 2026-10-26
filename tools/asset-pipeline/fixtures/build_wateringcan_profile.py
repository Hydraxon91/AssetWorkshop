"""Bounded reference-led exterior profile study for the watering-can body.

This is a stage script, not a finished asset generator. It builds one corrected
side-view reference plane from the shared ReferenceFrame calibration, a manual
visible-contour trace, a small number of Screw/Subsurf/Boolean profile candidates,
matched contour overlays, a live-edit proof and a new-name review checkpoint.

Run through Blender's Python with a stage name:
    run("reference")       # reference plane, trace, frame proof, records
    run("candidates")      # up to four low-control-count profile candidates
    run("editability", "A")# move one profile control, capture, restore
    run("save", "A")       # final visibility, save exterior_review_01.blend

No destination integration, UVs, materials delivery, inner shell or attachments.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

BASE = Path("/Users/hydraxon/Documents/GitHub/AssetWorkshop")
TOOLS = BASE / "tools" / "asset-pipeline" / "scripts"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from reference_compare import ReferenceFrame, contour_overlay  # noqa: E402

OUT = BASE / ".dev-shots" / "asset-pipeline" / "wateringcan_v2" / "curve_fit_01"
REF = (BASE / ".dev-shots" / "asset-pipeline" / "wateringcan_body_trial" /
       "reference" / "derived" / "plane_profile.png")
BASELINE = BASE / ".dev-shots" / "asset-pipeline" / "wateringcan_v2" / "wateringcan_v2_14.blend"
REVIEW = OUT / "exterior_review_01.blend"
PLANE_OFFSET_X_MM = -600.0
W, H = 402, 327
ORIGIN_PX = (220, 315)
TOP_PX = (226, 44)
BASE_PX = (226, 315)
HEIGHT_MM = 298.0
MM_PER_PX = HEIGHT_MM / (BASE_PX[1] - TOP_PX[1])  # 298 / 271
FRAME = ReferenceFrame(W, H, ORIGIN_PX, MM_PER_PX, "side")

# 12 meaningful profile controls, (radius_mm, z_mm), bottom-open to top-open.
BASE_PROFILE = [
    (44.0, 0.0),
    (60.0, 4.0),
    (84.0, 16.0),
    (105.0, 48.0),
    (112.0, 85.0),
    (113.0, 125.0),
    (109.0, 165.0),
    (100.0, 202.0),
    (86.0, 235.0),
    (68.0, 260.0),
    (48.0, 282.0),
    (28.0, 310.0),
]

# Visible contour trace, top-left image pixels. Uncertain intervals are separate.
VISIBLE_SEGMENTS = {
    "left_upper": [(226, 44), (219, 45), (212, 47), (204, 50), (196, 53),
                   (188, 56), (180, 60), (172, 65), (164, 71), (157, 77),
                   (150, 84), (144, 92), (139, 100), (134, 109), (130, 120),
                   (128, 130)],
    "left_lower": [(127, 240), (122, 250), (121, 260), (124, 272), (130, 282),
                   (140, 292), (153, 301), (170, 309), (190, 314), (210, 315),
                   (220, 315)],
    "right_upper": [(226, 44), (234, 46), (244, 50), (255, 56), (265, 62),
                    (275, 69), (285, 77), (293, 84)],
    "right_lower": [(315, 248), (317, 258), (315, 270), (309, 282), (300, 292),
                    (289, 301), (276, 308), (260, 313), (240, 315), (220, 315)],
}
UNCERTAIN_SEGMENTS = {
    "left_spout_overlap": [(128, 130), (134, 150), (136, 170), (137, 190),
                           (137, 207), (132, 225), (127, 240)],
    "right_handle_overlap": [(293, 84), (300, 100), (305, 130), (310, 160),
                             (313, 190), (314, 220), (315, 248)],
    "top_rim_visual": [(195, 72), (204, 61), (220, 57), (238, 58), (254, 62),
                       (269, 70), (277, 80), (272, 84), (256, 79), (238, 75),
                       (220, 77), (204, 82), (195, 72)],
}
METRIC_SEGMENTS = ("left_upper", "left_lower", "right_upper", "right_lower")

CANDIDATE_DEFS = {
    "A": {"profile": "base", "cut_ax_deg": 0.0, "cut_ay_deg": -12.0,
          "z0_mm": 286.0,
          "note": "Traced profile, simple tilted top cut; 12 controls."},
    "B": {"profile": "base", "cut_ax_deg": 6.0, "cut_ay_deg": -18.0,
          "z0_mm": 283.0,
          "note": "Traced profile, compound tilted cut testing an offset opening hypothesis."},
    "C": {"profile": "fuller_shoulder", "cut_ax_deg": 0.0, "cut_ay_deg": -12.0,
          "z0_mm": 285.0,
          "note": "Fuller shoulder +4 mm at z=202..282, same simple tilted cut." },
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n")


def get_collection(name, parent=None):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(collection)
    return collection


def new_object(name, data, collection):
    if bpy.data.objects.get(name) is not None:
        raise RuntimeError(f"refusing to replace existing object {name}")
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    return obj


def load_rgba(path):
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        width, height = map(int, image.size)
        pixels = np.empty(width * height * 4, dtype=np.float32)
        image.pixels.foreach_get(pixels)
        return pixels.reshape(height, width, 4).copy()
    finally:
        bpy.data.images.remove(image)


def save_rgba(path, array):
    path = Path(path)
    height, width = array.shape[:2]
    image = bpy.data.images.new(path.stem, width=width, height=height, alpha=True)
    try:
        image.colorspace_settings.name = "sRGB"
        image.pixels.foreach_set(np.ascontiguousarray(array, dtype=np.float32).ravel())
        image.filepath_raw = str(path)
        image.file_format = "PNG"
        image.save()
    finally:
        bpy.data.images.remove(image)


def draw_polyline(array, points, color, thickness=2):
    height = array.shape[0]
    for (u0, v0), (u1, v1) in zip(points[:-1], points[1:]):
        x0, y0 = float(u0), height - 1 - float(v0)
        x1, y1 = float(u1), height - 1 - float(v1)
        steps = max(2, int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1)
        for step in range(steps + 1):
            t = step / steps
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            ix, iy = int(round(x)), int(round(y))
            for dy in range(-thickness, thickness + 1):
                for dx in range(-thickness, thickness + 1):
                    if dx * dx + dy * dy <= thickness * thickness + 1:
                        xx, yy = ix + dx, iy + dy
                        if 0 <= xx < array.shape[1] and 0 <= yy < height:
                            array[yy, xx, :3] = color
                            array[yy, xx, 3] = 1.0


def mesh_hash(mesh):
    h = hashlib.sha256()
    for vertex in mesh.vertices:
        h.update(struct.pack("<3f", *vertex.co))
    for polygon in mesh.polygons:
        h.update(struct.pack("<i", len(polygon.vertices)))
        for index in polygon.vertices:
            h.update(struct.pack("<i", int(index)))
    return h.hexdigest()


def visibility(obj):
    return {
        "name": obj.name,
        "hide_viewport": bool(obj.hide_viewport),
        "hide_render": bool(obj.hide_render),
        "hide_get": bool(obj.hide_get()),
    }


def hide_for_review(obj, viewport=True, render=True):
    obj.hide_set(bool(viewport))
    obj.hide_viewport = False
    obj.hide_render = bool(render)


# ---------------------------------------------------------------------------
# Reference stage
# ---------------------------------------------------------------------------

def build_reference_plane(ref_coll, deriv_coll):
    geometry = FRAME.geometry()
    FRAME.validate_plane_size(geometry["width_mm"], geometry["height_mm"])
    corners = [[coordinate / 1000.0 for coordinate in corner]
               for corner in geometry["corners_mm"]]
    mesh = bpy.data.meshes.new("CF_RefMesh")
    mesh.from_pydata(corners, [], [tuple(geometry["face_order"])])
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for loop_index, vertex_index in enumerate(geometry["face_order"]):
        uv_layer.data[loop_index].uv = geometry["uv"][vertex_index]

    image = bpy.data.images.load(str(REF), check_existing=False)
    image.name = "CF_RefImage"
    image.colorspace_settings.name = "sRGB"
    image.pack()

    material = bpy.data.materials.new("CF_RefMaterial")
    material.use_nodes = True
    material.use_backface_culling = False
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    texture = nodes.new("ShaderNodeTexImage")
    texture.name = "Reference Image"
    texture.image = image
    texture.extension = "CLIP"
    texture.interpolation = "Linear"
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1.0
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(texture.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])

    obj = new_object("CF_Ref_Plane", mesh, ref_coll)
    obj.location = (PLANE_OFFSET_X_MM / 1000.0, 0.0, 0.0)
    obj.data.materials.append(material)
    obj.show_in_front = True
    obj.hide_render = True
    obj.display_type = "TEXTURED"
    obj.lock_location = (True, True, True)
    obj.lock_rotation = (True, True, True)
    obj.lock_scale = (True, True, True)
    obj["reference_projection"] = "side"
    obj["reference_mm_per_px"] = MM_PER_PX
    obj["reference_width_mm"] = geometry["width_mm"]
    obj["reference_height_mm"] = geometry["height_mm"]
    obj["reference_origin_px"] = list(ORIGIN_PX)
    obj["reference_source"] = str(REF.relative_to(BASE))
    obj["reference_sha256"] = sha256_file(REF)
    return obj, image, material


def trace_world_points(points):
    result = []
    for u, v in points:
        world = FRAME.pixel_to_world_mm(u, v)
        result.append((world[0] - 0.6, world[1] / 1000.0,
                       world[2] / 1000.0, 1.0))
    return result


def build_trace_curve(name, segments, color, collection):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = 0.00035
    curve.bevel_resolution = 2
    for label, points in segments.items():
        spline = curve.splines.new("POLY")
        world_points = trace_world_points(points)
        spline.points.add(len(world_points) - 1)
        for point, coordinate in zip(spline.points, world_points):
            point.co = coordinate
    material = bpy.data.materials.new(name + "_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 3.0
    emission.inputs["Color"].default_value = (*color, 1.0)
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    curve.materials.append(material)
    obj = new_object(name, curve, collection)
    obj.show_in_front = True
    obj.hide_render = True
    obj["trace_labels"] = ", ".join(segments.keys())
    return obj


def build_camera(collection):
    spec = FRAME.camera_spec_mm(1000.0)
    data = bpy.data.cameras.new("CF_Cam_Side_Data")
    data.type = "ORTHO"
    data.ortho_scale = spec["ortho_scale_mm"] / 1000.0
    data.sensor_fit = "HORIZONTAL"
    data.clip_start = 0.001
    data.clip_end = 10.0
    camera = new_object("CF_Cam_Side", data, collection)
    position = Vector(spec["position_mm"]) / 1000.0
    right = Vector((0.0, -1.0, 0.0))
    up = Vector((0.0, 0.0, 1.0))
    back = Vector((-1.0, 0.0, 0.0))
    rotation = Matrix((right, up, back)).transposed().to_4x4()
    camera.matrix_world = Matrix.Translation(position) @ rotation
    camera["camera_spec_mm"] = json.dumps(spec)
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.resolution_x = W
    scene.render.resolution_y = H
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = 1.0
    return camera, spec


def frame_proof(camera, spec):
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    landmarks = [(220, 315), (226, 44), (138, 100), (300, 80), (180, 280),
                 (260, 300), (195, 58), (317, 252)]
    rows = []
    for u, v in landmarks:
        point = FRAME.pixel_to_world_mm(u, v)
        world = Vector(((point[0] + PLANE_OFFSET_X_MM) / 1000.0,
                        point[1] / 1000.0, point[2] / 1000.0))
        projected = world_to_camera_view(scene, camera, world)
        px = projected.x * W
        py = (1.0 - projected.y) * H
        error = math.hypot(px - u, py - v)
        rows.append({"image_px": [u, v], "projected_px": [px, py],
                     "error_px": error, "world_mm": [point[0],
                                                     point[1], point[2]]})
    max_error = max(row["error_px"] for row in rows)
    return {"resolution": [W, H], "camera_spec_mm": spec,
            "plane_offset_x_mm": PLANE_OFFSET_X_MM,
            "landmarks": rows, "max_error_px": max_error}


def render_reference_only(plane, path):
    scene = bpy.context.scene
    old_transparent = scene.render.film_transparent
    old_hidden = plane.hide_render
    try:
        plane.hide_render = False
        scene.render.film_transparent = False
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
    finally:
        plane.hide_render = old_hidden
        scene.render.film_transparent = old_transparent
    rendered = load_rgba(path)
    source = load_rgba(REF)
    diff = np.abs(rendered[:, :, :3] - source[:, :, :3])
    return {"path": str(path), "mean_abs_rgb_diff": float(diff.mean()),
            "max_abs_rgb_diff": float(diff.max())}


def make_trace_overlay():
    source = load_rgba(REF)
    overlay = source.copy()
    for points in VISIBLE_SEGMENTS.values():
        draw_polyline(overlay, points, (0.02, 0.85, 0.20), thickness=2)
    for points in UNCERTAIN_SEGMENTS.values():
        draw_polyline(overlay, points, (1.0, 0.55, 0.0), thickness=1)
    path = OUT / "trace" / "trace_overlay.png"
    save_rgba(path, overlay)
    return path


def trace_record():
    return {
        "visible_segments": {
            key: [{"u": u, "v": v,
                   "z_mm": (ORIGIN_PX[1] - v) * MM_PER_PX,
                   "radius_mm": abs(u - ORIGIN_PX[0]) * MM_PER_PX}
                  for u, v in points]
            for key, points in VISIBLE_SEGMENTS.items()
        },
        "uncertain_segments": {
            key: [{"u": u, "v": v} for u, v in points]
            for key, points in UNCERTAIN_SEGMENTS.items()
        },
        "occluded_intervals": {
            "left_spout_overlap": {"v_range": [130, 240],
                                   "reason": "spout body/shading overlaps the body edge"},
            "right_handle_overlap": {"v_range": [84, 248],
                                     "reason": "handle and attachments overlap the body edge"},
            "top_rim_lip": {"v_range": [44, 84],
                            "reason": "visible rim lip / recessed opening; simplified in this pass"},
        },
    }


def reference_stage():
    scene = bpy.context.scene
    OUT.mkdir(parents=True, exist_ok=True)
    ref_coll = get_collection("CF_Reference")
    profile_coll = get_collection("CF_Profiles")
    deriv_coll = get_collection("CF_Derivation")
    cand_coll = get_collection("CF_Candidates")
    if bpy.data.objects.get("CF_Ref_Plane"):
        raise RuntimeError("reference stage already present; refusing duplicate")

    baseline_hashes = {
        "wateringcan_v2_14.blend": sha256_file(BASELINE),
        "Body_v2_mesh": mesh_hash(bpy.data.objects["Body_v2"].data),
        "Ref_side_v2_mesh": mesh_hash(bpy.data.objects["Ref_side_v2"].data),
    }
    baseline_vis = {
        "Body_v2": visibility(bpy.data.objects["Body_v2"]),
        "Ref_side_v2": visibility(bpy.data.objects["Ref_side_v2"]),
        "Reference_collection": {
            "name": "Reference",
            "hide_viewport": bool(bpy.data.collections["Reference"].hide_viewport),
            "hide_render": bool(bpy.data.collections["Reference"].hide_render),
        },
    }

    plane, image, material = build_reference_plane(ref_coll, deriv_coll)
    visible_curve = build_trace_curve("CF_Trace_Visible", VISIBLE_SEGMENTS,
                                      (0.02, 0.85, 0.20), ref_coll)
    uncertain_curve = build_trace_curve("CF_Trace_Uncertain", UNCERTAIN_SEGMENTS,
                                        (1.0, 0.55, 0.0), ref_coll)
    camera, spec = build_camera(deriv_coll)
    proof = frame_proof(camera, spec)
    if proof["max_error_px"] > 1.0:
        raise RuntimeError(f"frame proof failed: {proof['max_error_px']:.6f}px")
    reference_capture = render_reference_only(
        plane, OUT / "evidence" / "frame_proof_reference_only.png")
    trace_png = make_trace_overlay()

    source_hash = sha256_file(REF)
    record = {
        "schema": "wateringcan-profile-reference/v1",
        "asset": "wateringcan_v2/curve_fit_01",
        "stage": "exterior body only; not a finished shell",
        "source": {
            "relative_path": str(REF.relative_to(BASE)),
            "sha256": source_hash,
            "width": W,
            "height": H,
            "kind": "derived stylized elevated side-view crop",
        },
        "crop_rect": [0, 0, W, H],
        "projection": "side",
        "frame": {
            "width": W, "height": H, "origin_px": list(ORIGIN_PX),
            "mm_per_px": MM_PER_PX, "projection": "side",
            "image_right_axis": "-Y", "image_up_axis": "+Z",
            "camera_axis": "-X",
            "plane_offset_x_mm": PLANE_OFFSET_X_MM,
            "plane_width_mm": FRAME.geometry()["width_mm"],
            "plane_height_mm": FRAME.geometry()["height_mm"],
        },
        "calibration": {
            "p1_base_px": list(BASE_PX), "p2_top_px": list(TOP_PX),
            "distance_mm": HEIGHT_MM,
            "distance_px": BASE_PX[1] - TOP_PX[1],
            "mm_per_px": MM_PER_PX,
            "direction_deg": math.degrees(math.atan2(
                TOP_PX[1] - BASE_PX[1], TOP_PX[0] - BASE_PX[0])),
            "scale_anchor": "overall visible body height, base bottom to highest body point",
            "landmark_uncertainty_px": 2.0,
            "landmark_uncertainty_mm": 2.0 * MM_PER_PX,
            "approx_height_error_mm": 2.0 * MM_PER_PX,
        },
        "body_centre_axis_u_px": ORIGIN_PX[0],
        "camera_spec_mm": spec,
        "projection_limits": [
            "single stylized/elevated side view; not a true orthographic view",
            "no hidden depth, circularity or exact bore is certified",
            "width, base, shoulder and opening proportions are provisional",
            "the source has a visible rim lip and recessed opening that this exterior-only pass simplifies",
            "height is a scale anchor; all other dimensions are reference-led estimates",
        ],
        "uncertainty": {
            "height_anchor_mm": 2.2,
            "body_width_mm": 4.5,
            "base_width_mm": 4.5,
            "opening_width_mm": 6.0,
            "top_shoulder_shape": "highest uncertainty; stylized elevation and rim lip",
            "attachment_occlusion": "left spout interval and right handle interval excluded from contour ranking",
        },
        "trace": trace_record(),
        "assumptions": [
            "The body is treated as a surface of revolution about the vertical axis at u=220.",
            "The height anchor is the highest visible body outline, not the handle or spout.",
            "The very bright highlights, text and background grid are ignored.",
            "The opening is represented by a simple tilted cut; no lip or bore is engineered.",
        ],
        "baseline": {"hashes": baseline_hashes, "visibility": baseline_vis},
        "evidence": {
            "frame_proof": str(OUT / "evidence" / "frame_proof.json"),
            "reference_only_capture": str(OUT / "evidence" /
                                          "frame_proof_reference_only.png"),
            "trace_overlay": str(trace_png),
            "trace_curves": [visible_curve.name, uncertain_curve.name],
        },
    }
    write_json(OUT / "reference_record.json", record)
    write_json(OUT / "evidence" / "frame_proof.json", proof)
    write_json(OUT / "evidence" / "baseline_protected_state.json",
               {"hashes": baseline_hashes, "visibility": baseline_vis})
    write_json(OUT / "evidence" / "reference_capture_check.json", reference_capture)
    summary = {
        "stage": "reference",
        "reference_record": str(OUT / "reference_record.json"),
        "frame_proof": str(OUT / "evidence" / "frame_proof.json"),
        "max_error_px": proof["max_error_px"],
        "reference_capture": reference_capture,
        "trace_overlay": str(trace_png),
        "plane_size_mm": [FRAME.geometry()["width_mm"],
                          FRAME.geometry()["height_mm"]],
        "mm_per_px": MM_PER_PX,
        "objects": [plane.name, visible_curve.name, uncertain_curve.name,
                    camera.name],
    }
    return summary


# ---------------------------------------------------------------------------
# Candidate stage
# ---------------------------------------------------------------------------

def clay_material():
    material = bpy.data.materials.get("CF_Clay")
    if material is not None:
        return material
    material = bpy.data.materials.new("CF_Clay")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    bsdf = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    base = bsdf.inputs.get("Base Color") or bsdf.inputs[0]
    rough = bsdf.inputs.get("Roughness") or bsdf.inputs[2]
    base.default_value = (0.52, 0.54, 0.60, 1.0)
    rough.default_value = 0.52
    return material


def make_cutter(name, ax_deg, ay_deg, z0_mm, collection):
    size = 2.0
    height = 2.0
    verts = [(-size / 2, -size / 2, 0.0), (size / 2, -size / 2, 0.0),
             (size / 2, size / 2, 0.0), (-size / 2, size / 2, 0.0),
             (-size / 2, -size / 2, height), (size / 2, -size / 2, height),
             (size / 2, size / 2, height), (-size / 2, size / 2, height)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = new_object(name, mesh, collection)
    normal = Matrix.Rotation(math.radians(ay_deg), 3, "Y") @ \
        Matrix.Rotation(math.radians(ax_deg), 3, "X") @ Vector((0.0, 0.0, 1.0))
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector(normal).to_track_quat("Z", "Y")
    obj.location = (0.0, 0.0, z0_mm / 1000.0)
    hide_for_review(obj, viewport=True, render=True)
    obj["cut_ax_deg"] = ax_deg
    obj["cut_ay_deg"] = ay_deg
    obj["cut_normal"] = list(normal)
    return obj


def eval_stats(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        matrix = evaluated.matrix_world
        coords = [matrix @ vertex.co for vertex in mesh.vertices]
        minimum = [min(c[i] for c in coords) for i in range(3)]
        maximum = [max(c[i] for c in coords) for i in range(3)]
        edge_use = [0] * len(mesh.edges)
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                edge_use[mesh.loops[loop_index].edge_index] += 1
        areas = [polygon.area for polygon in mesh.polygons]
        stats = {
            "verts": len(mesh.vertices),
            "faces": len(mesh.polygons),
            "tris": len(mesh.loop_triangles),
            "boundary_edges": sum(1 for count in edge_use if count == 1),
            "nonmanifold_edges": sum(1 for count in edge_use if count != 2),
            "ngons": sum(1 for polygon in mesh.polygons
                         if len(polygon.vertices) > 4),
            "degenerate_faces": sum(1 for area in areas if area < 1e-9),
            "min_face_area_mm2": min(areas) * 1e6 if areas else 0.0,
            "bbox_min_mm": [value * 1000.0 for value in minimum],
            "bbox_max_mm": [value * 1000.0 for value in maximum],
            "dimensions_mm": [(maximum[i] - minimum[i]) * 1000.0
                              for i in range(3)],
            "hash": mesh_hash(mesh),
        }
    finally:
        evaluated.to_mesh_clear()
    return stats


def apply_height(body, profile, cutter):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    # Place the minimum at z=0 by moving the control/body pair.
    bpy.context.view_layer.update()
    stats = eval_stats(body)
    lower = stats["bbox_min_mm"][2] / 1000.0
    body.location.z -= lower
    profile.location.z -= lower
    bpy.context.view_layer.update()
    # Shift the cut until the highest remaining point is 298 mm.
    for _ in range(6):
        depsgraph.update()
        bpy.context.view_layer.update()
        stats = eval_stats(body)
        top = stats["bbox_max_mm"][2] / 1000.0
        delta = 0.298 - top
        cutter.location.z += delta
        if abs(delta) < 1e-7:
            break
    bpy.context.view_layer.update()
    return eval_stats(body)


def make_candidate(key, definition, profile_coll, cand_coll, deriv_coll):
    controls = [list(pair) for pair in BASE_PROFILE]
    if definition["profile"] == "fuller_shoulder":
        for index in (7, 8, 9, 10):
            controls[index][0] += 4.0
    mesh = bpy.data.meshes.new(f"CF_ProfileMesh_{key}")
    vertices = [(radius / 1000.0, 0.0, z / 1000.0) for radius, z in controls]
    edges = [(index, index + 1) for index in range(len(vertices) - 1)]
    mesh.from_pydata(vertices, edges, [])
    mesh.update()
    mesh.materials.append(clay_material())

    profile = new_object(f"CF_Profile_{key}", mesh, profile_coll)
    profile.display_type = "WIRE"
    profile.show_in_front = True
    profile.hide_render = True
    profile.color = (0.0, 1.0, 0.0, 1.0)

    body = new_object(f"CF_Body_{key}", mesh, cand_coll)
    body.show_in_front = False
    screw = body.modifiers.new("CF_Screw", "SCREW")
    screw.axis = "Z"
    screw.angle = 2.0 * math.pi
    screw.steps = 40
    screw.render_steps = 40
    screw.use_merge_vertices = True
    screw.merge_threshold = 0.00001
    screw.use_smooth_shade = True
    subsurf = body.modifiers.new("CF_Subsurf", "SUBSURF")
    subsurf.subdivision_type = "CATMULL_CLARK"
    subsurf.levels = 1
    subsurf.render_levels = 1
    cutter = make_cutter(f"CF_Cutter_{key}", definition["cut_ax_deg"],
                         definition["cut_ay_deg"], definition["z0_mm"],
                         deriv_coll)
    boolean = body.modifiers.new("CF_Cut", "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.solver = "EXACT"
    boolean.object = cutter
    boolean.use_self = False
    bpy.context.view_layer.update()
    stats = apply_height(body, profile, cutter)
    return {"key": key, "definition": definition, "controls": controls,
            "profile": profile, "body": body, "cutter": cutter,
            "stats": stats}


def ensure_lights(deriv_coll):
    created = []
    if bpy.data.objects.get("CF_Sun_Key") is None:
        data = bpy.data.lights.new("CF_Sun_Key_Data", "SUN")
        data.energy = 3.0
        data.angle = math.radians(25)
        obj = new_object("CF_Sun_Key", data, deriv_coll)
        obj.rotation_euler = (math.radians(52), 0.0, math.radians(28))
        created.append(obj)
    if bpy.data.objects.get("CF_Sun_Fill") is None:
        data = bpy.data.lights.new("CF_Sun_Fill_Data", "SUN")
        data.energy = 1.3
        data.angle = math.radians(35)
        obj = new_object("CF_Sun_Fill", data, deriv_coll)
        obj.rotation_euler = (math.radians(65), 0.0, math.radians(-115))
        created.append(obj)
    return created


def render_candidate(body, other_bodies, plane, old_body, old_lights, path):
    scene = bpy.context.scene
    old_transparent = scene.render.film_transparent
    old_plane_hidden = plane.hide_render
    old_body_hidden = old_body.hide_render
    old_light_hidden = [light.hide_render for light in old_lights]
    old_candidate_hidden = {candidate.name: candidate.hide_render
                            for candidate in other_bodies}
    try:
        plane.hide_render = True
        old_body.hide_render = True
        for light in old_lights:
            light.hide_render = True
        for candidate in other_bodies:
            candidate.hide_render = True
        body.hide_render = False
        scene.render.film_transparent = True
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
    finally:
        plane.hide_render = old_plane_hidden
        old_body.hide_render = old_body_hidden
        for light, hidden in zip(old_lights, old_light_hidden):
            light.hide_render = hidden
        for candidate in other_bodies:
            candidate.hide_render = old_candidate_hidden[candidate.name]
        scene.render.film_transparent = old_transparent
    return load_rgba(path)


def mask_edge(alpha):
    mask = alpha > 0.5
    padded = np.pad(mask, 1)
    interior = (mask & padded[:-2, 1:-1] & padded[2:, 1:-1] &
                padded[1:-1, :-2] & padded[1:-1, 2:])
    edge = mask & ~interior
    ys, xs = np.nonzero(edge)
    return mask, edge, xs, ys


def contour_metrics(alpha):
    mask, edge, xs, ys = mask_edge(alpha)
    if mask.all() or not mask.any():
        raise RuntimeError("candidate alpha is empty or entirely full")
    points = []
    for segment in METRIC_SEGMENTS:
        for u, v in VISIBLE_SEGMENTS[segment]:
            x, y = float(u), float(H - 1 - v)
            distances = np.hypot(xs - x, ys - y)
            seconds, twos = float(distances.min()), float(np.partition(distances, 1)[1])
            points.append({"segment": segment, "u": u, "v": v,
                           "distance_px": seconds, "second_distance_px": twos})
    values = np.array([point["distance_px"] for point in points])
    return {
        "count": int(values.size),
        "mean_px": float(values.mean()),
        "median_px": float(np.median(values)),
        "rmse_px": float(np.sqrt(np.mean(values ** 2))),
        "max_px": float(values.max()),
        "within_2px": float(np.mean(values <= 2.0)),
        "within_4px": float(np.mean(values <= 4.0)),
        "points": points,
        "excluded": ["left_spout_overlap", "right_handle_overlap", "top_rim_visual"],
        "method": "nearest evaluated model alpha edge to manually traced visible contour; no threshold claimed",
    }


def neutral_composite(rgba, background=0.18):
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3:4]
    out = np.empty_like(rgba)
    out[:, :, :3] = rgb * alpha + background * (1.0 - alpha)
    out[:, :, 3] = 1.0
    return out


def update_trace_curve(obj, segments):
    curve = obj.data
    while len(curve.splines):
        curve.splines.remove(curve.splines[0])
    for label, points in segments.items():
        spline = curve.splines.new("POLY")
        world_points = trace_world_points(points)
        spline.points.add(len(world_points) - 1)
        for point, coordinate in zip(spline.points, world_points):
            point.co = coordinate
    obj["trace_labels"] = ", ".join(segments.keys())
    bpy.context.view_layer.update()


def retrace_stage():
    """Update the existing pass-owned trace data in place and re-rank saved alphas."""
    record_path = OUT / "reference_record.json"
    if not record_path.exists():
        raise RuntimeError("reference record missing; not restarting builder")
    visible = bpy.data.objects.get("CF_Trace_Visible")
    uncertain = bpy.data.objects.get("CF_Trace_Uncertain")
    if visible is None or uncertain is None:
        raise RuntimeError("pass-owned trace objects missing")
    update_trace_curve(visible, VISIBLE_SEGMENTS)
    update_trace_curve(uncertain, UNCERTAIN_SEGMENTS)
    trace_png = make_trace_overlay()

    record = json.loads(record_path.read_text())
    record["trace"] = trace_record()
    record["trace_revision"] = "corrected_manual_trace_02"
    record["trace_note"] = (
        "Upper-left and lower-left anchors corrected after zoom inspection; "
        "spout overlap now ends at v=240 and handle overlap at v=248. "
        "Uncertain intervals remain excluded from ranking.")
    record.setdefault("evidence", {})["trace_overlay"] = str(trace_png)
    write_json(record_path, record)

    metrics = {}
    for key in CANDIDATE_DEFS:
        render_path = OUT / "candidates" / f"render_{key}.png"
        if not render_path.exists():
            raise RuntimeError(f"missing saved alpha render {render_path}")
        raw = load_rgba(render_path)
        metrics[key] = contour_metrics(raw[:, :, 3])
    ranked = sorted(metrics, key=lambda key: (metrics[key]["median_px"],
                                              metrics[key]["mean_px"]))
    write_json(OUT / "candidates" / "candidate_metrics.json", metrics)
    comparison_path = OUT / "candidates" / "candidate_comparison.json"
    comparison = json.loads(comparison_path.read_text())
    comparison["metrics"] = metrics
    comparison["ranked_by_visible_contour"] = ranked
    comparison["trace_revision"] = "corrected_manual_trace_02"
    comparison["trace_note"] = record["trace_note"]
    write_json(comparison_path, comparison)
    write_json(OUT / "evidence" / "trace_revision.json", {
        "stage": "retrace",
        "trace_revision": "corrected_manual_trace_02",
        "trace_overlay": str(trace_png),
        "visible_segments": list(VISIBLE_SEGMENTS.keys()),
        "uncertain_segments": list(UNCERTAIN_SEGMENTS.keys()),
        "excluded_intervals": {
            "left_spout_overlap": [130, 240],
            "right_handle_overlap": [84, 248],
            "top_rim_lip": [44, 84],
        },
        "ranked_by_visible_contour": ranked,
        "metrics": metrics,
        "note": "Metrics recomputed from existing saved candidate alpha masks; no geometry rebuilt.",
    })
    return {
        "stage": "retrace",
        "trace_overlay": str(trace_png),
        "ranked_by_visible_contour": ranked,
        "metrics": {key: {name: value for name, value in metric.items()
                          if name != "points"}
                    for key, metric in metrics.items()},
        "trace_objects_updated_in_place": [visible.name, uncertain.name],
    }


def comparison_grid(panels):
    count = len(panels)
    canvas = np.ones((2 * H, count * W, 4), dtype=np.float32)
    for index, (overlay, neutral, color) in enumerate(panels):
        x0 = index * W
        canvas[0:H, x0:x0 + W] = neutral
        canvas[H:2 * H, x0:x0 + W] = overlay
        canvas[H - 7:H - 1, x0:x0 + W, :3] = color
    for index in range(1, count):
        canvas[:, index * W - 1:index * W + 1, :3] = 0.0
        canvas[:, index * W - 1:index * W + 1, 3] = 1.0
    return canvas


def candidate_stage():
    if not (OUT / "reference_record.json").exists():
        raise RuntimeError("run the reference stage first")
    scene = bpy.context.scene
    profile_coll = get_collection("CF_Profiles")
    cand_coll = get_collection("CF_Candidates")
    deriv_coll = get_collection("CF_Derivation")
    ref_coll = get_collection("CF_Reference")
    plane = bpy.data.objects["CF_Ref_Plane"]
    camera = bpy.data.objects["CF_Cam_Side"]
    scene.camera = camera
    clay_material()
    ensure_lights(deriv_coll)

    old_body = bpy.data.objects["Body_v2"]
    old_lights = [obj for obj in bpy.data.objects
                  if obj.type == "LIGHT" and obj.name in ("Light", "Sun_Overlay")]
    source = load_rgba(REF)
    candidates = []
    for key, definition in CANDIDATE_DEFS.items():
        if bpy.data.objects.get(f"CF_Body_{key}"):
            raise RuntimeError(f"candidate {key} already present")
        candidates.append(make_candidate(key, definition, profile_coll,
                                         cand_coll, deriv_coll))
    bodies = [candidate["body"] for candidate in candidates]

    evidence_dir = OUT / "candidates"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    panels = []
    metrics = {}
    for candidate in candidates:
        key = candidate["key"]
        raw = render_candidate(candidate["body"], bodies, plane, old_body,
                               old_lights, evidence_dir / f"render_{key}.png")
        alpha = raw[:, :, 3]
        overlay = contour_overlay(source, alpha)
        overlay_path = evidence_dir / f"overlay_{key}.png"
        neutral_path = evidence_dir / f"neutral_{key}.png"
        save_rgba(overlay_path, overlay)
        neutral = neutral_composite(raw)
        save_rgba(neutral_path, neutral)
        metric = contour_metrics(alpha)
        metrics[key] = metric
        candidate["metric"] = metric
        candidate["overlay_path"] = overlay_path
        candidate["neutral_path"] = neutral_path
        candidate["render_path"] = evidence_dir / f"render_{key}.png"
        write_json(evidence_dir / f"controls_{key}.json", {
            "key": key,
            "definition": candidate["definition"],
            "controls_r_z_mm": candidate["controls"],
            "cut": candidate["cutter"].name,
            "cut_ax_deg": candidate["definition"]["cut_ax_deg"],
            "cut_ay_deg": candidate["definition"]["cut_ay_deg"],
            "cut_z0_mm": candidate["cutter"].location.z * 1000.0,
            "profile_location_mm": [value * 1000.0 for value in
                                    candidate["profile"].location],
            "body_location_mm": [value * 1000.0 for value in
                                 candidate["body"].location],
            "stats": candidate["stats"],
        })
        color = {"A": np.array([0.1, 0.9, 0.2]),
                 "B": np.array([1.0, 0.55, 0.05]),
                 "C": np.array([0.85, 0.2, 0.2])}[key]
        panels.append((overlay, neutral, color))
    # Reference panel first.
    ref_neutral = source.copy()
    ref_neutral[:, :, 3] = 1.0
    panels.insert(0, (source.copy(), ref_neutral, np.array([0.15, 0.35, 1.0])))
    grid = comparison_grid(panels)
    grid_path = evidence_dir / "comparison_grid.png"
    save_rgba(grid_path, grid)

    ranked = sorted(metrics, key=lambda key: (metrics[key]["median_px"],
                                              metrics[key]["mean_px"]))
    summary = {
        "stage": "candidates",
        "grid": str(grid_path),
        "panel_order": ["reference"] + list(CANDIDATE_DEFS.keys()),
        "top_row": "green contour overlays",
        "bottom_row": "neutral silhouettes",
        "ranked_by_visible_contour": ranked,
        "metrics": metrics,
        "candidates": {
            candidate["key"]: {
                "controls": candidate["controls"],
                "stats": candidate["stats"],
                "overlay": str(candidate["overlay_path"]),
                "neutral": str(candidate["neutral_path"]),
                "definition": candidate["definition"],
            } for candidate in candidates
        },
        "notes": {
            "A": "Simple tilted top cut, symmetric lathe; top opening sits at the height anchor rather than a recessed lip.",
            "B": "Compound cut tests an offset/elevated opening hypothesis; same controls, different elevation/cut.",
            "C": "Tests shoulder fullness by +4 mm on four upper controls; same cut as A.",
            "uncertainty": "Spout and handle overlap intervals are excluded from ranking. Top rim lip and hidden depth remain uncertain.",
        },
    }
    write_json(evidence_dir / "candidate_metrics.json", metrics)
    write_json(evidence_dir / "candidate_comparison.json", summary)
    return summary


# ---------------------------------------------------------------------------
# Editability and save
# ---------------------------------------------------------------------------

def bounds_equal(first, second, tolerance=1e-7):
    """Compare vector-valued bounds; never subtract lists as if scalars."""
    return all(len(first[key]) == len(second[key]) == 3 and
               all(abs(a-b) < tolerance for a, b in zip(first[key], second[key]))
               for key in ("bbox_min_mm", "bbox_max_mm"))


def editability_stage(best="A"):
    body = bpy.data.objects.get(f"CF_Body_{best}")
    profile = bpy.data.objects.get(f"CF_Profile_{best}")
    if body is None or profile is None:
        raise RuntimeError(f"missing candidate {best}")
    mesh = body.data
    baseline_stats = eval_stats(body)
    control_index = 5  # widest belly control, z=125 mm
    old = tuple(mesh.vertices[control_index].co)
    if abs(old[0] * 1000.0 - 113.0) > 1e-4:
        # Choose the nearest control at the widest belly if the variant differs.
        control_index = min(range(len(mesh.vertices)),
                            key=lambda i: abs(mesh.vertices[i].co.z * 1000.0 - 125.0))
        old = tuple(mesh.vertices[control_index].co)
    new = (old[0] + 0.006, old[1], old[2])
    scene = bpy.context.scene
    plane = bpy.data.objects["CF_Ref_Plane"]
    old_body = bpy.data.objects["Body_v2"]
    old_lights = [obj for obj in bpy.data.objects
                  if obj.type == "LIGHT" and obj.name in ("Light", "Sun_Overlay")]
    bodies = [obj for obj in bpy.data.objects
              if obj.name.startswith("CF_Body_")]
    modified_path = OUT / "evidence" / "editability_modified.png"
    try:
        mesh.vertices[control_index].co = new
        mesh.update()
        bpy.context.view_layer.update()
        modified_stats = eval_stats(body)
        raw = render_candidate(body, bodies, plane, old_body, old_lights, modified_path)
        modified_neutral = neutral_composite(raw)
        save_rgba(modified_path, modified_neutral)
    finally:
        mesh.vertices[control_index].co = old
        mesh.update()
        bpy.context.view_layer.update()
    restored_stats = eval_stats(body)
    restored_path = OUT / "evidence" / "editability_restored.png"
    raw = render_candidate(body, bodies, plane, old_body, old_lights, restored_path)
    restored_neutral = neutral_composite(raw)
    save_rgba(restored_path, restored_neutral)

    baseline_path = OUT / "candidates" / f"neutral_{best}.png"
    baseline_png = load_rgba(baseline_path)
    comparison = np.ones((H, 3 * W, 4), dtype=np.float32)
    comparison[:, 0:W] = baseline_png
    comparison[:, W:2 * W] = modified_neutral
    comparison[:, 2 * W:3 * W] = restored_neutral
    comparison[:, W - 1:W + 1, :3] = 0.0
    comparison[:, 2 * W - 1:2 * W + 1, :3] = 0.0
    comparison_path = OUT / "evidence" / "editability_comparison.png"
    save_rgba(comparison_path, comparison)
    restored_hash_equal = restored_stats["hash"] == baseline_stats["hash"]
    delta_radius_mm = (modified_stats["bbox_max_mm"][1] -
                       baseline_stats["bbox_max_mm"][1])
    result = {
        "stage": "editability",
        "candidate": best,
        "control_index": control_index,
        "control_old_local_mm": [value * 1000.0 for value in old],
        "control_new_local_mm": [value * 1000.0 for value in new],
        "expected_change": "evaluated radial extent changes by about +6 mm",
        "baseline": baseline_stats,
        "modified": modified_stats,
        "restored": restored_stats,
        "modified_bbox_max_y_delta_mm": delta_radius_mm,
        "restored_hash_equal": restored_hash_equal,
        "restored_bbox_equal": bounds_equal(restored_stats, baseline_stats),
        "comparison": str(comparison_path),
        "baseline_image": str(baseline_path),
        "modified_image": str(modified_path),
        "restored_image": str(restored_path),
        "uncertainty": "The in-memory edit is proof of live derivation, not a shape proposal.",
    }
    if not restored_hash_equal:
        raise RuntimeError("restored evaluated mesh differs from baseline")
    write_json(OUT / "evidence" / "editability.json", result)
    return result


def threequarter_stage(best="C"):
    body = bpy.data.objects.get(f"CF_Body_{best}")
    if body is None:
        raise RuntimeError(f"missing candidate {best}")
    scene = bpy.context.scene
    deriv_coll = get_collection("CF_Derivation")
    camera = bpy.data.objects.get("CF_Cam_ThreeQuarter")
    if camera is None:
        data = bpy.data.cameras.new("CF_Cam_ThreeQuarter_Data")
        data.type = "PERSP"
        data.lens = 55.0
        data.sensor_fit = "AUTO"
        data.clip_start = 0.001
        data.clip_end = 10.0
        camera = new_object("CF_Cam_ThreeQuarter", data, deriv_coll)
        target = Vector((0.0, 0.0, 0.15))
        position = Vector((-0.55, -0.55, 0.42))
        camera.location = position
        camera.rotation_mode = "QUATERNION"
        camera.rotation_quaternion = (target - position).to_track_quat("-Z", "Y")
        camera["camera_role"] = "diagnostic 3/4 neutral review capture"
    old_camera = scene.camera
    old_resolution = (scene.render.resolution_x, scene.render.resolution_y)
    old_aspect = (scene.render.pixel_aspect_x, scene.render.pixel_aspect_y)
    plane = bpy.data.objects["CF_Ref_Plane"]
    old_body = bpy.data.objects["Body_v2"]
    old_lights = [obj for obj in bpy.data.objects
                  if obj.type == "LIGHT" and obj.name in ("Light", "Sun_Overlay")]
    bodies = [obj for obj in bpy.data.objects if obj.name.startswith("CF_Body_")]
    path = OUT / "evidence" / f"threequarter_{best}.png"
    try:
        scene.camera = camera
        scene.render.resolution_x = 512
        scene.render.resolution_y = 512
        scene.render.pixel_aspect_x = 1.0
        scene.render.pixel_aspect_y = 1.0
        raw = render_candidate(body, bodies, plane, old_body, old_lights, path)
        neutral = neutral_composite(raw, background=0.18)
        save_rgba(path, neutral)
    finally:
        scene.camera = old_camera
        scene.render.resolution_x, scene.render.resolution_y = old_resolution
        scene.render.pixel_aspect_x, scene.render.pixel_aspect_y = old_aspect
    result = {
        "stage": "threequarter",
        "candidate": best,
        "path": str(path),
        "camera": camera.name,
        "resolution": [512, 512],
        "note": "Diagnostic neutral 3/4; open bottom and simplified rim are expected.",
    }
    write_json(OUT / "evidence" / "threequarter.json", result)
    return result


def save_stage(best="A"):
    scene = bpy.context.scene
    if REVIEW.exists():
        raise RuntimeError(f"refusing to overwrite {REVIEW}")
    # Final review visibility: best candidate only; baseline and alternates hidden.
    for obj in bpy.data.objects:
        if obj.name.startswith("CF_Body_"):
            hide_for_review(obj, viewport=(obj.name != f"CF_Body_{best}"),
                            render=(obj.name != f"CF_Body_{best}"))
        elif obj.name.startswith("CF_Profile_"):
            hide_for_review(obj, viewport=True, render=True)
        elif obj.name.startswith("CF_Cutter_"):
            hide_for_review(obj, viewport=True, render=True)
    body = bpy.data.objects[f"CF_Body_{best}"]
    body.hide_render = False
    body.hide_set(False)
    old_body = bpy.data.objects["Body_v2"]
    old_body.hide_set(True)
    old_body.hide_render = True
    old_ref = bpy.data.objects.get("Ref_side_v2")
    if old_ref:
        old_ref.hide_set(True)
        old_ref.hide_render = True
    old_ref_coll = bpy.data.collections.get("Reference")
    if old_ref_coll:
        old_ref_coll.hide_viewport = True
    for name in ("Light", "Sun_Overlay"):
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_set(True)
            obj.hide_render = True
    plane = bpy.data.objects["CF_Ref_Plane"]
    plane.hide_set(False)
    plane.hide_render = True
    scene.camera = bpy.data.objects["CF_Cam_Side"]
    scene.render.resolution_x = W
    scene.render.resolution_y = H
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = 1.0
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    bpy.ops.wm.save_as_mainfile(filepath=str(REVIEW))
    saved_hash = sha256_file(REVIEW)
    protected = {
        "stage": "save",
        "saved_path": str(REVIEW),
        "saved_sha256": saved_hash,
        "live_filepath": bpy.data.filepath,
        "live_dirty_after_save": bool(bpy.data.is_dirty),
        "baseline_file_sha256": sha256_file(BASELINE),
        "Body_v2_mesh_sha256": mesh_hash(bpy.data.objects["Body_v2"].data),
        "Ref_side_v2_mesh_sha256": mesh_hash(bpy.data.objects["Ref_side_v2"].data),
        "baseline_visibility": {
            "Body_v2": visibility(bpy.data.objects["Body_v2"]),
            "Ref_side_v2": visibility(bpy.data.objects["Ref_side_v2"]),
        },
        "best_candidate": best,
        "candidate_visibility": {
            obj.name: visibility(obj) for obj in bpy.data.objects
            if obj.name.startswith("CF_Body_")},
        "reference_plane": visibility(plane),
        "collections": {collection.name: {
            "hide_viewport": bool(collection.hide_viewport),
            "hide_render": bool(collection.hide_render),
            "objects": [obj.name for obj in collection.objects]}
            for collection in bpy.data.collections},
        "body_stats": eval_stats(body),
        "notes": [
            "v2_14 and its Body_v2/Ref_side_v2 data are preserved; this is a new-name review checkpoint.",
            "Best candidate is the only visible body; alternates, profiles and cutters remain editable but hidden.",
            "The corrected reference plane is visible in the viewport and excluded from render.",
        ],
    }
    write_json(OUT / "evidence" / "protected_state.json", protected)
    write_json(OUT / "evidence" / "build_report.json", protected)
    return protected


def run(stage, best="A"):
    if stage == "reference":
        return reference_stage()
    if stage == "retrace":
        return retrace_stage()
    if stage == "candidates":
        return candidate_stage()
    if stage == "editability":
        return editability_stage(best)
    if stage == "save":
        return save_stage(best)
    raise ValueError(f"unknown stage {stage!r}")


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    print(json.dumps(run(arguments[0] if arguments else "reference",
                         arguments[1] if len(arguments) > 1 else "A"),
                     indent=2))
