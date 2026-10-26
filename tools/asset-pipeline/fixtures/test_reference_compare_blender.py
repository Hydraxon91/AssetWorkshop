"""Disposable camera-registration and overlay controls; never opens an asset."""
from pathlib import Path
import sys
import unittest
import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reference_compare import ReferenceFrame, contour_overlay


class RegistrationTests(unittest.TestCase):
    def test_landmarks_all_views_landscape_and_portrait(self):
        scene = bpy.context.scene
        for w, h in ((402, 327), (327, 402)):
            for projection in ('side', 'front', 'top'):
                f = ReferenceFrame(w, h, (w/2, h-10), 1.1, projection)
                data = bpy.data.cameras.new('SyntheticRegistrationCamera')
                camera = bpy.data.objects.new('SyntheticRegistrationCamera', data)
                scene.collection.objects.link(camera)
                spec, g = f.camera_spec_mm(), f.geometry()
                right = (Vector(g['corners_mm'][1])-Vector(g['corners_mm'][0])).normalized()
                up = (Vector(g['corners_mm'][0])-Vector(g['corners_mm'][3])).normalized()
                normal = Vector(g['normal'])
                camera.rotation_euler = Matrix((right, up, normal)).transposed().to_euler()
                camera.location = Vector(spec['position_mm']) / 1000
                kinds = {i.identifier for i in data.bl_rna.properties['type'].enum_items}
                self.assertIn('ORTHO', kinds)
                data.type = 'ORTHO'
                data.ortho_scale = spec['ortho_scale_mm']/1000
                scene.render.resolution_x, scene.render.resolution_y = w, h
                scene.render.resolution_percentage = 100
                scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
                bpy.context.view_layer.update()
                for u, v in ((0, 0), (w, h), f.origin_px, (w*.23, h*.71)):
                    p = Vector(f.pixel_to_world_mm(u, v))/1000
                    screen = world_to_camera_view(scene, camera, p)
                    self.assertAlmostEqual(screen.x*w, u, delta=.001)
                    self.assertAlmostEqual((1-screen.y)*h, v, delta=.001)
                bpy.data.objects.remove(camera, do_unlink=True)
                bpy.data.cameras.remove(data)

    def test_overlay_registration_and_rejection(self):
        ref = np.ones((10, 12, 4), np.float32)*.5
        alpha = np.zeros((10, 12), np.float32)
        alpha[2:8, 3:9] = 1
        out = contour_overlay(ref, alpha)
        np.testing.assert_allclose(out[2, 3, :3], [.02, .85, .2])
        np.testing.assert_allclose(out[0, 0, :3], [.5, .5, .5])
        self.assertTrue(np.all(out[:, :, 3] == 1))
        with self.assertRaises(ValueError):
            contour_overlay(ref, np.zeros((5, 6)))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RegistrationTests)
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
        raise RuntimeError('reference comparison fixtures failed')
