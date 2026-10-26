"""Frame math regression tests, no Blender or external dependencies."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reference_compare import ReferenceFrame


class FrameTests(unittest.TestCase):
    def test_origin_and_roundtrip_all_projections(self):
        for projection in ('side', 'front', 'top'):
            f = ReferenceFrame(402, 327, (219, 314), 298/270, projection)
            self.assertEqual(f.pixel_to_world_mm(219, 314), (0, 0, 0))
            for p in [(0, 0), (402, 327), (19.25, 93.5), (219, 314)]:
                result = f.world_to_pixel_mm(f.pixel_to_world_mm(*p))
                for a, b in zip(p, result):
                    self.assertAlmostEqual(a, b)

    def test_camera_matches_plane(self):
        f = ReferenceFrame(402, 327, (219, 314), 1.1)
        c = f.camera_spec_mm()
        self.assertAlmostEqual(c['ortho_scale_mm'], 442.2)
        self.assertAlmostEqual(c['position_mm'][0], -1000)
        self.assertTrue(f.validate_plane_size(442.2, 359.7))

    def test_old_mismatched_scale_rejected(self):
        f = ReferenceFrame(402, 327, (219, 314), 1.0797)
        with self.assertRaises(ValueError):
            f.validate_plane_size(410.241, 333.703)

    def test_invalid_calibration(self):
        for s in (0, -1, float('nan'), float('inf'), True):
            with self.assertRaises(ValueError):
                ReferenceFrame(402, 327, (219, 314), s)
        with self.assertRaises(ValueError):
            ReferenceFrame(402, 327, (999, 314), 1)


if __name__ == '__main__':
    unittest.main()
