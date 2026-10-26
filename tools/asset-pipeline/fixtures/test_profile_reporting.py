"""Exercise pure builder reporting and restoration without importing bpy."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

SOURCE = Path(__file__).with_name('build_wateringcan_profile.py')
tree = ast.parse(SOURCE.read_text())
functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and
             n.name in ('bounds_equal', 'editability_stage')]
scope = {}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), 'exec'), scope)


class ReportingTests(unittest.TestCase):
    def test_vector_bounds_equal(self):
        a = {'bbox_min_mm': [0., 1., 2.], 'bbox_max_mm': [3., 4., 5.]}
        self.assertTrue(scope['bounds_equal'](a, a))
        b = dict(a, bbox_max_mm=[3., 4., 6.])
        self.assertFalse(scope['bounds_equal'](a, b))
        self.assertFalse(scope['bounds_equal'](a, dict(a, bbox_max_mm=[3., 4.])))

    def test_control_restored_on_evaluation_error(self):
        vertex = SimpleNamespace(co=(.113, 0., .125))
        mesh = SimpleNamespace(vertices=[vertex]*6, update=lambda: None)
        body = SimpleNamespace(name='CF_Body_B', type='MESH', data=mesh)
        objects = {'CF_Body_B': body, 'CF_Profile_B': object(),
                   'CF_Ref_Plane': object(), 'Body_v2': object()}

        class Objects(dict):
            def __iter__(self):
                return iter([body])

        calls = []
        def stats(obj):
            calls.append(obj)
            if len(calls) > 1:
                raise RuntimeError('injected evaluation failure')
            return {}
        env = dict(scope, bpy=SimpleNamespace(
            data=SimpleNamespace(objects=Objects(objects)),
            context=SimpleNamespace(scene=object(),
                view_layer=SimpleNamespace(update=lambda: None))),
            eval_stats=stats, OUT=Path('unused-synthetic-output'))
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), 'exec'), env)
        with self.assertRaisesRegex(RuntimeError, 'injected evaluation failure'):
            env['editability_stage']('B')
        self.assertEqual(vertex.co, (.113, 0., .125))


if __name__ == '__main__':
    unittest.main()
