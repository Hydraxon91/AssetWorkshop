"""Masked compositing and palette quantisation for generated texture atlases.

Pure list-based helpers (no numpy, no bpy) so they can be unit-tested with the
system interpreter. Images are lists of rows; each pixel is an [r, g, b] float
list in sRGB 0-1; masks are lists of boolean rows.

Why this module exists: the truck livery needed four hand-rolled variants.
Nearest-RGB quantisation turned pale highlights into white hairlines, and
straight compositing let generated gradients bleed into panels. HSV
classification with a rim erosion fixed both, so it lives here with tests.
"""
from __future__ import annotations


def rgb_to_hsv(rgb):
    r, g, b = rgb
    high = max(rgb)
    low = min(rgb)
    delta = high - low
    if delta <= 1e-9:
        hue = 0.0
    elif high == r:
        hue = ((g - b) / delta) % 6.0
    elif high == g:
        hue = (b - r) / delta + 2.0
    else:
        hue = (r - g) / delta + 4.0
    hue /= 6.0
    saturation = 0.0 if high <= 1e-9 else delta / high
    return hue, saturation, high


def classify_hsv(rgb, white_max_saturation=0.06, white_min_value=0.90,
                 orange_hue=(0.02, 0.12), orange_min_saturation=0.45,
                 orange_min_value=0.45):
    """Return 'white', 'orange' or 'blue' for one sRGB pixel."""
    hue, saturation, value = rgb_to_hsv(rgb)
    if saturation < white_max_saturation and value > white_min_value:
        return "white"
    if (orange_hue[0] < hue < orange_hue[1]
            and saturation > orange_min_saturation and value > orange_min_value):
        return "orange"
    return "blue"


def erode_mask(mask, iterations=2):
    """Shrink a boolean mask; edges become False."""
    height = len(mask)
    width = len(mask[0]) if height else 0
    current = [list(row) for row in mask]
    for _ in range(max(0, iterations)):
        nxt = [[False] * width for _ in range(height)]
        for y in range(height):
            for x in range(width):
                if not current[y][x]:
                    continue
                if (x == 0 or y == 0 or x == width - 1 or y == height - 1):
                    continue
                nxt[y][x] = (current[y - 1][x] and current[y + 1][x]
                             and current[y][x - 1] and current[y][x + 1])
        current = nxt
    return current


def composite_quantised(source, mask, palette, background, erosion=2):
    """Fill the canvas with ``background``; paint quantised source inside the mask.

    ``palette`` maps names to rgb rows, e.g. {"blue": [...], "white": [...],
    "orange": [...]}. ``background`` is usually the blue paint colour so any gap
    reads as paint rather than as the generator's canvas.
    """
    height = len(source)
    width = len(source[0]) if height else 0
    inner = erode_mask(mask, erosion) if erosion else [list(row) for row in mask]
    out = []
    for y in range(height):
        row = []
        for x in range(width):
            if inner[y][x]:
                row.append(list(palette[classify_hsv(source[y][x])]))
            else:
                row.append(list(background))
        out.append(row)
    return out


def palette_from_hex(mapping):
    """{'blue': '#1F5C99', ...} -> {'blue': [0.121, 0.361, 0.600], ...}"""
    def parse(value):
        text = value.lstrip("#")
        return [int(text[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return {name: parse(value) for name, value in mapping.items()}
