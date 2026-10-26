"""Rebuild the watering-can spout as an outline-driven horn.

Reads the traced reference contours stored on CF_Spout_Surface and lofts a
surface whose side silhouette follows them. Sections lie in planes PERPENDICULAR
to the local axis (the previous attempt built them in a plane containing the
axis, which produced a ribbon). Saves nothing: the caller saves.

Run inside the live scene with:
    import runpy; runpy.run_path(<this file>, run_name="__main__")
"""
import json

import bpy
from mathutils import Vector, Matrix

ROOT = "Model_Control"
SRC_NAMES = ("CF_Spout_Surface", "CF_Spout_Surface_superseded")
NEW = "CF_Spout_Horn"
RING = 32
MATERIAL = "CF_Clay"

# Calibrated reference mapping (mm), from reference_record_orientation_fixed.json
U0, V0, MMPX = 220.0, 315.0, 1.0996309963


def world_mm(u, v):
    """Reference pixel -> world point (metres) on the X=0 median plane."""
    y = (U0 - u) * MMPX
    z = (V0 - v) * MMPX
    return Vector((0.0, y / 1000.0, z / 1000.0))


def load_contours():
    src = None
    for name in SRC_NAMES:
        src = bpy.data.objects.get(name)
        if src is not None:
            break
    if src is None:
        raise SystemExit("BLOCKED: no traced contour source object found")
    up = json.loads(src["traced_px_upper"])
    lo = json.loads(src["traced_px_lower"])
    if len(up) != len(lo):
        raise SystemExit("contour length mismatch: %d vs %d" % (len(up), len(lo)))
    # The trace runs rose -> body junction; the loft needs junction -> rose so
    # that index 0 is the buried root and the last ring is the rose face.
    return list(reversed(up)), list(reversed(lo))


def smooth(values, window=5):
    n = len(values)
    half = window // 2
    out = []
    for i in range(n):
        lo_i = max(0, i - half)
        hi_i = min(n, i + half + 1)
        chunk = values[lo_i:hi_i]
        out.append(sum(chunk) / len(chunk))
    return out


def stations(up, lo):
    pts = []
    radii = []
    for (u1, v1), (u2, v2) in zip(up, lo):
        a = world_mm(u1, v1)
        b = world_mm(u2, v2)
        pts.append((a + b) * 0.5)
        radii.append((a - b).length * 0.5)
    radii = smooth(radii, 5)

    # Root: extend into the body so the cap is buried inside the shell.
    t0 = (pts[0] - pts[1]).normalized()
    for back, grow in ((0.026, 1.06), (0.016, 1.05), (0.008, 1.02)):
        pts.insert(0, pts[0] + t0 * back)
        radii.insert(0, radii[0] * grow)

    # Head: a short rolled rim then a face disc.
    t1 = (pts[-1] - pts[-2]).normalized()
    base_r = radii[-1]
    for fwd, scale in ((0.004, 1.05), (0.007, 0.95), (0.009, 0.80)):
        pts.append(pts[-1] + t1 * fwd)
        radii.append(base_r * scale)
    return pts, radii


def frame(p_prev, p_next):
    t = (p_next - p_prev).normalized()
    n0 = t.cross(Vector((1.0, 0.0, 0.0)))
    if n0.length < 1e-6:
        n0 = t.cross(Vector((0.0, 1.0, 0.0)))
    n0.normalize()
    n1 = t.cross(n0).normalized()
    return n0, n1


def build(up, lo):
    ctrl = bpy.data.objects[ROOT]
    inv = ctrl.matrix_world.inverted()
    pts, radii = stations(up, lo)

    verts = []
    for i, (p, r) in enumerate(zip(pts, radii)):
        prev = pts[i - 1] if i > 0 else pts[i]
        nxt = pts[i + 1] if i < len(pts) - 1 else pts[i]
        n0, n1 = frame(prev, nxt)
        for k in range(RING):
            ang = 2.0 * 3.141592653589793 * k / RING
            q = p + (n0 * (r * __import__("math").cos(ang)) +
                     n1 * (r * __import__("math").sin(ang)))
            verts.append(inv @ q)

    faces = []
    for i in range(len(pts) - 1):
        a = i * RING
        b = (i + 1) * RING
        for k in range(RING):
            k2 = (k + 1) % RING
            faces.append((a + k, a + k2, b + k2, b + k))
    faces.append(tuple(range(RING - 1, -1, -1)))                 # root cap
    tip = (len(pts) - 1) * RING
    faces.append(tuple(tip + k for k in range(RING)))            # rose face

    me = bpy.data.meshes.new(NEW)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.validate()
    me.update()
    for poly in me.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(NEW, me)
    coll = bpy.data.collections.get("CF_Assembly_01") or bpy.context.scene.collection
    coll.objects.link(obj)
    mat = bpy.data.materials.get(MATERIAL)
    if mat:
        me.materials.append(mat)
    obj.parent = ctrl
    obj.parent_type = "OBJECT"
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_world = ctrl.matrix_world
    obj.hide_render = False
    obj.hide_viewport = False
    obj["construction"] = ("outline-driven loft: sections perpendicular to the local "
                           "axis, half-width from the traced reference contours; "
                           "rolled rim + face disc; no bore/holes")
    obj["section_count"] = len(pts)
    obj["radius_mm"] = [round(1000.0 * r, 2) for r in radii]
    return obj, pts, radii


def supersede():
    for name in SRC_NAMES:
        old = bpy.data.objects.get(name)
        if old is not None:
            if not name.endswith("_superseded"):
                old.name = SRC_NAMES[1]
            old.hide_render = True
            old.hide_viewport = True
            break
    for name in ("CF_Spout_Path", "CF_Spout_Taper"):
        o = bpy.data.objects.get(name)
        if o:
            o.hide_render = True
            o.hide_viewport = True


def main():
    existing = bpy.data.objects.get(NEW)
    if existing is not None:
        # Rebuild: retire the previous attempt instead of refusing.
        existing.name = NEW + "_superseded"
        existing.hide_render = True
        existing.hide_viewport = True
    up, lo = load_contours()          # read BEFORE the source is renamed
    supersede()
    obj, pts, radii = build(up, lo)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    nt = 0
    try:
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        nv = len(me.vertices)
    finally:
        ev.to_mesh_clear()
    lo_mm = min(1000.0 * r for r in radii)
    hi_mm = max(1000.0 * r for r in radii)
    print("SPOUT_HORN_OK " + json.dumps({
        "object": obj.name,
        "sections": len(pts),
        "verts": nv,
        "tris": nt,
        "radius_mm_min": round(lo_mm, 2),
        "radius_mm_max": round(hi_mm, 2),
        "diameter_mm_root": round(2000.0 * radii[0], 1),
        "diameter_mm_tip": round(2000.0 * radii[-1], 1),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
