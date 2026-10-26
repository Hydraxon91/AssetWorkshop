"""Pure tests for deterministic shelf packing. No Blender required."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.common import PipelineError
from pipeline.packing import min_pair_gap, pack_to_unit, shelf_pack


class ShelfTests(unittest.TestCase):
    def test_places_without_overlap_and_respects_margin(self):
        rects = [(0.2, 0.1), (0.1, 0.3), (0.25, 0.05), (0.05, 0.05)]
        placements, used = shelf_pack(rects, 1.0, 0.02)
        self.assertEqual(len(placements), len(rects))
        boxes = [(x, y, x + w, y + h) for (x, y), (w, h) in zip(placements, rects)]
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ax0, ay0, ax1, ay1 = boxes[i]
                bx0, by0, bx1, by1 = boxes[j]
                separated = (ax1 <= bx0 + 1e-12 or bx1 <= ax0 + 1e-12
                             or ay1 <= by0 + 1e-12 or by1 <= ay0 + 1e-12)
                self.assertTrue(separated)
        self.assertGreater(used, 0)

    def test_rejects_oversized_rect(self):
        with self.assertRaises(PipelineError):
            shelf_pack([(1.5, 0.1)], 1.0, 0.01)

    def test_rejects_bad_input(self):
        for width, margin in ((0, 0.01), (1.0, -0.01)):
            with self.subTest(width=width, margin=margin):
                with self.assertRaises(PipelineError):
                    shelf_pack([(0.1, 0.1)], width, margin)

    def test_deterministic(self):
        rects = [(0.1, 0.2), (0.3, 0.1), (0.2, 0.2)]
        self.assertEqual(shelf_pack(rects, 1.0, 0.01), shelf_pack(rects, 1.0, 0.01))


class UnitPackTests(unittest.TestCase):
    def assert_gap_and_bounds(self, rects, target):
        placements, scale, achieved = pack_to_unit(rects, target)
        self.assertGreaterEqual(achieved + 1e-9, target)
        self.assertGreaterEqual(min_pair_gap(rects, placements, scale) + 1e-9, target)
        for (x, y), (w, h) in zip(placements, rects):
            self.assertGreaterEqual(x, -1e-12)
            self.assertGreaterEqual(y, -1e-12)
            self.assertLessEqual(x + w * scale, 1.0 + 1e-9)
            self.assertLessEqual(y + h * scale, 1.0 + 1e-9)
        return placements, scale

    def test_gap_meets_target_and_stays_in_bounds(self):
        rects = [(0.3, 0.2), (0.2, 0.4), (0.25, 0.25), (0.1, 0.1), (0.15, 0.35)]
        for target in (0.004, 0.008, 0.012):
            with self.subTest(target=target):
                self.assert_gap_and_bounds(rects, target)

    def test_many_small_rects_still_keep_the_gap(self):
        self.assert_gap_and_bounds([(0.02, 0.02)] * 40, 0.006)

    def test_layout_stays_square_instead_of_one_tall_column(self):
        # 40 identical rects packed into a 1.0-wide bin would make a thin column.
        rects = [(0.02, 0.02)] * 40
        placements, scale = self.assert_gap_and_bounds(rects, 0.006)
        used_w = max(x + w * scale for (x, _), (w, _) in zip(placements, rects))
        used_h = max(y + h * scale for (_, y), (_, h) in zip(placements, rects))
        self.assertLess(abs(used_w - used_h), 0.25)
        self.assertGreater(used_w, 0.6)

    def test_seat_fixture_and_zero_margin(self):
        import json
        data = json.loads(Path(__file__).with_name('seat_01_uv_04_island_rects.json').read_text())
        rects = [r for rows in data['objects'].values() for r in rows]
        self.assertEqual(len(rects), 188)
        _, scale = self.assert_gap_and_bounds(rects, 9 / 2048)
        self.assertGreater(0.0542766403 * scale * scale, 0.40)
        self.assertEqual(pack_to_unit(rects, 9 / 2048), pack_to_unit(rects, 9 / 2048))
        self.assert_gap_and_bounds(rects, 0)

    def test_rejects_impossible_or_bad_input(self):
        for rects, margin in [([(float('nan'), 1)], .01),
                              ([(1, float('inf'))], .01),
                              ([(1, 1)], float('nan')),
                              ([(1,)], .01)]:
            with self.subTest(rects=rects, margin=margin):
                with self.assertRaises(PipelineError):
                    pack_to_unit(rects, margin)
        with self.assertRaises(PipelineError):
            pack_to_unit([], 0.01)
        with self.assertRaises(PipelineError):
            pack_to_unit([(0.1, 0.1)], 0.5)
        with self.assertRaises(PipelineError):
            pack_to_unit([(0.0, 0.1)], 0.01)
        with self.assertRaises(PipelineError):
            pack_to_unit([(0.1, 0.1)], -0.01)

    def test_tight_margin_is_reached_by_shrinking_past_the_clamp(self):
        # Two big rects and a 0.2 margin are only possible if islands also shrink, which
        # in-place shrinking could never do: 3 gaps + 2 islands must fill the sheet.
        rects = [(0.9, 0.9), (0.9, 0.9)]
        placements, scale, achieved = pack_to_unit(rects, 0.2)
        self.assertGreaterEqual(achieved + 1e-9, 0.2)
        self.assertGreaterEqual(min_pair_gap(rects, placements, scale) + 1e-9, 0.2)
        self.assertAlmostEqual(achieved, 0.2, places=3)


if __name__ == '__main__':
    unittest.main()
