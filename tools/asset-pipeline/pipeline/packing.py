"""Tested fixed-sheet rectangle packer; positions/gutters are final UV units.

Core used by pipeline.py's explicit `pack:true` UV mode. Bounding boxes waste
space inside concave islands; this is not shape nesting or a texel-density solver.
"""
import math
from .common import PipelineError


def shelf_pack(rects, width, margin):
    if not math.isfinite(width) or width <= 0 or not math.isfinite(margin) or margin < 0:
        raise PipelineError('invalid bin or margin')
    order = sorted(range(len(rects)), key=lambda i: (-rects[i][1], -rects[i][0], i))
    positions = [None] * len(rects)
    x = y = margin
    height = 0.0
    for i in order:
        w, h = rects[i]
        if w + 2 * margin > width + 1e-12:
            raise PipelineError('rectangle wider than bin')
        if x + w + margin > width + 1e-12:
            y += height + margin
            x, height = margin, 0.0
        positions[i] = (x, y)
        x += w + margin
        height = max(height, h)
    return positions, y + height + margin


def pack_to_unit(rects, target_margin):
    """Search uniform size in deterministic fixed shelves; no rotation/distortion.

    Binary search changes sizes only, never gutters. Returned positions are
    final UV coordinates; scale multiplies original rectangle dimensions.
    """
    if not rects or not math.isfinite(target_margin) or not 0 <= target_margin < 0.5:
        raise PipelineError('invalid rectangles or margin')
    if any(len(r) != 2 for r in rects):
        raise PipelineError('each rectangle requires width and height')
    if any(not math.isfinite(v) or v <= 0 for r in rects for v in r):
        raise PipelineError('rectangle dimensions must be finite and positive')
    lo = 0.0
    hi = (1 - 2 * target_margin) / max(max(r) for r in rects)
    best = None
    for _ in range(60):
        scale = (lo + hi) / 2
        scaled = [(w * scale, h * scale) for w, h in rects]
        positions, used = shelf_pack(scaled, 1.0, target_margin)
        if used <= 1.0:
            lo, best = scale, positions
        else:
            hi = scale
    if best is None or lo <= 1e-12:
        raise PipelineError('no positive scale fits the requested gutter')
    return best, lo, target_margin


def min_pair_gap(rects, placements, scale):
    boxes = [(x, y, x + w * scale, y + h * scale)
             for (x, y), (w, h) in zip(placements, rects)]
    best = math.inf
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            dx = max(b[0] - a[2], a[0] - b[2], 0.0)
            dy = max(b[1] - a[3], a[1] - b[3], 0.0)
            best = min(best, max(dx, dy))
    return best
