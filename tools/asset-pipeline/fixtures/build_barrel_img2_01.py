"""Image-only barrel pilot builder.

Reads exactly five allowed source images from barrel-efficiency-01/evidence,
builds locked reference planes first, then one new procedural barrel candidate.
No existing barrel geometry, maps, scripts, checkpoints or GLBs are read.
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
OUT = ROOT / ".dev-shots" / "barrel-img2-01"
SRC = ROOT / ".dev-shots" / "barrel-efficiency-01" / "evidence"
ALLOWED = {
    "front": SRC / "clay_source_front.png",
    "opposite": SRC / "clay_source_opposite.png",
    "three_quarter": SRC / "clay_source_three_quarter.png",
    "top": SRC / "clay_source_top.png",
    "textured_three_quarter": SRC / "textured_source_three_quarter.png",
}
# Manual landmark observations on the 512 px sources. These are deliberately
# not auto-thresholded masks: the backgrounds are opaque studio grey.
BBOX = {
    "front": (83, 78, 449, 323),
    "opposite": (84, 78, 449, 323),
    "top": (65, 62, 449, 450),
    "three_quarter": (54, 62, 466, 454),
    "textured_three_quarter": (52, 52, 473, 455),
}
PASS_ID = "initial"
PASS_INDEX = 1
if "--" in sys.argv:
    extra = sys.argv[sys.argv.index("--") + 1:]
    if "pass2" in extra or "--pass2" in extra:
        PASS_ID = "corrected_01"
        PASS_INDEX = 2
    elif "technical" in extra or "--technical" in extra:
        PASS_ID = "technical_01"
        PASS_INDEX = 2
SUFFIX = "" if PASS_INDEX == 1 else f"_{PASS_ID}"


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


def save_generated_image(name, arr, filepath, colorspace):
    h, w = arr.shape[:2]
    img = bpy.data.images.new(name, width=w, height=h, alpha=False, float_buffer=False)
    img.colorspace_settings.name = colorspace
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = arr[:, :, :3]
    # Blender's pixel buffer is bottom-up.
    img.pixels.foreach_set(np.flipud(rgba).ravel())
    img.file_format = "PNG"
    img.filepath_raw = str(filepath)
    img.save()
    img.pack()
    return img


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def make_wood_textures(texture_dir):
    n = 1024
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    u = xx / (n - 1)
    v = yy / (n - 1)
    staves = 20.0
    su = u * staves
    board = np.floor(su)
    within = su - board
    rng = np.random.default_rng(20261023)
    board_phase = (np.sin(board * 12.9898 + 3.17) * 43758.5453) % 1.0
    fine = (np.sin((u * 731.0 + v * 397.0) * math.tau) * 0.5 + 0.5)
    broad = (np.sin((v * 24.0 + u * 7.0 + board_phase * 3.0) * math.tau) * 0.5 + 0.5)
    grain = 0.55 * fine + 0.45 * broad
    grain2 = (np.sin((v * 91.0 + 0.16 * np.sin(v * 17.0 + board * 1.9) +
                      u * 5.0 + board_phase * 4.0) * math.tau) * 0.5 + 0.5)
    grain = 0.28 * grain + 0.72 * grain2
    seam = 1.0 - np.clip(np.minimum(within, 1.0 - within) / 0.017, 0.0, 1.0)
    seam *= (within < 0.017) | (within > 0.983)
    # Knots: warm dark ellipses with concentric grain distortion.
    knot = np.zeros((n, n), dtype=np.float32)
    ring = np.zeros((n, n), dtype=np.float32)
    for _ in range(8):
        ku = float(rng.uniform(0.03, 0.97))
        kv = float(rng.uniform(0.08, 0.92))
        rx = float(rng.uniform(0.008, 0.017))
        ry = float(rng.uniform(0.022, 0.050))
        dx = (u - ku) / rx
        dy = (v - kv) / ry
        d = np.sqrt(dx * dx + dy * dy)
        knot += np.exp(-(d * d) * 0.9)
        ring += np.exp(-((d - 1.65) ** 2) * 5.0) * 0.55
    knot = np.clip(knot, 0.0, 1.0)
    ring = np.clip(ring, 0.0, 1.0)

    hsl_light = np.array([srgb_to_linear(0.82), srgb_to_linear(0.68), srgb_to_linear(0.47)], np.float32)
    hsl_dark = np.array([srgb_to_linear(0.48), srgb_to_linear(0.31), srgb_to_linear(0.17)], np.float32)
    hsl_seam = np.array([srgb_to_linear(0.26), srgb_to_linear(0.16), srgb_to_linear(0.09)], np.float32)
    tone = 0.74 + 0.14 * (grain - 0.5) + 0.09 * (board_phase - 0.5) - 0.10 * knot - 0.08 * ring
    tone = np.clip(tone, 0.0, 1.0)
    col = hsl_dark[None, None, :] + (hsl_light - hsl_dark)[None, None, :] * tone[:, :, None]
    col = col * (1.0 - seam[:, :, None] * 0.82) + hsl_seam[None, None, :] * seam[:, :, None] * 0.82
    col = np.clip(col, 0.0, 1.0)

    height = 0.58 * grain + 0.18 * ring + 0.10 * knot - 0.70 * seam
    gy, gx = np.gradient(height)
    strength = 4.2
    normal = np.dstack((-gx * strength, -gy * strength, np.ones_like(height)))
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)
    normal = normal * 0.5 + 0.5

    rough = np.clip(0.44 + 0.15 * (1.0 - grain) + 0.22 * seam + 0.12 * knot, 0.0, 1.0)
    rough_rgb = np.dstack((rough, rough, rough))

    base = save_generated_image("Barrel_Wood_BaseColor", col, texture_dir / "barrel_wood_basecolor_1024.png", "sRGB")
    nrm = save_generated_image("Barrel_Wood_Normal", normal, texture_dir / "barrel_wood_normal_1024.png", "Non-Color")
    rgh = save_generated_image("Barrel_Wood_Roughness", rough_rgb, texture_dir / "barrel_wood_roughness_1024.png", "Non-Color")
    for img in (base, nrm, rgh):
        img.filepath = bpy.path.relpath(str(texture_dir / Path(img.filepath_raw).name), start=str(OUT))
    return base, nrm, rgh


def image_material(name, image):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Linear"
    tex.extension = "CLIP"
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    mat["reference_only"] = True
    return mat


def make_reference_plane(name, image, bbox, s, dirv, upv, target, plane_distance=1.5):
    wpx, hpx = image.size
    w = wpx * s
    h = hpx * s
    dirv = Vector(dirv).normalized()
    upv = Vector(upv).normalized()
    right = (-dirv).cross(upv).normalized()
    center = Vector(target) - dirv * plane_distance
    corners = [
        center - right * (w * 0.5) - upv * (h * 0.5),
        center + right * (w * 0.5) - upv * (h * 0.5),
        center + right * (w * 0.5) + upv * (h * 0.5),
        center - right * (w * 0.5) + upv * (h * 0.5),
    ]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata([tuple(c) for c in corners], [], [(0, 1, 2, 3)])
    mesh.update()
    uv = mesh.uv_layers.new(name="UVMap")
    for loop, co in zip(uv.data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop.uv = co
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections["REFERENCE_Planes"].objects.link(obj)
    obj.data.materials.append(image_material(name + "_Mat", image))
    obj.lock_location = (True, True, True)
    obj.lock_rotation = (True, True, True)
    obj.lock_scale = (True, True, True)
    obj.hide_render = True
    obj["reference_image"] = str(image.filepath)
    obj["source_bbox_px"] = list(bbox)
    obj["pixels_per_world_unit"] = 1.0 / s
    obj["reference_scale_uniform"] = s
    obj["locked_reference"] = True
    return obj


def add_object(name, mesh, collection, root, mat):
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    obj.parent = root
    return obj


def lathe_solid(name, profile, segments=64):
    verts = []
    faces = []
    rings = []
    for r, z in profile:
        if abs(r) < 1e-9:
            rings.append([len(verts)])
            verts.append((0.0, 0.0, z))
        else:
            ring = []
            for i in range(segments):
                a = math.tau * i / segments
                ring.append(len(verts))
                verts.append((r * math.cos(a), r * math.sin(a), z))
            rings.append(ring)
    for ridx in range(len(rings) - 1):
        a, b = rings[ridx], rings[ridx + 1]
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for i in range(segments):
                faces.append((a[0], b[(i + 1) % segments], b[i]))
        elif len(b) == 1:
            for i in range(segments):
                faces.append((a[i], a[(i + 1) % segments], b[0]))
        else:
            for i in range(segments):
                j = (i + 1) % segments
                faces.append((a[i], a[j], b[j], b[i]))
    # Close first and last radial rings if they are not axis points.
    if len(rings[0]) > 1:
        faces.append(tuple(reversed(rings[0])))
    if len(rings[-1]) > 1:
        faces.append(tuple(rings[-1]))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for p in mesh.polygons:
        p.use_smooth = True
    return mesh


def ring_mesh(name, r_in, r_out, z0, z1, segments=64, rounding=0.35):
    # Rounded rectangular sweep, defined by an 8 point radial cross-section.
    dz = z1 - z0
    rr = min(abs(r_out - r_in) * rounding, dz * 0.42)
    profile = [
        (r_in, z1),
        (r_out - rr, z1),
        (r_out, z1 - rr),
        (r_out, z0 + rr),
        (r_out - rr, z0),
        (r_in, z0),
        (r_in, z0 + rr),
        (r_in, z1 - rr),
    ]
    # Lathe profile is an open but radial loop; add a closing quad ring manually.
    verts = []
    rings = []
    for r, z in profile:
        ring = []
        for i in range(segments):
            a = math.tau * i / segments
            ring.append(len(verts))
            verts.append((r * math.cos(a), r * math.sin(a), z))
        rings.append(ring)
    faces = []
    for ridx in range(len(rings)):
        a = rings[ridx]
        b = rings[(ridx + 1) % len(rings)]
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((a[i], a[j], b[j], b[i]))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for p in mesh.polygons:
        p.use_smooth = True
    return mesh


def cylinder_uv(mesh, height, v_offset=0.0):
    uv = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        us = []
        for li in poly.loop_indices:
            vi = mesh.loops[li].vertex_index
            x, y, z = mesh.vertices[vi].co
            u = math.atan2(y, x) / math.tau + 0.5
            us.append(u)
        if max(us) - min(us) > 0.5:
            us = [u + 1.0 if u < 0.5 else u for u in us]
        for li, u in zip(poly.loop_indices, us):
            vi = mesh.loops[li].vertex_index
            z = mesh.vertices[vi].co.z
            uv.data[li].uv = (u, (z - v_offset) / height)


def lid_uv(mesh, scale=0.40):
    uv = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        planar = abs(poly.normal.z) > 0.55
        us = []
        for li in poly.loop_indices:
            vi = mesh.loops[li].vertex_index
            x, y, z = mesh.vertices[vi].co
            if planar:
                us.append((x * scale + 0.5, y * scale + 0.5))
            else:
                us.append(((math.atan2(y, x) / math.tau) + 0.5, (z - 0.945) / 0.06))
        for li, val in zip(poly.loop_indices, us):
            uv.data[li].uv = val


def wood_material(base, nrm, rgh):
    mat = bpy.data.materials.new("MAT_Barrel_Wood")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = "UVMap"
    tb = nt.nodes.new("ShaderNodeTexImage")
    tb.image = base
    tb.interpolation = "Linear"
    tn = nt.nodes.new("ShaderNodeTexImage")
    tn.image = nrm
    tn.interpolation = "Linear"
    tr = nt.nodes.new("ShaderNodeTexImage")
    tr.image = rgh
    tr.interpolation = "Linear"
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = 0.55
    nt.links.new(uvn.outputs["UV"], tb.inputs["Vector"])
    nt.links.new(uvn.outputs["UV"], tn.inputs["Vector"])
    nt.links.new(uvn.outputs["UV"], tr.inputs["Vector"])
    nt.links.new(tb.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tr.outputs["Color"], bsdf.inputs["Roughness"])
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.35
    return mat


def metal_material():
    mat = bpy.data.materials.new("MAT_Barrel_Metal")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.39, 0.40, 0.40, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.31
    if "Anisotropic IOR Level" in bsdf.inputs:
        bsdf.inputs["Anisotropic IOR Level"].default_value = 0.35
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def clay_material():
    mat = bpy.data.materials.new("MAT_Review_Clay")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.36, 0.37, 0.38, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.62
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    mat["review_helper"] = True
    return mat


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = -0.35
    world = bpy.data.worlds.new("WORLD_Barrel_Review")
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.055, 0.058, 0.060, 1.0)
    bg.inputs["Strength"].default_value = 0.65
    scene.world = world
    scene.render.filepath = str(OUT / "renders" / "tmp.png")
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15
    return scene


def add_lights():
    specs = [
        ("KEY", (-2.6, -3.4, 4.2), 180.0, 4.0),
        ("FILL", (3.0, -1.0, 2.4), 65.0, 3.5),
        ("RIM", (1.8, 3.2, 3.6), 120.0, 3.0),
        ("TOP", (0.0, 0.0, 5.0), 55.0, 3.0),
    ]
    for name, loc, power, size in specs:
        data = bpy.data.lights.new("LIGHT_" + name, type="AREA")
        data.energy = power
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new("LIGHT_" + name, data)
        bpy.data.collections["STUDIO"].objects.link(obj)
        obj.location = loc
        direction = Vector((0, 0, 0.5)) - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    # No floor: the supplied studio references have a flat backdrop, not a visible ground.


def camera_view(name, loc, target, ortho_scale):
    data = bpy.data.cameras.new("CAM_" + name)
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
    obj = bpy.data.objects.new("CAM_" + name, data)
    bpy.data.collections["STUDIO"].objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return obj


def projected_px(scene, obj, point):
    co = world_to_camera_view(scene, obj, Vector(point))
    return [co.x * 512.0, (1.0 - co.y) * 512.0, co.z]


def make_sources():
    hashes_before = {key: sha256(path) for key, path in ALLOWED.items()}
    imgs = {}
    for key, path in ALLOWED.items():
        if not path.exists():
            raise FileNotFoundError(path)
        img = bpy.data.images.load(str(path), check_existing=False)
        # Pack the allowlisted reference bytes so the new checkpoint is portable.
        # The original files remain untouched and are re-hashed at the end.
        img.pack()
        imgs[key] = img
    return imgs, hashes_before


def build():
    if PASS_INDEX == 1:
        if OUT.exists():
            existing_files = [p for p in OUT.rglob("*") if p.is_file() and p.name != ".DS_Store"]
            if existing_files:
                raise RuntimeError("Refusing to overwrite non-empty barrel-img2-01 directory")
        else:
            OUT.mkdir(parents=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "renders").mkdir(exist_ok=True)
    texture_dir = OUT / ("textures" if PASS_INDEX == 1 else f"textures_{PASS_ID}")
    texture_dir.mkdir(exist_ok=True)
    scene = setup_scene()
    coll_ref = bpy.data.collections.new("REFERENCE_Planes")
    coll_model = bpy.data.collections.new("MODEL_Barrel")
    coll_ctrl = bpy.data.collections.new("MODEL_Controls")
    coll_studio = bpy.data.collections.new("STUDIO")
    for c in (coll_ref, coll_model, coll_ctrl, coll_studio):
        scene.collection.children.link(c)
    add_lights()

    imgs, hashes_before = make_sources()
    # Manual bbox-derived scale: 1.0 normalized world unit equals observed barrel height.
    front_h = BBOX["front"][3] - BBOX["front"][1]
    opp_h = BBOX["opposite"][3] - BBOX["opposite"][1]
    s_front = 1.0 / front_h
    s_opp = 1.0 / opp_h
    top_diam = 386.0
    s_top = 1.5 / top_diam
    t3_h = BBOX["three_quarter"][3] - BBOX["three_quarter"][1]
    tt3_h = BBOX["textured_three_quarter"][3] - BBOX["textured_three_quarter"][1]
    s_t3 = 1.0 / t3_h
    s_tt3 = 1.0 / tt3_h

    def target_for(key, s, up_axis="z"):
        x0, y0, x1, y1 = BBOX[key]
        cx = (x0 + x1) * 0.5
        cy = (y0 + y1) * 0.5
        if up_axis == "z":
            tx = -(cx - 256.0) * s
            tz = (y1 - 256.0) * s
            return (tx, 0.0, tz)
        tx = -(cx - 256.0) * s
        ty = (cy - 256.0) * s
        return (tx, ty, 0.5)

    front_target = target_for("front", s_front)
    opp_target = target_for("opposite", s_opp)
    top_target = target_for("top", s_top, "y")
    t3_target = (0.0, 0.0, 0.5)
    tt3_target = (0.0, 0.0, 0.5)
    planes = [
        make_reference_plane("Ref_Plane_Front", imgs["front"], BBOX["front"], s_front, (0, -1, 0), (0, 0, 1), front_target),
        make_reference_plane("Ref_Plane_Opposite", imgs["opposite"], BBOX["opposite"], s_opp, (0, 1, 0), (0, 0, 1), opp_target),
        make_reference_plane("Ref_Plane_Top", imgs["top"], BBOX["top"], s_top, (0, 0, 1), (0, 1, 0), top_target),
        make_reference_plane("Ref_Plane_Clay_ThreeQuarter", imgs["three_quarter"], BBOX["three_quarter"], s_t3,
                             (0.506, -0.723, 0.469), (0, 0, 1), t3_target, 2.0),
        make_reference_plane("Ref_Plane_Textured_ThreeQuarter", imgs["textured_three_quarter"],
                             BBOX["textured_three_quarter"], s_tt3,
                             (0.506, -0.723, 0.469), (0, 0, 1), tt3_target, 2.0),
    ]
    print("REFERENCE_PLANES_BUILT", [(p.name, tuple(round(v, 6) for v in p.location), p.lock_location) for p in planes])

    base_img, nrm_img, rgh_img = make_wood_textures(texture_dir)
    mat_wood = wood_material(base_img, nrm_img, rgh_img)
    mat_metal = metal_material()
    mat_clay = clay_material()

    root = bpy.data.objects.new("Barrel_Model_Control", None)
    coll_model.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.2

    # Body source: editable radial profile + live Screw modifier.
    stations = [
        (0.600, 0.000), (0.617, 0.020), (0.637, 0.055), (0.665, 0.115),
        (0.704, 0.210), (0.730, 0.320), (0.742, 0.420), (0.735, 0.520),
        (0.715, 0.620), (0.685, 0.720), (0.650, 0.815), (0.620, 0.885),
        (0.604, 0.928), (0.598, 0.950),
    ]
    pm = bpy.data.meshes.new("Barrel_Body_Profile_Mesh")
    pm.from_pydata([(r, 0.0, z) for r, z in stations], [(i, i + 1) for i in range(len(stations) - 1)], [])
    pm.update()
    profile_obj = bpy.data.objects.new("Barrel_Body_Profile", pm)
    coll_ctrl.objects.link(profile_obj)
    profile_obj.parent = root
    profile_obj.show_in_front = True
    profile_obj.display_type = "WIRE"
    profile_obj.hide_render = True
    profile_obj["role"] = "editable lathe radius/height stations"

    body_ctrl_mesh = bpy.data.meshes.new("Barrel_Body_Screw_Source_Mesh")
    body_ctrl_mesh.from_pydata([(r, 0.0, z) for r, z in stations], [(i, i + 1) for i in range(len(stations) - 1)], [])
    body_ctrl = bpy.data.objects.new("Barrel_Body_Screw_Source", body_ctrl_mesh)
    coll_ctrl.objects.link(body_ctrl)
    body_ctrl.parent = root
    body_ctrl.hide_render = True
    body_ctrl.hide_set(True)
    screw = body_ctrl.modifiers.new("Editable_Revolve", "SCREW")
    screw.axis = "Z"
    screw.angle = math.tau
    screw.steps = 64
    screw.render_steps = 64
    screw.use_merge_vertices = True
    screw.merge_threshold = 1e-4
    if hasattr(screw, "use_smooth_shade"):
        screw.use_smooth_shade = True
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body_ctrl.evaluated_get(dg)
    body_mesh = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
    body_mesh.name = "Barrel_Body_Mesh"
    # Fill the two hidden end loops so the authored exterior is a closed mesh.
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(body_mesh)
    boundary = [e for e in bm.edges if len(e.link_faces) == 1]
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary, sides=64)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(body_mesh)
    bm.free()
    body = add_object("Barrel_Body", body_mesh, coll_model, root, mat_wood)
    cylinder_uv(body.data, 1.0)
    body["profile_source"] = profile_obj.name
    body["derived_from"] = body_ctrl.name

    lid_profile = [
        (0.000, 1.000), (0.535, 1.000), (0.580, 0.997), (0.600, 0.987),
        (0.604, 0.973), (0.600, 0.959), (0.575, 0.951), (0.000, 0.951),
    ]
    lid_mesh = lathe_solid("Barrel_Lid", lid_profile, 64)
    lid = add_object("Barrel_Lid", lid_mesh, coll_model, root, mat_wood)
    lid_uv(lid.data, 0.40)

    # Hoops and narrow rim strips. Broad positions come from the front image bands.
    hoop_specs = [
        ("Barrel_Hoop_Upper", 0.606, 0.623, 0.898, 0.951, 64),
        ("Barrel_Hoop_Center", 0.720, 0.740, 0.520, 0.586, 64),
        ("Barrel_Hoop_Lower", 0.686, 0.704, 0.127, 0.181, 64),
        ("Barrel_Rim_Top", 0.600, 0.620, 0.958, 0.984, 64),
        ("Barrel_Rim_Bottom", 0.605, 0.624, 0.012, 0.044, 64),
    ]
    hoop_objs = []
    for hname, rin, rout, z0, z1, seg in hoop_specs:
        hm = ring_mesh(hname, rin, rout, z0, z1, seg)
        ho = add_object(hname, hm, coll_model, root, mat_metal)
        cylinder_uv(ho.data, 1.0)
        hoop_objs.append(ho)

    part_names = ["Barrel_Body", "Barrel_Lid"] + [h.name for h in hoop_objs]
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name in part_names:
            for p in obj.data.polygons:
                p.use_smooth = True

    # Cameras use the source pixel mapping established above.
    cam_front = camera_view("Front", (front_target[0], -3.0, front_target[2]), front_target, 512.0 * s_front)
    cam_opp = camera_view("Opposite", (opp_target[0], 3.0, opp_target[2]), opp_target, 512.0 * s_opp)
    cam_top = camera_view("Top", (top_target[0], top_target[1], 3.0), top_target, 512.0 * s_top)
    t3_dir = Vector((0.506, -0.723, 0.469)).normalized()
    tt3_dir = t3_dir
    cam_t3 = camera_view("Clay_ThreeQuarter", Vector(t3_target) + t3_dir * 3.5, t3_target, 2.05)
    cam_tt3 = camera_view("Textured_ThreeQuarter", Vector(tt3_target) + tt3_dir * 3.5, tt3_target, 2.05)

    bpy.context.view_layer.update()
    projections = {}
    for label, cam, key in (("front", cam_front, "front"), ("opposite", cam_opp, "opposite"), ("top", cam_top, "top")):
        projections[label] = {
            "source_bbox": BBOX[key],
            "image_center_world_target": list(target_for(key, s_front if label != "top" else s_top,
                                                       "z" if label != "top" else "y")),
            "model_bottom_center_px": projected_px(scene, cam, (0, 0, 0.0))[:2],
            "model_top_center_px": projected_px(scene, cam, (0, 0, 1.0))[:2],
        }
        if label == "top":
            projections[label]["model_diameter_px"] = 2.0 * projected_px(scene, cam, (0.755, 0, 0.5))[0] - 512.0
        else:
            projections[label]["model_width_px"] = projected_px(scene, cam, (0.755, 0, 0.5))[0] - projected_px(scene, cam, (-0.755, 0, 0.5))[0]
    scene.camera = cam_front
    checkpoint = OUT / (f"barrel_img2_01{SUFFIX}.blend")
    if checkpoint.exists():
        raise RuntimeError("Refusing to overwrite checkpoint: " + str(checkpoint))
    bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint), check_existing=False)
    print("CHECKPOINT_SAVED", checkpoint)

    # Clay matched contours, transparent so the contact sheet can overlay them.
    scene.camera = cam_front
    bpy.context.view_layer.material_override = mat_clay
    scene.render.film_transparent = True
    render_paths = {}
    for label, cam in (("front", cam_front), ("opposite", cam_opp), ("top", cam_top)):
        scene.camera = cam
        path = OUT / "renders" / f"clay_{label}{SUFFIX}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        render_paths[label] = path
    scene.camera = cam_tt3
    path = OUT / "renders" / f"textured_three_quarter{SUFFIX}.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    render_paths["textured_three_quarter"] = path
    scene.camera = cam_t3
    path = OUT / "renders" / f"clay_three_quarter{SUFFIX}.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    render_paths["three_quarter"] = path
    bpy.context.view_layer.material_override = None

    # Cost/health snapshot through the repository helper.
    sys.path.insert(0, str(ROOT / "tools" / "asset-pipeline"))
    from pipeline.inspection import snapshot
    snap = snapshot(part_names)
    snap_path = OUT / f"inspection{SUFFIX}.json"
    with open(snap_path, "w") as f:
        json.dump(snap, f, indent=2, sort_keys=True)
    print("SNAPSHOT_SAVED", snap_path)

    # Health and bounds from the authored meshes.
    health = {}
    all_min = Vector((1e9, 1e9, 1e9))
    all_max = Vector((-1e9, -1e9, -1e9))
    for name in part_names:
        obj = bpy.data.objects[name]
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        boundary = sum(1 for e in bm.edges if len(e.link_faces) == 1)
        nonmanifold = sum(1 for e in bm.edges if not e.is_manifold)
        tris = sum(max(0, len(p.vertices) - 2) for p in mesh.polygons)
        bm.free()
        for v in mesh.vertices:
            w = obj.matrix_world @ v.co
            for i in range(3):
                all_min[i] = min(all_min[i], w[i])
                all_max[i] = max(all_max[i], w[i])
        health[name] = {"verts": len(mesh.vertices), "faces": len(mesh.polygons),
                        "tris": tris, "boundary_edges": boundary,
                        "nonmanifold_edges": nonmanifold, "uv_layers": [l.name for l in mesh.uv_layers]}

    hashes_after = {key: sha256(path) for key, path in ALLOWED.items()}
    if hashes_before != hashes_after:
        raise RuntimeError("Allowed source image bytes changed")
    source_hashes = {key: {"path": str(ALLOWED[key]), "sha256": hashes_after[key]} for key in ALLOWED}

    # Contact sheets. Labels are drawn with a tiny local 5x7 bitmap font.
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
        "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
        "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
        "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
        "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
        " ": ["00000"] * 7,
        "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
        "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    }

    def draw_text(canvas, x0, y0, text, scale=2, color=(0.9, 0.9, 0.9)):
        cx = x0
        for ch in text:
            rows = font.get(ch, font[" "])
            for ry, row in enumerate(rows):
                for rx, val in enumerate(row):
                    if val == "1":
                        yy = y0 + ry * scale
                        xx = cx + rx * scale
                        canvas[yy:yy + scale, xx:xx + scale, :3] = color
            cx += 6 * scale

    def load_rgba(path):
        img = bpy.data.images.load(str(path), check_existing=False)
        arr = image_pixels(img).copy()
        bpy.data.images.remove(img)
        return arr

    def cell_view(arr, bg=0.055):
        rgb = arr[:, :, :3].copy()
        a = arr[:, :, 3:4] if arr.shape[2] > 3 else np.ones_like(rgb[:, :, :1])
        return rgb * a + bg * (1.0 - a)

    def overlay_view(src, model):
        a = model[:, :, 3:4]
        rgb = src[:, :, :3].copy()
        tint = np.array([0.38, 0.07, 0.015], np.float32)
        return rgb * (1.0 - 0.55 * a) + tint[None, None, :] * (0.55 * a)

    def sheet_shape():
        cell = 512
        lab = 28
        gap = 10
        rows = 3
        canvas = np.zeros((rows * (cell + lab) + (rows + 1) * gap, 3 * cell + 4 * gap, 4), np.float32)
        canvas[:, :, :3] = 0.045
        canvas[:, :, 3] = 1.0
        src_imgs = [imgs["front"], imgs["opposite"], imgs["top"]]
        names = ["SOURCE FRONT", "SOURCE OPPOSITE", "SOURCE TOP"]
        for col, (img, name) in enumerate(zip(src_imgs, names)):
            x = gap + col * (cell + gap)
            y = gap
            draw_text(canvas, x + 4, y + 7, name, 2)
            canvas[y + lab:y + lab + cell, x:x + cell, :3] = cell_view(image_pixels(img))
            canvas[y + lab:y + lab + cell, x:x + cell, 3] = 1.0
        names = ["MODEL CLAY FRONT", "MODEL CLAY OPPOSITE", "MODEL CLAY TOP"]
        for col, (label, name) in enumerate(zip(["front", "opposite", "top"], names)):
            x = gap + col * (cell + gap)
            y = gap + (cell + lab + gap)
            draw_text(canvas, x + 4, y + 7, name, 2)
            canvas[y + lab:y + lab + cell, x:x + cell, :3] = cell_view(load_rgba(render_paths[label]))
            canvas[y + lab:y + lab + cell, x:x + cell, 3] = 1.0
        names = ["OVERLAY FRONT", "OVERLAY OPPOSITE", "OVERLAY TOP"]
        for col, (label, name) in enumerate(zip(["front", "opposite", "top"], names)):
            x = gap + col * (cell + gap)
            y = gap + 2 * (cell + lab + gap)
            draw_text(canvas, x + 4, y + 7, name, 2)
            src = image_pixels(imgs[label]) if label != "top" else image_pixels(imgs["top"])
            out = overlay_view(src, load_rgba(render_paths[label]))
            canvas[y + lab:y + lab + cell, x:x + cell, :3] = out
            canvas[y + lab:y + lab + cell, x:x + cell, 3] = 1.0
        path = OUT / f"comparison_shape_sheet{SUFFIX}.png"
        save_generated_image("Barrel_Comparison_Shape", canvas, path, "sRGB")
        print("SHEET_SAVED", path)
        return path

    def sheet_textured():
        cell = 512
        lab = 28
        gap = 10
        canvas = np.zeros((cell + lab + 2 * gap, 2 * cell + 3 * gap, 4), np.float32)
        canvas[:, :, :3] = 0.045
        canvas[:, :, 3] = 1.0
        draw_text(canvas, gap + 4, gap + 7, "SOURCE TEXTURED 3/4", 2)
        canvas[gap + lab:gap + lab + cell, gap:gap + cell, :3] = cell_view(image_pixels(imgs["textured_three_quarter"]))
        canvas[gap + lab:gap + lab + cell, gap:gap + cell, 3] = 1.0
        draw_text(canvas, 2 * gap + cell + 4, gap + 7, "MODEL TEXTURED 3/4", 2)
        canvas[gap + lab:gap + lab + cell, 2 * gap + cell:2 * gap + 2 * cell, :3] = cell_view(load_rgba(render_paths["textured_three_quarter"]))
        canvas[gap + lab:gap + lab + cell, 2 * gap + cell:2 * gap + 2 * cell, 3] = 1.0
        path = OUT / f"comparison_textured_sheet{SUFFIX}.png"
        save_generated_image("Barrel_Comparison_Textured", canvas, path, "sRGB")
        print("SHEET_SAVED", path)
        return path

    shape_sheet = sheet_shape()
    textured_sheet = sheet_textured()

    report = {
        "model_id": "barrel_img2_01" + SUFFIX,
        "pass": PASS_ID,
        "input_images": source_hashes,
        "image_only_statement": "Only the five allowlisted source images were read for reference; no earlier barrel scripts, checks, GLBs, maps or geometry were opened.",
        "source_image_bytes_unchanged": hashes_before == hashes_after,
        "axes": {
            "up": "+Z",
            "front_model_face": "-Y (chosen design datum; form is rotationally near-symmetric and front/opposite labels are provisional)",
            "front_camera": "at -Y looking +Y; image right +X; image up +Z",
            "opposite_camera": "at +Y looking -Y; image right -X; image up +Z",
            "top_camera": "at +Z looking -Z; image right +X; image up +Y (up direction chosen, not proved by a rotationally symmetric top)"
        },
        "scale": {
            "overall_height": 1.0,
            "classification": "PROVISIONAL normalized pilot scale anchor, not measured physical size",
            "front_pixels_per_unit": 1.0 / s_front,
            "top_pixels_per_unit": 1.0 / s_top,
            "max_body_radius": 0.742,
            "max_body_diameter": 1.484
        },
        "bbox_px_manual": BBOX,
        "pixel_mapping": projections,
        "checkpoint": str(checkpoint),
        "renders": {k: str(v) for k, v in render_paths.items()},
        "sheets": [str(shape_sheet), str(textured_sheet)],
        "inspection": str(snap_path),
        "parts": part_names,
        "health": health,
        "bounds_world": {"min": list(all_min), "max": list(all_max)},
        "materials": [m.name for m in bpy.data.materials],
        "textures": [{"name": i.name, "size": list(i.size), "packed": bool(i.packed_file), "path": i.filepath}
                     for i in (base_img, nrm_img, rgh_img)],
        "reference_planes": [{"name": p.name, "location": list(p.location), "locked": bool(p.lock_location),
                              "hide_render": bool(p.hide_render)} for p in planes],
        "strategy": "Editable radial profile / Screw source, derived closed body, lathe lid, repeated swept hoops and rim strips; stave seams/grain in generated 1024 maps plus shallow normal detail.",
        "limitations": [
            "Front/opposite object orientation is not recoverable from a rotationally symmetric barrel; labels follow filenames and are not claimed as measured facing.",
            "Top-view image up direction and the 3/4 camera pose are chosen approximate visual-guide datums.",
            "The source camera calibration/physical dimensions are unknown; comparisons use separate uniform per-view scales.",
            "Stave seams are material/normal detail, not modeled grooves."
        ],
    }
    report_path = OUT / f"build_report{SUFFIX}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print("BUILD_REPORT", report_path)
    print("COST", json.dumps(snap.get("cost", {}), sort_keys=True))
    print("DONE")


build()
