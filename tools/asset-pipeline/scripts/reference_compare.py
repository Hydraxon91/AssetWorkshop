"""Shared pixel frame for a reference plane, matched camera and contour overlays.

Reuses reference_sheet's axis/UV conventions; never infers calibration from color
or treats a perspective illustration as an orthographic measurement. Pure frame
math needs only stdlib. Overlay arrays use Blender's bottom-left pixel layout and
NumPy already shipped with Blender. This module never edits a Blender scene.
"""
from dataclasses import dataclass
import math

from reference_sheet import plane_geometry


@dataclass(frozen=True)
class ReferenceFrame:
    width: int
    height: int
    origin_px: tuple
    mm_per_px: float
    projection: str = 'side'

    def __post_init__(self):
        for value in (self.width, self.height):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError('positive integer pixel dimensions required')
        if (isinstance(self.mm_per_px, bool) or
                not math.isfinite(self.mm_per_px) or self.mm_per_px <= 0):
            raise ValueError('one positive uniform mm_per_px required')
        if (len(self.origin_px) != 2 or
                not all(math.isfinite(x) for x in self.origin_px) or
                not 0 <= self.origin_px[0] <= self.width or
                not 0 <= self.origin_px[1] <= self.height):
            raise ValueError('origin must be inside the image; top-left coordinates')
        if self.projection not in ('front', 'side', 'top'):
            raise ValueError('unsupported projection')

    def geometry(self):
        return plane_geometry({'name': 'comparison', 'projection': self.projection,
                               'rect': [0, 0, self.width, self.height],
                               'origin_px': list(self.origin_px)}, self.mm_per_px)

    def pixel_to_world_mm(self, u, v):
        g = self.geometry()
        a, b, _, d = g['corners_mm']
        return tuple(a[i] + u / self.width * (b[i] - a[i]) +
                     v / self.height * (d[i] - a[i]) for i in range(3))

    def world_to_pixel_mm(self, point):
        g = self.geometry()
        a, b, _, d = g['corners_mm']
        right = [b[i] - a[i] for i in range(3)]
        down = [d[i] - a[i] for i in range(3)]
        rel = [point[i] - a[i] for i in range(3)]
        return (sum(rel[i] * right[i] for i in range(3)) /
                sum(x*x for x in right) * self.width,
                sum(rel[i] * down[i] for i in range(3)) /
                sum(x*x for x in down) * self.height)

    def camera_spec_mm(self, distance=1000):
        if not math.isfinite(distance) or distance <= 0:
            raise ValueError('positive camera distance required')
        centre = self.pixel_to_world_mm(self.width / 2, self.height / 2)
        normal = self.geometry()['normal']
        return {'target_mm': centre,
                'position_mm': tuple(centre[i] + normal[i] * distance for i in range(3)),
                'up': (1, 0, 0) if self.projection == 'top' else (0, 0, 1),
                'ortho_scale_mm': max(self.width, self.height) * self.mm_per_px,
                'resolution': (self.width, self.height)}

    def validate_plane_size(self, width_mm, height_mm, tolerance=1e-4):
        expected = (self.width*self.mm_per_px, self.height*self.mm_per_px)
        if any(abs(actual-want) > tolerance for actual, want in
               zip((width_mm, height_mm), expected)):
            raise ValueError('plane size disagrees with shared pixel frame')
        return True


def contour_overlay(reference_rgba, model_alpha, fill=0.12):
    """Readable green model contour over reference, no rescale/translation.

    Both inputs MUST already share resolution/framing and bottom-left row order.
    The model alpha is used only as a mask, avoiding color/premultiplication drift.
    """
    import numpy as np
    ref = np.asarray(reference_rgba, dtype=np.float32)
    alpha = np.asarray(model_alpha, dtype=np.float32)
    if ref.ndim != 3 or ref.shape[2] != 4 or alpha.shape != ref.shape[:2]:
        raise ValueError('RGBA reference and same-size 2D alpha required')
    if not 0 <= fill <= 1:
        raise ValueError('fill must be in [0,1]')
    mask = alpha > 0.5
    padded = np.pad(mask, 1)
    interior = (mask & padded[:-2, 1:-1] & padded[2:, 1:-1] &
                padded[1:-1, :-2] & padded[1:-1, 2:])
    edge = mask & ~interior
    out = ref.copy()
    color = np.array([0.02, 0.85, 0.2], dtype=np.float32)
    out[mask, :3] = (1-fill)*out[mask, :3] + fill*color
    out[edge, :3] = color
    out[:, :, 3] = 1
    return out
