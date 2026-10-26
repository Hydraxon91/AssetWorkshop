"""Pure-Python regression tests for the round69 UV/texture tooling.

Run with the system interpreter (no numpy, no bpy):
    python3 tools/asset-pipeline/tests/phase8/test_texture_tools.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pipeline import texture_composite as tc  # noqa: E402
from pipeline import uv  # noqa: E402

PALETTE = tc.palette_from_hex({"blue": "#1F5C99", "white": "#F2F2EF", "orange": "#E86A1E"})


def tri(a, b, c):
    return [a, b, c]


class TriangleOverlapTests(unittest.TestCase):
    def test_identical_triangles_overlap_fully(self):
        shape = tri((0.0, 0.0), (0.1, 0.0), (0.0, 0.1))
        self.assertAlmostEqual(uv.triangles_overlap_area(shape, shape),
                               uv._tri_area(shape), places=12)

    def test_disjoint_triangles_do_not_overlap(self):
        first = tri((0.0, 0.0), (0.1, 0.0), (0.0, 0.1))
        second = tri((0.5, 0.5), (0.6, 0.5), (0.5, 0.6))
        self.assertEqual(uv.triangles_overlap_area(first, second), 0.0)

    def test_shared_edge_only_is_not_overlap(self):
        first = tri((0.0, 0.0), (0.1, 0.0), (0.0, 0.1))
        second = tri((0.1, 0.0), (0.1, 0.1), (0.0, 0.1))
        self.assertLess(uv.triangles_overlap_area(first, second), 1e-12)

    def test_degenerate_triangle_is_zero(self):
        flat = tri((0.1, 0.1), (0.2, 0.0), (0.15, 0.05))
        other = tri((0.0, 0.0), (0.3, 0.0), (0.0, 0.3))
        self.assertEqual(uv.triangles_overlap_area(flat, other), 0.0)


class PaletteTests(unittest.TestCase):
    def test_pale_blue_highlight_stays_blue(self):
        # This is the exact failure: a pale blue highlight is nearest to white
        # in RGB, but must not be painted white.
        self.assertEqual(tc.classify_hsv([0.62, 0.74, 0.88]), "blue")

    def test_bright_neutral_stays_white(self):
        self.assertEqual(tc.classify_hsv([0.96, 0.96, 0.95]), "white")

    def test_saturated_orange_stays_orange(self):
        self.assertEqual(tc.classify_hsv([0.91, 0.42, 0.12]), "orange")

    def test_grey_generator_background_is_not_white(self):
        self.assertEqual(tc.classify_hsv([0.69, 0.69, 0.69]), "blue")

    def test_camo_blob_muddy_colour_is_not_orange(self):
        self.assertEqual(tc.classify_hsv([0.55, 0.55, 0.60]), "blue")

    def test_boundary_values_fall_to_blue(self):
        # Thresholds are strict: equality must not silently promote a pixel.
        self.assertEqual(tc.classify_hsv([0.90, 0.90, 0.90]), "blue")
        self.assertEqual(tc.classify_hsv([1.0, 0.97, 0.94]), "blue")
        self.assertEqual(tc.classify_hsv([1.0, 0.72, 0.0]), "blue")
        self.assertEqual(tc.classify_hsv([1.0, 0.12, 0.0]), "blue")


class CompositeTests(unittest.TestCase):
    def test_outside_mask_is_background(self):
        source = [[[0.9, 0.9, 0.9] for _ in range(4)] for _ in range(4)]
        mask = [[False] * 4 for _ in range(4)]
        out = tc.composite_quantised(source, mask, PALETTE, PALETTE["blue"], erosion=0)
        self.assertEqual(out[0][0], PALETTE["blue"])

    def test_inside_mask_is_quantised(self):
        source = [[[0.96, 0.96, 0.95] for _ in range(4)] for _ in range(4)]
        mask = [[False] * 4 for _ in range(4)]
        mask[1][1] = mask[1][2] = mask[2][1] = mask[2][2] = True
        out = tc.composite_quantised(source, mask, PALETTE, PALETTE["blue"], erosion=0)
        self.assertEqual(out[1][1], PALETTE["white"])

    def test_erosion_removes_the_generator_rim(self):
        source = [[[0.95, 0.95, 0.94] for _ in range(6)] for _ in range(6)]
        mask = [[False] * 6 for _ in range(6)]
        for y in range(1, 5):
            for x in range(1, 5):
                mask[y][x] = True
        out = tc.composite_quantised(source, mask, PALETTE, PALETTE["blue"], erosion=1)
        # The generator's pale rim becomes background; the centre survives.
        self.assertEqual(out[1][1], PALETTE["blue"])
        self.assertEqual(out[2][2], PALETTE["white"])

    def test_all_false_mask_with_erosion_is_all_background(self):
        source = [[[0.96, 0.96, 0.95] for _ in range(2)] for _ in range(3)]
        mask = [[False] * 2 for _ in range(3)]
        out = tc.composite_quantised(source, mask, PALETTE, PALETTE["blue"], erosion=2)
        self.assertTrue(all(pixel == PALETTE["blue"] for row in out for pixel in row))

    def test_palette_from_hex_roundtrip(self):
        self.assertAlmostEqual(PALETTE["blue"][0], 0x1F / 255.0, places=6)
        self.assertAlmostEqual(PALETTE["orange"][1], 0x6A / 255.0, places=6)

    def test_erosion_of_thin_mask_removes_everything(self):
        eroded = tc.erode_mask([[False, False, False], [False, True, False],
                                [False, False, False]], iterations=1)
        self.assertFalse(any(any(row) for row in eroded))


if __name__ == "__main__":
    unittest.main(verbosity=2)
