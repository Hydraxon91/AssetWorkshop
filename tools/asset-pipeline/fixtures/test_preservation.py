"""Portable contract tests: python -m unittest discover -s fixtures -p test_preservation.py."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.common import PipelineError
from pipeline.preservation import FIELDS, compare, digest, strict_json
from pipeline.inspection import image_record, scalar, settings


def sample():
    obj = {'counts': dict(vertices=8, edges=12, polygons=6, triangles=12),
           'fields': {f: dict(status='ok', hash=digest(f), issues=[]) for f in FIELDS}}
    return dict(version=1, context=dict(frame=1, view_layer='ViewLayer', source_path=''),
                objects={n: copy.deepcopy(obj) for n in ('Trunk', 'Canopy')},
                cost={'status': 'not_requested', 'errors': [], 'limits': []}, limits=[])


class PreservationTests(unittest.TestCase):
    def test_session_ids_are_not_authored_settings(self):
        properties = [SimpleNamespace(identifier=n, type='INT') for n in ('session_uid', 'segments')]
        first = SimpleNamespace(bl_rna=SimpleNamespace(properties=properties), session_uid=12, segments=3)
        second = SimpleNamespace(bl_rna=SimpleNamespace(properties=properties), session_uid=99, segments=3)
        self.assertEqual(settings(first), settings(second))
        second.segments = 4
        self.assertNotEqual(settings(first), settings(second))

    def test_image_animation_capability_and_enum_flags(self):
        image = SimpleNamespace(source='GENERATED', packed_files=[],
                                packed_file=SimpleNamespace(data=b'fixture'), is_dirty=False,
                                name='Packed', size=(2, 2), channels=4,
                                colorspace_settings=SimpleNamespace(name='sRGB'), alpha_mode='STRAIGHT')
        record, issues = image_record(image, set())
        self.assertEqual(issues, [])
        self.assertEqual(record['content'][0]['bytes'], 7)
        image.animation_data = object()
        self.assertIn('animated/driven image', image_record(image, set())[1])
        self.assertEqual(scalar({'Z', 'A'}), ['A', 'Z'])

    def setUp(self):
        self.a = sample()
        self.b = copy.deepcopy(self.a)
        self.policy = dict(version=1, objects={})

    def change(self, field, part='Canopy'):
        self.b['objects'][part]['fields'][field]['hash'] = digest('changed ' + field)

    def passed(self):
        return compare(self.a, self.b, self.policy)['status'] == 'pass'

    def test_default_and_each_exact_field(self):
        self.assertTrue(self.passed())
        for field in FIELDS:
            with self.subTest(field=field):
                self.b = copy.deepcopy(self.a)
                self.change(field)
                self.assertFalse(self.passed())

    def test_material_and_uv_tasks(self):
        for allowed in ('materials', 'uv'):
            self.b = copy.deepcopy(self.a)
            self.policy['objects']['Canopy'] = dict(preserve=[f for f in FIELDS if f != allowed], require_changes=[allowed])
            self.assertFalse(self.passed())
            self.change(allowed)
            self.assertTrue(self.passed())
            self.change('transforms', 'Trunk')
            self.assertFalse(self.passed())

    def test_canopy_ratio_not_whole_tree(self):
        self.policy['objects']['Canopy'] = dict(preserve=['materials', 'images', 'transforms'], triangle_ratio=dict(ratio=.5, tolerance=0))
        self.b['objects']['Canopy']['counts']['triangles'] = 6
        self.change('geometry')
        self.change('uv')
        self.assertTrue(self.passed())
        self.b['objects']['Canopy']['counts']['triangles'] = 0
        self.assertFalse(self.passed())

    def test_mapping_and_object_sets(self):
        self.b['objects']['Renamed'] = self.b['objects'].pop('Canopy')
        self.assertFalse(self.passed())
        self.policy['mapping'] = {'Canopy': 'Renamed'}
        self.assertTrue(self.passed())
        self.policy['objects']['Unknown'] = dict(preserve=['geometry'])
        with self.assertRaises(PipelineError):
            self.passed()

    def test_add_missing_explicit(self):
        del self.b['objects']['Canopy']
        self.assertFalse(self.passed())
        self.policy['allow_missing'] = ['Canopy']
        self.assertTrue(self.passed())
        self.b['objects']['New'] = copy.deepcopy(self.a['objects']['Canopy'])
        self.assertFalse(self.passed())
        self.policy['allow_new'] = ['New']
        self.assertTrue(self.passed())

    def test_invalid_fail_closed(self):
        mutations = [lambda a: a['objects'].clear(),
                     lambda a: a['objects']['Canopy']['fields']['uv'].update(hash=None),
                     lambda a: a['objects']['Canopy']['fields'].clear(),
                     lambda a: a['objects']['Canopy']['counts'].update(triangles=True),
                     lambda a: a['context'].update(frame=float('nan')),
                     lambda a: a.update(unknown=1)]
        for mutation in mutations:
            a = copy.deepcopy(self.a)
            mutation(a)
            with self.assertRaises(PipelineError):
                compare(a, self.b, self.policy)
        for rule in ({'preserve': []}, {'preserve': ['unknown']}, {'preserve': ['geometry'], 'mode': 'guess'},
                     {'preserve': ['geometry'], 'triangle_ratio': {'ratio': True, 'tolerance': 0}}):
            with self.assertRaises(PipelineError):
                compare(self.a, self.b, dict(version=1, objects={'Canopy': rule}))

    def test_unsupported_not_pass(self):
        for snapshot in (self.a, self.b):
            snapshot['objects']['Trunk']['fields']['materials'].update(status='unsupported', issues=['unresolved'])
        self.assertFalse(self.passed())

    def test_cost_errors_fail_and_missing_cost_rejected(self):
        self.b['cost']['status'] = 'error'
        self.b['cost']['errors'] = ['evaluation failed']
        with self.assertRaises(PipelineError):
            self.passed()

    def test_strict_json(self):
        for text in ('{"x":1,"x":2}', '{"x": NaN}'):
            with self.assertRaises(PipelineError):
                strict_json(text)

    def test_cli_no_bpy_and_collision(self):
        cli = Path(__file__).resolve().parents[1] / 'scripts/inspect_preservation.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [root / n for n in ('before.json', 'after.json', 'policy.json')]
            for p, value in zip(paths, (self.a, self.b, self.policy)):
                p.write_text(json.dumps(value))
            args = [sys.executable, '-B', str(cli), 'compare', '--before', str(paths[0]), '--after', str(paths[1]), '--policy', str(paths[2]), '--out']
            out = root / 'report.json'
            self.assertEqual(subprocess.run(args + [str(out)], capture_output=True).returncode, 0)
            original = out.read_bytes()
            self.assertEqual(subprocess.run(args + [str(out)], capture_output=True).returncode, 2)
            self.assertEqual(original, out.read_bytes())
            self.assertEqual(subprocess.run(args + [str(paths[0])], capture_output=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
