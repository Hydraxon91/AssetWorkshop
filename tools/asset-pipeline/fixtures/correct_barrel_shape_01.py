"""One bounded shape correction from the owned barrel technical-01 checkpoint.

Loads only the owned technical checkpoint and the five allowlisted source images.
No texture generation, material-node editing, textured render, UV work, or
imports of any other barrel asset. Saves a new shape-review checkpoint.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[3]
TECH = ROOT / ".dev-shots" / "barrel-img2-01" / "barrel_img2_01_technical_01.blend"
OUT = ROOT / ".dev-shots" / "barrel-img2-01" / "shape-review-01"
SRC = ROOT / ".dev-shots" / "barrel-efficiency-01" / "evidence"
ALLOWED = {
    "front": SRC / "clay_source_front.png",
    "opposite": SRC / "clay_source_opposite.png",
    "three_quarter": SRC / "clay_source_three_quarter.png",
    "top": SRC / "clay_source_top.png",
    "textured_three_quarter": SRC / "textured_source_three_quarter.png",
}
PARTS = ["Barrel_Body", "Barrel_Lid", "Barrel_Hoop_Upper", "Barrel_Hoop_Center",
         "Barrel_Hoop_Lower", "Barrel_Rim_Top", "Barrel_Rim_Bottom"]
RADIAL_MESHES = PARTS + ["Barrel_Body_Profile", "Barrel_Body_Screw_Source"]
BBOX = {
    "front": (68, 80, 441, 430),
    "opposite": (67, 80, 442, 430),
    "top": (62, 62, 449, 450),
}
NEW_MAX_RADIUS = ((441 - 68) / (430 - 80)) * 0.5


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def image_for(key):
    names = [f"clay_source_{key}.png", f"textured_source_{key}.png"]
    for name in names:
        img = bpy.data.images.get(name)
        if img is not None:
            return img
    img = bpy.data.images.load(str(ALLOWED[key]), check_existing=False)
    img.pack()
    return img


def image_pixels(img):
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)


def save_generated_image(name, arr, filepath, colorspace="sRGB"):
    h, w = arr.shape[:2]
    img = bpy.data.images.new(name, width=w, height=h, alpha=False)
    img.colorspace_settings.name = colorspace
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = arr[:, :, :3]
    img.pixels.foreach_set(np.flipud(rgba).ravel())
    img.file_format = "PNG"
    img.filepath_raw = str(filepath)
    img.save()
    return img


def plane_mesh(name, image, s, dirv, upv, target, bbox):
    wpx, hpx = image.size
    W, H = wpx * s, hpx * s
    d = Vector(dirv).normalized()
    u = Vector(upv).normalized()
    right = (-d).cross(u).normalized()
    center = Vector(target) - d * 1.5
    corners = [center - right * W * 0.5 - u * H * 0.5,
               center + right * W * 0.5 - u * H * 0.5,
               center + right * W * 0.5 + u * H * 0.5,
               center - right * W * 0.5 + u * H * 0.5]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata([tuple(v) for v in corners], [], [(0, 1, 2, 3)])
    mesh.update()
    uv = mesh.uv_layers.new(name="UVMap")
    for loop, co in zip(uv.data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop.uv = co
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections["REFERENCE_Planes_SHAPE_01"].objects.link(obj)
    old_mat = bpy.data.materials.get("Ref_Plane_Front_Mat")
    if old_mat is None:
        raise RuntimeError("Existing reference material not found")
    obj.data.materials.append(old_mat)
    obj.lock_location = (True, True, True)
    obj.lock_rotation = (True, True, True)
    obj.lock_scale = (True, True, True)
    obj.hide_render = True
    obj["source_bbox_px"] = list(bbox)
    obj["reference_scale_uniform"] = s
    obj["pixels_per_normalized_unit"] = 1.0 / s
    obj["locked_reference"] = True
    return obj


def set_camera(obj, target, direction, ortho_scale):
    obj.data.type = "ORTHO"
    obj.data.ortho_scale = ortho_scale
    obj.location = Vector(target) + Vector(direction).normalized() * 3.0
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def project(scene, cam, p):
    c = world_to_camera_view(scene, cam, Vector(p))
    return [c.x * 512.0, (1.0 - c.y) * 512.0, c.z]


def main():
    if OUT.exists():
        if any(p.is_file() for p in OUT.rglob("*") if p.name != ".DS_Store"):
            raise RuntimeError("Refusing to overwrite non-empty shape-review-01")
    else:
        OUT.mkdir(parents=True, exist_ok=False)
    if Path(bpy.data.filepath).resolve() != TECH.resolve():
        raise RuntimeError("Expected owned technical checkpoint, got " + bpy.data.filepath)
    tech_hash_before = sha256(TECH)
    src_before = {k: sha256(v) for k, v in ALLOWED.items()}
    preflight = {
        "filepath": bpy.data.filepath,
        "objects": {},
        "root_matrix_world": None,
        "materials": [m.name for m in bpy.data.materials],
        "images": [{"name": i.name, "size": list(i.size), "packed": bool(i.packed_file)} for i in bpy.data.images],
    }
    root = bpy.data.objects.get("Barrel_Model_Control")
    if root is None:
        raise RuntimeError("Missing Barrel_Model_Control")
    preflight["root_matrix_world"] = [list(r) for r in root.matrix_world]
    for name in RADIAL_MESHES:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise RuntimeError("Missing " + name)
        preflight["objects"][name] = {
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "matrix_world": [list(r) for r in obj.matrix_world],
            "verts": len(obj.data.vertices) if obj.type == "MESH" else None,
            "modifiers": [m.type for m in obj.modifiers],
            "materials": [s.material.name if s.material else None for s in obj.material_slots],
        }
    # Preserve old evidence planes but hide them in the viewport.
    old_refs = bpy.data.collections.get("REFERENCE_Planes")
    old_ref_hidden = []
    if old_refs:
        for obj in old_refs.objects:
            obj.hide_set(True)
            old_ref_hidden.append(obj.name)
    bpy.data.collections.new("REFERENCE_Planes_SHAPE_01")
    scene = bpy.context.scene
    # Correct source mapping: 1 normalized unit = 350 px front/opposite.
    s_front = 1.0 / (BBOX["front"][3] - BBOX["front"][1])
    s_opp = 1.0 / (BBOX["opposite"][3] - BBOX["opposite"][1])
    s_top = NEW_MAX_RADIUS * 2.0 / (BBOX["top"][2] - BBOX["top"][0])
    front_cx = (BBOX["front"][0] + BBOX["front"][2]) * 0.5
    front_target = (-(front_cx - 256.0) * s_front, 0.0, (BBOX["front"][3] - 256.0) * s_front)
    opp_cx = (BBOX["opposite"][0] + BBOX["opposite"][2]) * 0.5
    opp_target = (-(opp_cx - 256.0) * s_opp, 0.0, (BBOX["opposite"][3] - 256.0) * s_opp)
    top_cx = (BBOX["top"][0] + BBOX["top"][2]) * 0.5
    top_cy = (BBOX["top"][1] + BBOX["top"][3]) * 0.5
    top_target = (-(top_cx - 256.0) * s_top, (top_cy - 256.0) * s_top, 0.5)

    # Build corrected reference planes before touching geometry.
    planes = [
        plane_mesh("Ref_Plane_Front_SHAPE_01", image_for("front"), s_front, (0, -1, 0), (0, 0, 1), front_target, BBOX["front"]),
        plane_mesh("Ref_Plane_Opposite_SHAPE_01", image_for("opposite"), s_opp, (0, 1, 0), (0, 0, 1), opp_target, BBOX["opposite"]),
        plane_mesh("Ref_Plane_Top_SHAPE_01", image_for("top"), s_top, (0, 0, 1), (0, 1, 0), top_target, BBOX["top"]),
    ]

    # ONE geometry correction: radial coordinates only. Height and root pose stay fixed.
    profile = bpy.data.objects["Barrel_Body_Profile"]
    old_radii = [round(v.co.x, 6) for v in profile.data.vertices]
    old_max = max(old_radii)
    factor = NEW_MAX_RADIUS / old_max
    for name in RADIAL_MESHES:
        obj = bpy.data.objects[name]
        for v in obj.data.vertices:
            v.co.x *= factor
            v.co.y *= factor
        obj.data.update()
    new_radii = [round(v.co.x, 6) for v in bpy.data.objects["Barrel_Body_Profile"].data.vertices]

    cams = {n: bpy.data.objects.get(n) for n in ("CAM_Front", "CAM_Opposite", "CAM_Top")}
    if any(v is None for v in cams.values()):
        raise RuntimeError("Missing one or more shape cameras")
    set_camera(cams["CAM_Front"], front_target, (0, -1, 0), 512.0 * s_front)
    set_camera(cams["CAM_Opposite"], opp_target, (0, 1, 0), 512.0 * s_opp)
    set_camera(cams["CAM_Top"], top_target, (0, 0, 1), 512.0 * s_top)
    scene.camera = cams["CAM_Front"]
    bpy.context.view_layer.update()

    mapping = {}
    for label, cam, bbox in (("front", cams["CAM_Front"], BBOX["front"]),
                             ("opposite", cams["CAM_Opposite"], BBOX["opposite"]),
                             ("top", cams["CAM_Top"], BBOX["top"])):
        bottom = project(scene, cam, (0, 0, 0.0))[:2]
        top = project(scene, cam, (0, 0, 1.0))[:2]
        left = project(scene, cam, (-NEW_MAX_RADIUS, 0, 0.5))[:2]
        right = project(scene, cam, (NEW_MAX_RADIUS, 0, 0.5))[:2]
        mapping[label] = {"source_bbox_px": list(bbox),
                          "projected_bottom_center_px": bottom,
                          "projected_top_center_px": top,
                          "projected_width_px": abs(right[0] - left[0]),
                          "ortho_scale": cam.data.ortho_scale,
                          "camera_location": list(cam.location)}
    bounds_min = Vector((1e9, 1e9, 1e9))
    bounds_max = Vector((-1e9, -1e9, -1e9))
    for name in PARTS:
        obj = bpy.data.objects[name]
        for v in obj.data.vertices:
            p = obj.matrix_world @ v.co
            for i in range(3):
                bounds_min[i] = min(bounds_min[i], p[i])
                bounds_max[i] = max(bounds_max[i], p[i])

    checkpoint = OUT / "barrel_shape_01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint), check_existing=False)
    print("SHAPE_CHECKPOINT_SAVED", checkpoint)
    (OUT / "renders").mkdir(parents=True, exist_ok=True)

    clay = bpy.data.materials.get("MAT_Review_Clay")
    if clay is None:
        raise RuntimeError("Missing neutral clay override material")
    render_paths = {}
    bpy.context.view_layer.material_override = clay
    bpy.context.view_layer.update()
    try:
        for label, cam in (("front", cams["CAM_Front"]), ("opposite", cams["CAM_Opposite"]),
                           ("top", cams["CAM_Top"])):
            scene.camera = cam
            path = OUT / "renders" / f"clay_{label}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            render_paths[label] = path
    finally:
        bpy.context.view_layer.material_override = None
        bpy.context.view_layer.update()

    sys.path.insert(0, str(ROOT / "tools" / "asset-pipeline"))
    from pipeline.inspection import snapshot
    snap = snapshot(PARTS)
    with open(OUT / "inspection_shape_01.json", "w") as f:
        json.dump(snap, f, indent=2, sort_keys=True)

    health = {}
    for name in PARTS:
        obj = bpy.data.objects[name]
        me = obj.data
        me.calc_loop_triangles()
        me.update()
        boundary = 0
        degenerate = 0
        for poly in me.polygons:
            if poly.area < 1e-10:
                degenerate += 1
        # boundary/nonmanifold via edge-face counts
        edge_faces = [0] * len(me.edges)
        for poly in me.polygons:
            for ek in poly.edge_keys:
                pass
        for e in me.edges:
            edge_faces[e.index] = 0
        for poly in me.polygons:
            for vi in poly.vertices:
                pass
        # Mesh edge users are not exposed as a simple collection in 5.x; use bmesh.
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(me)
        boundary = sum(1 for e in bm.edges if len(e.link_faces) == 1)
        nonmanifold = sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
        health[name] = {"verts": len(me.vertices), "faces": len(me.polygons),
                        "tris": sum(len(p.vertices) - 2 for p in me.polygons),
                        "boundary_edges": boundary, "nonmanifold_edges": nonmanifold,
                        "degenerate_faces": degenerate}

    # Contact sheet: source / clay / overlay, full 512 px cells.
    font = {
        "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
        "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
        "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
        "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
        "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
        "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
        "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
        "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
        "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
        "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
        "M": ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
        "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
        "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
        "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
        "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
        "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
        "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
        "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
        "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
        "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
        " ": ["00000"] * 7,
    }

    def draw_text(canvas, x0, y0, text, scale=2, color=(0.9, 0.9, 0.9)):
        cx = x0
        for ch in text:
            rows = font.get(ch, font[" "])
            for ry, row in enumerate(rows):
                for rx, val in enumerate(row):
                    if val == "1":
                        canvas[y0 + ry * scale:y0 + ry * scale + scale,
                               cx + rx * scale:cx + rx * scale + scale, :3] = color
            cx += 6 * scale

    def load_rgba(path):
        im = bpy.data.images.load(str(path), check_existing=False)
        arr = image_pixels(im).copy()
        bpy.data.images.remove(im)
        return arr

    def over_bg(arr):
        rgb = arr[:, :, :3]
        a = arr[:, :, 3:4]
        return rgb * a + 0.055 * (1.0 - a)

    def overlay(src, model):
        a = model[:, :, 3:4]
        tint = np.array([0.40, 0.07, 0.015], np.float32)
        return src[:, :, :3] * (1.0 - 0.55 * a) + tint[None, None, :] * (0.55 * a)

    cell, lab, gap = 512, 28, 10
    canvas = np.zeros((3 * (cell + lab) + 4 * gap, 3 * cell + 4 * gap, 4), np.float32)
    canvas[:, :, :3] = 0.045
    canvas[:, :, 3] = 1.0
    src_imgs = [image_pixels(image_for("front")), image_pixels(image_for("opposite")), image_pixels(image_for("top"))]
    labels = ["SOURCE FRONT", "SOURCE OPPOSITE", "SOURCE TOP"]
    for i, (src, label) in enumerate(zip(src_imgs, labels)):
        x, y = gap + i * (cell + gap), gap
        draw_text(canvas, x + 4, y + 7, label)
        canvas[y + lab:y + lab + cell, x:x + cell, :3] = over_bg(src)
        canvas[y + lab:y + lab + cell, x:x + cell, 3] = 1.0
    labels = ["CLAY FRONT", "CLAY OPPOSITE", "CLAY TOP"]
    for i, (key, label) in enumerate(zip(("front", "opposite", "top"), labels)):
        x, y = gap + i * (cell + gap), gap + (cell + lab + gap)
        draw_text(canvas, x + 4, y + 7, label)
        canvas[y + lab:y + lab + cell, x:x + cell, :3] = over_bg(load_rgba(render_paths[key]))
        canvas[y + lab:y + lab + cell, x:x + cell, 3] = 1.0
    labels = ["OVERLAY FRONT", "OVERLAY OPPOSITE", "OVERLAY TOP"]
    for i, (key, label) in enumerate(zip(("front", "opposite", "top"), labels)):
        x, y = gap + i * (cell + gap), gap + 2 * (cell + lab + gap)
        draw_text(canvas, x + 4, y + 7, label)
        src = image_pixels(image_for(key))
        canvas[y + lab:y + lab + cell, x:x + cell, :3] = overlay(src, load_rgba(render_paths[key]))
        canvas[y + lab:y + lab + cell, x:x + cell, 3] = 1.0
    sheet = OUT / "shape_comparison_sheet.png"
    save_generated_image("Barrel_Shape_Comparison", canvas, sheet)

    src_after = {k: sha256(v) for k, v in ALLOWED.items()}
    tech_hash_after = sha256(TECH)
    report = {
        "model_id": "barrel_img2_01_shape_01",
        "stage": "shape-only",
        "input_images": {k: {"path": str(v), "sha256": src_after[k]} for k, v in ALLOWED.items()},
        "image_only_statement": "Only the five allowlisted source images and the owned barrel_img2_01_technical_01 checkpoint were read. No original GLB, old candidate, source UV/map, research mesh, or other barrel file was opened.",
        "source_bytes_unchanged": src_before == src_after,
        "technical_checkpoint": str(TECH),
        "technical_checkpoint_sha256_before": tech_hash_before,
        "technical_checkpoint_sha256_after": tech_hash_after,
        "technical_checkpoint_preserved": tech_hash_before == tech_hash_after,
        "checkpoint": str(checkpoint),
        "preflight": preflight,
        "axes": {
            "up": "+Z",
            "front_camera": "at -Y looking +Y; image right +X; image up +Z",
            "opposite_camera": "at +Y looking -Y; image right -X; image up +Z",
            "top_camera": "at +Z looking -Z; image right +X; image up +Y (top up is a chosen datum)",
            "front_back_note": "Barrel is rotationally near-symmetric; front/opposite labels are provisional camera labels, not recovered object facing.",
        },
        "bbox_authority": {
            "front_px": list(BBOX["front"]), "opposite_px": list(BBOX["opposite"]), "top_px": list(BBOX["top"]),
            "front_width_px": BBOX["front"][2] - BBOX["front"][0],
            "front_height_px": BBOX["front"][3] - BBOX["front"][1],
            "front_aspect_width_over_height": (BBOX["front"][2] - BBOX["front"][0]) / (BBOX["front"][3] - BBOX["front"][1]),
            "normalized_height": 1.0,
            "classification": "PROVISIONAL normalized pilot height, not physical size",
            "pixels_per_unit_front": 1.0 / s_front,
            "pixels_per_unit_top": 1.0 / s_top,
            "mask_threshold": 0.08,
            "mask_diagnostic": "reference_landmark_diagnostic.json and mask_front_probe.png; bbox chosen from rows_gt20px/cols_gt20px and visual full contour",
            "old_bbox_was": {"front": [83, 78, 449, 323], "height_px": 245, "aspect": 1.506},
        },
        "geometry_correction": {
            "hypothesis": "The old front bbox height 245 px compressed normalized height and made radial proportions too wide; correcting the source pixel height and applying one radial scale should fix the stumpy aspect without changing topology or height.",
            "radius_scale_factor": factor,
            "old_max_radius": old_max,
            "new_max_radius": NEW_MAX_RADIUS,
            "old_profile_radii": old_radii,
            "new_profile_radii": new_radii,
            "z_profile_and_height_unchanged": True,
            "hoop_count": "3 broad hoops plus top/bottom narrow rim strips retained from the image-derived build",
            "topology_rebuild": False,
            "material_edits": False,
            "uv_edits": False,
            "texture_generation": False,
            "textured_renders": False,
        },
        "camera_pixel_mapping": mapping,
        "bounds_world": {"min": list(bounds_min), "max": list(bounds_max)},
        "dimensions": {"height": bounds_max[2] - bounds_min[2],
                       "width_x": bounds_max[0] - bounds_min[0],
                       "depth_y": bounds_max[1] - bounds_min[1]},
        "parts": PARTS,
        "health": health,
        "cost": snap.get("cost", {}),
        "cost_report_path": str(OUT / "inspection_shape_01.json"),
        "renders": {k: str(v) for k, v in render_paths.items()},
        "sheet": str(sheet),
        "materials_status": "UNREVIEWED; no material datablock or node graph edits in this shape pass; textured rendering BLOCKED.",
        "old_reference_planes_hidden_in_viewport": old_ref_hidden,
        "new_reference_planes": [{"name": p.name, "locked": bool(p.lock_location), "hide_render": bool(p.hide_render),
                                  "scale": p["reference_scale_uniform"]} for p in planes],
        "limitations": [
            "Source studio cameras/physical dimensions are unknown; per-view uniform scales are used.",
            "Front bbox includes the dark lower contact/shadow band resolved by the one-pass mask; normalized height is provisional.",
            "The top-view image up direction remains an arbitrary datum.",
            "No textured render, material inspection, UV review, or appearance claim is made.",
            "The 3/4 pose is not used in this correction pass.",
        ],
    }
    with open(OUT / "shape_report.json", "w") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print("SHEET_SAVED", sheet)
    print("COST", json.dumps(snap.get("cost", {}), sort_keys=True))
    print("DONE")


main()
