"""Shared-sheet packing and conservative global layout validation."""
import math
from types import SimpleNamespace
from .common import PipelineError
from . import uv
from .packing import pack_to_unit, min_pair_gap


def charts(objects, layer_name):
    result = []
    for obj in objects:
        layer = obj.data.uv_layers.get(layer_name)
        if layer is None:
            raise PipelineError(f'{obj.name}: missing UV layer {layer_name}')
        if not obj.data.polygons:
            raise PipelineError(f'{obj.name}: empty mesh')
        for faces in uv.uv_islands(obj.data, layer):
            result.append((obj, faces, uv.island_bounds(obj.data, layer, faces)))
    if not result:
        raise PipelineError('no atlas charts')
    return result


def repack(objects, layer_name, gap_uv):
    rows = charts(objects, layer_name)
    if any(o.data.users > 1 for o in objects):
        raise PipelineError('shared meshes require explicit single-user preparation')
    positions, scale, _ = pack_to_unit(
        [(b[2]-b[0], b[3]-b[1]) for _, _, b in rows], gap_uv)
    for (obj, faces, box), (x, y) in zip(rows, positions):
        layer = obj.data.uv_layers[layer_name]
        for fi in faces:
            for li in obj.data.polygons[fi].loop_indices:
                p = layer.data[li].uv.copy()
                layer.data[li].uv = (x+(p.x-box[0])*scale, y+(p.y-box[1])*scale)
        obj.data.update()
    return {'islands': len(rows), 'uniform_scale': scale}


def validate(objects, layer_name='AtlasUV', resolution=2048, min_gap_px=0):
    """Global triangle intersections plus conservative chart-box gap lower bound.

    Interlocking chart boxes can fail this gate even if true contours are spaced.
    No sampling-based claim of positive clearance is made in that case.
    """
    rows = charts(objects, layer_name)
    data, triangles, areas = [], [], []
    bad_coords = False
    for obj in objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        layer = mesh.uv_layers[layer_name]
        for tri in mesh.loop_triangles:
            ids, points = [], []
            for li in tri.loops:
                p = layer.data[li].uv.copy()
                bad_coords |= not all(math.isfinite(v) and 0 <= v <= 1 for v in p)
                ids.append(len(data))
                points.append(tuple(p))
                data.append(SimpleNamespace(uv=p))
            triangles.append(SimpleNamespace(index=len(triangles), loops=ids))
            areas.append(uv._tri_area(points))
    if bad_coords:
        return {'ok': False, 'failures': ['invalid_or_out_of_bounds_uv']}
    proxy = SimpleNamespace(name='GLOBAL_ATLAS', data=SimpleNamespace(
        uv_layers=SimpleNamespace(get=lambda name: SimpleNamespace(data=data)),
        calc_loop_triangles=lambda: None, loop_triangles=triangles))
    overlaps = uv.island_overlap_report([proxy], layer_name, resolution=resolution)
    boxes = [b for _, _, b in rows]
    gap = min_pair_gap([(b[2]-b[0], b[3]-b[1]) for b in boxes],
                       [(b[0], b[1]) for b in boxes], 1.0)
    failures = []
    if overlaps['truncated']: failures.append('global_overlap_report_truncated')
    if overlaps['total_pairs']: failures.append('global_overlaps_present')
    if any(a <= uv.EPS_AREA for a in areas): failures.append('degenerate_uv_triangles')
    if gap * resolution + 1e-5 < min_gap_px: failures.append('global_box_gap_below_limit')
    return {'ok': not failures, 'failures': failures, 'overlaps': overlaps,
            'islands': len(rows), 'coverage_fraction': sum(areas),
            'gap_lower_bound_px': gap * resolution if math.isfinite(gap) else None,
            'gap_method': 'global_chart_bounding_boxes',
            'degenerate_triangles': sum(a <= uv.EPS_AREA for a in areas)}


def corner_snapshot(objects, layer_name):
    """Exact indexed mesh/UV corner correspondence, not merely UV bounds."""
    return {o.name: {
        'vertices': [tuple(v.co) for v in o.data.vertices],
        'edges': [tuple(e.vertices) for e in o.data.edges],
        'faces': [tuple(p.vertices) for p in o.data.polygons],
        'loops': [l.vertex_index for l in o.data.loops],
        'uv': [tuple(v.uv) for v in o.data.uv_layers[layer_name].data],
        'matrix': [tuple(r) for r in o.matrix_world],
    } for o in objects}
