"""Shape-only clay evidence from the saved barrel_shape_01 checkpoint.

No materials are edited. Workbench renders are used only as neutral shape
diagnostics. No textured render, UV, or texture generation is performed.
"""
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / ".dev-shots" / "barrel-img2-01" / "shape-review-01"
TECH = ROOT / ".dev-shots" / "barrel-img2-01" / "barrel_img2_01_technical_01.blend"
SHAPE = OUT / "barrel_shape_01.blend"
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
BBOX = {"front": (68, 80, 441, 430), "opposite": (67, 80, 442, 430),
        "top": (62, 62, 449, 450)}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def image_pixels(img):
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)


def save_png(name, arr, path):
    h, w = arr.shape[:2]
    img = bpy.data.images.new(name, width=w, height=h, alpha=False)
    img.colorspace_settings.name = "sRGB"
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = arr[:, :, :3]
    img.pixels.foreach_set(np.flipud(rgba).ravel())
    img.file_format = "PNG"
    img.filepath_raw = str(path)
    img.save()
    return img


def project(scene, cam, p):
    c = world_to_camera_view(scene, cam, Vector(p))
    return [c.x * 512.0, (1.0 - c.y) * 512.0, c.z]


def main():
    if Path(bpy.data.filepath).resolve() != SHAPE.resolve():
        raise RuntimeError("Expected saved barrel_shape_01 checkpoint: " + bpy.data.filepath)
    source_before = {k: sha256(v) for k, v in ALLOWED.items()}
    checkpoint_before = sha256(SHAPE)
    tech_before = sha256(TECH)
    scene = bpy.context.scene
    cams = {n: bpy.data.objects[n] for n in ("CAM_Front", "CAM_Opposite", "CAM_Top")}
    scene.camera = cams["CAM_Front"]
    try:
        scene.render.engine = "BLENDER_WORKBENCH"
    except TypeError:
        # Blender reports valid identifiers in the TypeError message.
        raise
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    sh = scene.display.shading
    sh.light = "STUDIO"
    if hasattr(sh, "studio_light"):
        sh.studio_light = "paint.sl"
    sh.color_type = "SINGLE"
    sh.single_color = (0.52, 0.53, 0.55)
    sh.show_shadows = True
    sh.show_cavity = True
    if hasattr(sh, "cavity_type"):
        sh.cavity_type = "BOTH"
    if hasattr(sh, "show_object_outline"):
        sh.show_object_outline = False
    if hasattr(sh, "background_type"):
        sh.background_type = "VIEWPORT"
    if hasattr(sh, "background_color"):
        sh.background_color = (0.055, 0.055, 0.055)
    (OUT / "renders").mkdir(exist_ok=True)
    render_paths = {}
    for key, cam in (("front", cams["CAM_Front"]), ("opposite", cams["CAM_Opposite"]), ("top", cams["CAM_Top"])):
        scene.camera = cam
        path = OUT / "renders" / f"shape_clay_{key}_01.png"
        if path.exists():
            render_paths[key] = path
            continue
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        render_paths[key] = path

    # Cost/health snapshot through the unchanged repository helper.
    sys.path.insert(0, str(ROOT / "tools" / "asset-pipeline"))
    from pipeline.inspection import snapshot
    snap = snapshot(PARTS)
    insp_path = OUT / "inspection_shape_01.json"
    if insp_path.exists():
        with open(insp_path) as f:
            snap = json.load(f)
    else:
        snap = snapshot(PARTS)
        with open(insp_path, "w") as f:
            json.dump(snap, f, indent=2, sort_keys=True)

    import bmesh
    health = {}
    bmin = np.array([1e9, 1e9, 1e9], np.float64)
    bmax = np.array([-1e9, -1e9, -1e9], np.float64)
    for name in PARTS:
        obj = bpy.data.objects[name]
        me = obj.data
        bm = bmesh.new()
        bm.from_mesh(me)
        boundary = sum(1 for e in bm.edges if len(e.link_faces) == 1)
        nonmanifold = sum(1 for e in bm.edges if not e.is_manifold)
        degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-12)
        bm.free()
        for v in me.vertices:
            p = np.array(obj.matrix_world @ v.co)
            bmin = np.minimum(bmin, p)
            bmax = np.maximum(bmax, p)
        health[name] = {"verts": len(me.vertices), "faces": len(me.polygons),
                        "tris": sum(len(p.vertices) - 2 for p in me.polygons),
                        "boundary_edges": boundary, "nonmanifold_edges": nonmanifold,
                        "degenerate_faces": degenerate, "uv_layers": [u.name for u in me.uv_layers]}
    mapping = {}
    for key, cam in (("front", cams["CAM_Front"]), ("opposite", cams["CAM_Opposite"]), ("top", cams["CAM_Top"])):
        b = project(scene, cam, (0, 0, 0.0))
        t = project(scene, cam, (0, 0, 1.0))
        l = project(scene, cam, (-0.532857, 0, 0.5))
        r = project(scene, cam, (0.532857, 0, 0.5))
        mapping[key] = {"source_bbox_px": list(BBOX[key]), "bottom_center_px": b[:2],
                        "top_center_px": t[:2], "width_px": abs(r[0] - l[0]),
                        "ortho_scale": cam.data.ortho_scale, "camera_location": list(cam.location),
                        "camera_rotation_euler": list(cam.rotation_euler)}

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

    def text(canvas, x0, y0, s, scale=2, color=(0.9, 0.9, 0.9)):
        x = x0
        for ch in s:
            for ry, row in enumerate(font.get(ch, font[" "])):
                for rx, val in enumerate(row):
                    if val == "1":
                        canvas[y0 + ry * scale:y0 + ry * scale + scale,
                               x + rx * scale:x + rx * scale + scale, :3] = color
            x += 6 * scale

    def load_rgba(path):
        im = bpy.data.images.load(str(path), check_existing=False)
        arr = image_pixels(im).copy()
        bpy.data.images.remove(im)
        return arr

    def model_with_alpha(path):
        arr = load_rgba(path)
        if arr[:, :, 3].min() > 0.99:
            # Workbench transparent fallback: separate the neutral object from
            # the known flat review background by RGB difference.
            bg = arr[0, 0, :3]
            d = np.max(np.abs(arr[:, :, :3] - bg[None, None, :]), axis=2)
            alpha = (d > 0.012).astype(np.float32)
            arr[:, :, 3] = alpha
        return arr

    def bg_over(arr):
        return arr[:, :, :3] * arr[:, :, 3:4] + 0.055 * (1.0 - arr[:, :, 3:4])

    def overlay(src, mod):
        a = mod[:, :, 3:4]
        tint = np.array([0.40, 0.07, 0.015], np.float32)
        return src[:, :, :3] * (1.0 - 0.55 * a) + tint[None, None, :] * (0.55 * a)

    src_arrays = {}
    for key in ("front", "opposite", "top"):
        im = bpy.data.images.get(f"clay_source_{key}.png")
        if im is None:
            im = bpy.data.images.load(str(ALLOWED[key]), check_existing=False)
        src_arrays[key] = image_pixels(im).copy()
    cell, lab, gap = 512, 28, 10
    canvas = np.zeros((3 * (cell + lab) + 4 * gap, 3 * cell + 4 * gap, 4), np.float32)
    canvas[:, :, :3] = 0.045
    canvas[:, :, 3] = 1.0
    for i, key in enumerate(("front", "opposite", "top")):
        x, y = gap + i * (cell + gap), gap
        text(canvas, x + 4, y + 7, "SOURCE " + key.upper())
        canvas[y + lab:y + lab + cell, x:x + cell, :3] = bg_over(src_arrays[key])
        canvas[y + lab:y + lab + cell, x:x + cell, 3] = 1.0
    models = {}
    for i, key in enumerate(("front", "opposite", "top")):
        x, y = gap + i * (cell + gap), gap + (cell + lab + gap)
        text(canvas, x + 4, y + 7, "CLAY " + key.upper())
        models[key] = model_with_alpha(render_paths[key])
        canvas[y + lab:y + lab + cell, x:x + cell, :3] = bg_over(models[key])
        canvas[y + lab:y + lab + cell, x:x + cell, 3] = 1.0
    for i, key in enumerate(("front", "opposite", "top")):
        x, y = gap + i * (cell + gap), gap + 2 * (cell + lab + gap)
        text(canvas, x + 4, y + 7, "OVERLAY " + key.upper())
        canvas[y + lab:y + lab + cell, x:x + cell, :3] = overlay(src_arrays[key], models[key])
        canvas[y + lab:y + lab + cell, x:x + cell, 3] = 1.0
    sheet = OUT / "shape_comparison_sheet_01.png"
    if sheet.exists():
        raise RuntimeError("Refusing to overwrite " + str(sheet))
    save_png("Barrel_Shape_Comparison_01", canvas, sheet)

    src_after = {k: sha256(v) for k, v in ALLOWED.items()}
    checkpoint_after = sha256(SHAPE)
    tech_after = sha256(TECH)
    report = {
        "model_id": "barrel_img2_01_shape_01",
        "stage": "shape-only",
        "checkpoint": str(SHAPE),
        "checkpoint_sha256_before_evidence": checkpoint_before,
        "checkpoint_sha256_after_evidence": checkpoint_after,
        "checkpoint_preserved": checkpoint_before == checkpoint_after,
        "input_images": {k: {"path": str(v), "sha256": src_after[k]} for k, v in ALLOWED.items()},
        "source_bytes_unchanged": source_before == src_after,
        "technical_checkpoint": str(TECH),
        "technical_checkpoint_sha256_before": tech_before,
        "technical_checkpoint_sha256_after": tech_after,
        "technical_checkpoint_preserved": tech_before == tech_after,
        "image_only_statement": "Only the five allowlisted source images and the owned barrel_img2_01_technical_01 / barrel_shape_01 checkpoints were read. No original GLB, old candidate, source UV/map, research mesh, or other barrel file was opened.",
        "axes": {"up": "+Z", "front_camera": "at -Y looking +Y", "opposite_camera": "at +Y looking -Y",
                 "top_camera": "at +Z looking -Z", "front_back_note": "front/opposite labels provisional for a near-symmetric barrel"},
        "bbox_authority": {
            "front_px": list(BBOX["front"]), "opposite_px": list(BBOX["opposite"]), "top_px": list(BBOX["top"]),
            "front_width_px": 373, "front_height_px": 350, "front_aspect": 373.0 / 350.0,
            "old_front_bbox": [83, 78, 449, 323], "old_height_px": 245, "old_aspect": 1.506,
            "normalized_height": 1.0, "classification": "PROVISIONAL normalized pilot height, not physical size",
            "mask_diagnostic": "reference_landmark_diagnostic.json; contour_probe_once.json; mask_front_probe.png",
            "mask_threshold": 0.08,
        },
        "camera_pixel_mapping": mapping,
        "dimensions": {"height": float(bmax[2] - bmin[2]), "width_x": float(bmax[0] - bmin[0]),
                       "depth_y": float(bmax[1] - bmin[1])},
        "bounds_world": {"min": bmin.tolist(), "max": bmax.tolist()},
        "parts": PARTS, "health": health,
        "cost": snap.get("cost", {}), "cost_report_path": str(insp_path),
        "renders": {k: str(v) for k, v in render_paths.items()},
        "sheet": str(sheet),
        "materials_status": "UNREVIEWED; no material graph or assignment edits; textured rendering BLOCKED.",
        "limitations": [
            "Per-view uniform scale uses unknown studio camera calibration.",
            "Front bbox includes the lower dark contact band resolved by the inspected one-pass mask; height is provisional.",
            "Top image up direction is a chosen datum.",
            "3/4 pose is not used or adjudicated in this pass.",
            "Workbench is a neutral shape diagnostic, not final appearance.",
        ],
    }
    report_path = OUT / "shape_report_01.json"
    if report_path.exists():
        raise RuntimeError("Refusing to overwrite " + str(report_path))
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print("SHEET", sheet)
    print("REPORT", report_path)
    print("COST", json.dumps(snap.get("cost", {}), sort_keys=True))
    print("DONE")


main()
