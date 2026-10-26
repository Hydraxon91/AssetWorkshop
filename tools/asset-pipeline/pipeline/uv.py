"""UV preparation and UV-space diagnostics."""
from __future__ import annotations

import math

from .common import PipelineError


def material_of(obj, index):
    slots = obj.material_slots
    if index >= len(slots):
        return None
    return slots[index].material


def image_texture_nodes(material):
    if material is None or not material.node_tree:
        return []
    return [node for node in material.node_tree.nodes if node.type == "TEX_IMAGE"]


def uv_layers(obj):
    return [layer.name for layer in obj.data.uv_layers]


def ensure_source_uv(obj, active_name="AtlasUV"):
    """Preserve the current UV layout under SourceUV, then add a fresh atlas layer."""
    mesh = obj.data
    source = None
    for layer in mesh.uv_layers:
        if layer.name != active_name:
            source = layer
            break
    if source is None:
        if not mesh.uv_layers:
            mesh.uv_layers.new(name="SourceUV")
        source = mesh.uv_layers[0]
    if source.name != "SourceUV":
        source.name = "SourceUV"
    atlas = mesh.uv_layers.get(active_name) or mesh.uv_layers.new(name=active_name)
    mesh.uv_layers.active = atlas
    atlas.active_render = True
    return source, atlas


def smart_unwrap(obj, margin=0.02, angle_degrees=66.0):
    import bpy

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if obj.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle_degrees),
                             island_margin=margin, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def point_image_textures_to_source_uv(obj, source_name="SourceUV"):
    """Make existing texture chains sample the preserved layout, not the atlas."""
    for slot in obj.material_slots:
        material = slot.material
        nodes = image_texture_nodes(material)
        if not nodes:
            continue
        tree = material.node_tree
        uvmap = next((n for n in tree.nodes if n.type == "UVMAP"), None)
        if uvmap is None:
            uvmap = tree.nodes.new("ShaderNodeUVMap")
            uvmap.uv_map = source_name
            uvmap.location = (-900, -300)
        else:
            uvmap.uv_map = source_name
        for node in nodes:
            if not node.inputs["Vector"].is_linked:
                tree.links.new(uvmap.outputs["UV"], node.inputs["Vector"])


def uv_bounds(obj, layer_name):
    layer = obj.data.uv_layers.get(layer_name)
    if layer is None:
        raise PipelineError(f"{obj.name} has no UV layer {layer_name}")
    xs = [value.uv.x for value in layer.data]
    ys = [value.uv.y for value in layer.data]
    return [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)]


def padding_pixels(objects, layer_name, resolution):
    """Nearest-neighbour island gap in pixels, sampled from UV-space rasterisation.

    This is a diagnostic, not a gate: it reports the smallest gap between faces that
    do not share vertices at the given resolution.
    """
    import numpy as np

    owner = np.full((resolution, resolution), -1, dtype=np.int32)
    filled = np.zeros((resolution, resolution), dtype=bool)
    for index, obj in enumerate(objects):
        layer = obj.data.uv_layers.get(layer_name)
        if layer is None:
            continue
        for poly in obj.data.polygons:
            coords = [layer.data[i].uv for i in poly.loop_indices]
            px = [int(min(max(round(c.x * (resolution - 1)), 0), resolution - 1)) for c in coords]
            py = [int(min(max(round((1 - c.y) * (resolution - 1)), 0), resolution - 1)) for c in coords]
            from .bake import raster_triangle  # shared rasteriser

            mask = raster_triangle(px, py, resolution)
            owner[mask] = index
            filled |= mask
    if not filled.any():
        return {"resolution": resolution, "min_gap_px": None, "note": "no UV area"}
    return {
        "resolution": resolution,
        "filled_pixels": int(filled.sum()),
        "coverage": round(float(filled.mean()), 4),
        "min_gap_px": None,
        "note": "raster coverage only; inter-island gap requires island separation",
    }


def uv_report(objects, layer_name="AtlasUV"):
    payload = {"layer": layer_name, "objects": []}
    for obj in objects:
        bounds = uv_bounds(obj, layer_name)
        out_of_bounds = (bounds[0] < -1e-4 or bounds[1] < -1e-4 or
                         bounds[2] > 1 + 1e-4 or bounds[3] > 1 + 1e-4)
        payload["objects"].append({
            "object": obj.name,
            "faces": len(obj.data.polygons),
            "uv_bounds": bounds,
            "out_of_bounds": out_of_bounds,
        })
    payload["out_of_bounds"] = any(item["out_of_bounds"] for item in payload["objects"])
    return payload


# ---------------------------------------------------------------------------
# Island geometry, overlap and packing checks (round69 hardening)
#
# These exist because two silent failure modes cost a full round:
#   * bpy.ops.uv.pack_islands reported FINISHED while moving already-disjoint
#     islands on top of each other;
#   * a capped overlap list (64 pairs) hid 72,744 real pairs and looked benign.
# Every function here returns numbers, and anything capped says so.
# ---------------------------------------------------------------------------

EPS_AREA = 1e-12


def _tri_area(tri):
    ax, ay = tri[0]
    bx, by = tri[1]
    cx, cy = tri[2]
    return abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax)) * 0.5


def _clip_area(subject, clip):
    """Positive intersection area of two triangles (Sutherland-Hodgman)."""
    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    if cross(*clip) < 0:
        clip = list(reversed(clip))
    polygon = list(subject)
    for index, a in enumerate(clip):
        b = clip[(index + 1) % len(clip)]
        output = []
        for j, end in enumerate(polygon):
            start = polygon[j - 1]
            ds, de = cross(a, b, start), cross(a, b, end)
            if (ds >= 0) != (de >= 0) and ds != de:
                t = ds / (ds - de)
                output.append((start[0] + t * (end[0] - start[0]),
                               start[1] + t * (end[1] - start[1])))
            if de >= 0:
                output.append(end)
        polygon = output
        if not polygon:
            return 0.0
    return abs(sum(polygon[i - 1][0] * p[1] - p[0] * polygon[i - 1][1]
                   for i, p in enumerate(polygon))) * 0.5


def triangles_overlap_area(first, second):
    """Intersection area in UV units; edge contact returns 0.0."""
    if _tri_area(first) <= EPS_AREA or _tri_area(second) <= EPS_AREA:
        return 0.0
    lox = max(min(p[0] for p in first), min(p[0] for p in second))
    hix = min(max(p[0] for p in first), max(p[0] for p in second))
    loy = max(min(p[1] for p in first), min(p[1] for p in second))
    hiy = min(max(p[1] for p in first), max(p[1] for p in second))
    if hix <= lox or hiy <= loy:
        return 0.0
    return _clip_area(first, second)


def uv_islands(mesh, layer):
    """Faces connected across shared UV edges, as a list of face-index lists."""
    parent = list(range(len(mesh.polygons)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    edges = {}
    for polygon in mesh.polygons:
        loops = list(polygon.loop_indices)
        for i, li in enumerate(loops):
            lj = loops[(i + 1) % len(loops)]
            key = tuple(sorted((
                (mesh.loops[li].vertex_index, (round(layer.data[li].uv.x, 7),
                                               round(layer.data[li].uv.y, 7))),
                (mesh.loops[lj].vertex_index, (round(layer.data[lj].uv.x, 7),
                                               round(layer.data[lj].uv.y, 7))))))
            edges.setdefault(key, []).append(polygon.index)
    for faces in edges.values():
        for other in faces[1:]:
            ra, rb = find(faces[0]), find(other)
            if ra != rb:
                parent[rb] = ra
    groups = {}
    for polygon in mesh.polygons:
        groups.setdefault(find(polygon.index), []).append(polygon.index)
    return list(groups.values())


def island_bounds(mesh, layer, faces):
    coords = [layer.data[k].uv for f in faces for k in mesh.polygons[f].loop_indices]
    return (min(c.x for c in coords), min(c.y for c in coords),
            max(c.x for c in coords), max(c.y for c in coords))


def _boxes_overlap(first, second):
    return (first[0] < second[2] and second[0] < first[2]
            and first[1] < second[3] and second[1] < first[3])


def island_overlap_report(objects, layer_name="AtlasUV", resolution=2048,
                          max_pairs=200000):
    """Positive-area overlap summary with a high default cap and explicit truncation.

    Separate objects own separate 0-1 spaces, so pairs are only compared within
    one object. ``truncated`` is explicit so a capped result cannot read as clean.
    """
    payload = {"layer": layer_name, "resolution": resolution, "objects": [],
               "total_pairs": 0, "total_px2": 0.0, "truncated": False}
    px2 = float(resolution * resolution)
    for obj in objects:
        layer = obj.data.uv_layers.get(layer_name)
        if layer is None:
            continue
        mesh = obj.data
        mesh.calc_loop_triangles()
        triangles = []
        for tri in mesh.loop_triangles:
            points = [(layer.data[k].uv.x, layer.data[k].uv.y) for k in tri.loops]
            if _tri_area(points) <= EPS_AREA:
                continue
            triangles.append((tri.index, points))
        cells = {}
        pairs = {}
        for tri_index, points in triangles:
            lo = [min(p[0] for p in points), min(p[1] for p in points)]
            hi = [max(p[0] for p in points), max(p[1] for p in points)]
            keys = [(x, y)
                    for x in range(int(max(0.0, lo[0]) * 64), min(63, int(min(1.0, hi[0]) * 64)) + 1)
                    for y in range(int(max(0.0, lo[1]) * 64), min(63, int(min(1.0, hi[1]) * 64)) + 1)]
            for key in keys:
                for other_index, other_points in cells.get(key, ()):
                    pair = (min(tri_index, other_index), max(tri_index, other_index))
                    if pair in pairs:
                        continue
                    area = triangles_overlap_area(points, other_points)
                    if area > EPS_AREA:
                        pairs[pair] = area
                        if len(pairs) >= max_pairs:
                            payload["truncated"] = True
                            break
                if payload["truncated"]:
                    break
                cells.setdefault(key, []).append((tri_index, points))
            if payload["truncated"]:
                break
        total = sum(pairs.values())
        largest = max(pairs.values(), default=0.0)
        payload["objects"].append({
            "object": obj.name, "triangles": len(triangles), "pairs": len(pairs),
            "total_px2": total * px2, "largest_pair_px2": largest * px2,
            "fraction_of_sheet": total, "truncated": payload["truncated"],
        })
        payload["total_pairs"] += len(pairs)
        payload["total_px2"] += total * px2
    return payload


def min_island_gap(objects, layer_name="AtlasUV", step_uv=0.002):
    """Measured smallest gap between UV islands; None distances are skipped."""
    from mathutils import kdtree

    results = {"layer": layer_name, "step_uv": step_uv, "objects": []}
    best_overall = None
    for obj in objects:
        layer = obj.data.uv_layers.get(layer_name)
        if layer is None:
            continue
        mesh = obj.data
        islands = uv_islands(mesh, layer)
        island_points = []
        for faces in islands:
            segments = set()
            for face in faces:
                loops = list(mesh.polygons[face].loop_indices)
                for i, li in enumerate(loops):
                    lj = loops[(i + 1) % len(loops)]
                    a, b = layer.data[li].uv, layer.data[lj].uv
                    if abs(a.x - b.x) < 1e-9 and abs(a.y - b.y) < 1e-9:
                        continue
                    segments.add(tuple(sorted(((round(a.x, 7), round(a.y, 7)),
                                               (round(b.x, 7), round(b.y, 7))))))
            points = []
            for (ax, ay), (bx, by) in segments:
                length = math.hypot(bx - ax, by - ay)
                count = max(1, int(math.ceil(length / step_uv)))
                for index in range(count + 1):
                    t = index / count
                    points.append((ax + (bx - ax) * t, ay + (by - ay) * t))
            island_points.append(points)
        best = None
        for left in range(len(island_points)):
            for right in range(left + 1, len(island_points)):
                tree = kdtree.KDTree(len(island_points[right]))
                for index, point in enumerate(island_points[right]):
                    tree.insert((point[0], point[1], 0.0), index)
                tree.balance()
                for point in island_points[left]:
                    _, _, distance = tree.find((point[0], point[1], 0.0))
                    if distance is None:
                        continue
                    if best is None or distance < best:
                        best = distance
        results["objects"].append({"object": obj.name, "islands": len(islands),
                                   "min_gap_uv": best,
                                   "min_gap_px_1024": None if best is None else best * 1024,
                                   "min_gap_px_2048": None if best is None else best * 2048})
        if best is not None and (best_overall is None or best < best_overall):
            best_overall = best
    results["min_gap_uv"] = best_overall
    results["min_gap_px_2048"] = None if best_overall is None else best_overall * 2048
    return results


def ensure_island_gaps(obj, layer_name="AtlasUV", margin=0.008):
    """Shrink each island about its own centre instead of repacking.

    ``bpy.ops.uv.pack_islands`` is not used: in background Blender it reported
    FINISHED while creating overlapping islands. Real gaps are measured after.
    """
    layer = obj.data.uv_layers.get(layer_name)
    if layer is None:
        raise PipelineError(f"{obj.name} has no UV layer {layer_name}")
    mesh = obj.data
    islands = uv_islands(mesh, layer)
    factors = []
    for faces in islands:
        x0, y0, x1, y1 = island_bounds(mesh, layer, faces)
        largest = max(x1 - x0, y1 - y0)
        if largest <= 1e-9:
            factors.append({"faces": len(faces), "factor": 1.0, "reason": "degenerate"})
            continue
        factor = min(1.0, max(0.5, 1.0 - (2.0 * margin) / largest))
        cx, cy = (x0 + x1) * 0.5, (y0 + y1) * 0.5
        loops = {loop for face in faces for loop in mesh.polygons[face].loop_indices}
        for index in loops:
            uv = layer.data[index].uv
            uv.x = cx + (uv.x - cx) * factor
            uv.y = cy + (uv.y - cy) * factor
        factors.append({"faces": len(faces), "factor": round(factor, 6)})
    if not factors:
        return {"object": obj.name, "islands": 0, "margin_requested": margin,
                "min_factor": None, "measured_gap_uv": None,
                "measured_gap_px_2048": None, "factors": [],
                "note": "no UV islands (empty mesh); nothing to space"}
    gap = min_island_gap([obj], layer_name, step_uv=max(margin / 4.0, 0.0005))
    return {"object": obj.name, "islands": len(islands),
            "margin_requested": margin, "min_factor": min(f["factor"] for f in factors),
            "measured_gap_uv": gap["min_gap_uv"],
            "measured_gap_px_2048": gap["min_gap_px_2048"],
            "factors": factors}


def pack_islands_checked(obj, layer_name="AtlasUV", margin=0.008, pack=None):
    """Run pack_islands, then fail if packing added island-box overlaps.

    The default packer restores Object mode itself and the wrapper also verifies
    and restores it, because ``bpy.ops.object.mode_set`` acts on the *active*
    object: a packer that hands active away can otherwise leave this object in
    Edit mode with no error. Operator context failures and a packer that raises
    IndexError/ValueError during the UV data swap are reported as PipelineError.
    """
    import bpy

    if obj.data.uv_layers.get(layer_name) is None:
        raise PipelineError(f"{obj.name} has no UV layer {layer_name}")
    mesh = obj.data
    view_layer = bpy.context.view_layer
    previous_active = view_layer.objects.active
    previous_selection = [item for item in view_layer.objects if item.select_get()]

    def measure():
        # Re-acquire the layer: the pointer from before a mode switch can go stale
        # (bpy_prop_collection index errors) even though the layer still exists.
        layer = mesh.uv_layers[layer_name]
        return [island_bounds(mesh, layer, faces) for faces in uv_islands(mesh, layer)]

    def overlaps(current):
        count = 0
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                if _boxes_overlap(current[i], current[j]):
                    count += 1
        return count

    def override():
        """Operator context bound to this object, independent of the active one."""
        return bpy.context.temp_override(active_object=obj, object=obj,
                                         selected_objects=[obj],
                                         selected_editable_objects=[obj])

    def to_object_mode():
        """Leave Edit mode on THIS object, whatever is currently active."""
        if obj.mode == "OBJECT":
            return
        try:
            if view_layer.objects.active is not obj:
                view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            with override():
                bpy.ops.object.mode_set(mode="OBJECT")

    def default_pack():
        with override():
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.select_all(action="SELECT")
            try:
                return bpy.ops.uv.pack_islands(rotate=True, margin=margin,
                                               margin_method="FRACTION",
                                               shape_method="CONCAVE", scale=True)
            finally:
                if obj.mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")

    runner = pack or default_pack
    try:
        to_object_mode()                      # measure needs Object-mode UV data
        before = overlaps(measure())
        result = runner()
        left_edit_mode = obj.mode != "OBJECT"
        to_object_mode()                      # a custom packer may have left Edit mode
        if left_edit_mode:
            raise PipelineError("packer left %s in %s mode; it must restore Object mode"
                                % (obj.name, "EDIT"))
        after = overlaps(measure())
    except (RuntimeError, IndexError, ValueError) as exc:
        raise PipelineError("pack_islands_checked could not complete for %s: %s: %s"
                            % (obj.name, type(exc).__name__, exc))
    finally:
        try:
            to_object_mode()
        except RuntimeError:
            pass
        # Restore the user's selection/active object if they still exist.
        for item in previous_selection:
            if item.name in view_layer.objects:
                item.select_set(True)
        if previous_active is not None and previous_active.name in view_layer.objects:
            view_layer.objects.active = previous_active
        else:
            view_layer.objects.active = obj

    report = {"object": obj.name,
              "operator_result": sorted(result) if isinstance(result, set) else result,
              "box_overlaps_before": before, "box_overlaps_after": after,
              "regressed": after > before}
    if after > before:
        raise PipelineError(
            "pack_islands introduced island overlaps (%d -> %d); keep the unwrap result and "
            "use ensure_island_gaps instead: %r" % (before, after, report))
    return report
