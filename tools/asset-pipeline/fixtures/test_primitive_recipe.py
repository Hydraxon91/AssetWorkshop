"""Pure recipe contract tests: no Blender imports, processes or file outputs."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.primitive_recipe import validate, digest, part_names, material_content, stage_plan
from pipeline.common import PipelineError

FIXTURE = Path(__file__).resolve().parents[1] / 'examples/primitive-recipe.fixture.json'


class Recipes(unittest.TestCase):
    def setUp(self):
        self.recipe = json.loads(FIXTURE.read_text())

    def test_canonical_repeatable_and_not_mutated(self):
        original = copy.deepcopy(self.recipe)
        a = validate(self.recipe)
        self.assertEqual(a, validate(a))
        self.assertEqual(digest(a), digest(validate(self.recipe)))
        self.assertEqual(original, self.recipe)
        self.assertEqual(part_names(a, True), ['Bake__Slab', 'Bake__Block'])

    def test_dimensions_reject_bad_values(self):
        for bad in [True, 0, -1, float('nan'), float('inf'), '0.1', None]:
            with self.subTest(bad=bad), self.assertRaises(PipelineError):
                r = copy.deepcopy(self.recipe)
                r['parts'][0]['dimensions'][1] = bad
                validate(r)

    def test_unknown_fields_each_level(self):
        for which in ['root', 'part', 'bevel', 'material']:
            r = copy.deepcopy(self.recipe)
            obj = {'root': r, 'part': r['parts'][0], 'bevel': r['parts'][0]['bevel'],
                   'material': r['material']}[which]
            obj['python'] = 'not allowed'
            with self.subTest(which=which), self.assertRaises(PipelineError):
                validate(r)

    def test_names_and_version(self):
        for key, value in [('root', 'Bake__Reserved'), ('root', '../file'), ('version', True), ('version', 2)]:
            r = copy.deepcopy(self.recipe)
            r[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(PipelineError):
                validate(r)
        for value in [self.recipe['root'], 'Slab', 'Bake__Block']:
            r = copy.deepcopy(self.recipe)
            r['parts'][1]['name'] = value
            with self.subTest(value=value), self.assertRaises(PipelineError):
                validate(r)

    def test_bounds_and_types(self):
        edits = [('segments', True), ('segments', 0), ('segments', 5), ('width', .1)]
        for key, value in edits:
            r = copy.deepcopy(self.recipe)
            r['parts'][0]['bevel'][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(PipelineError):
                validate(r)
        for parts in [[], self.recipe['parts'] * 9, 'box']:
            r = copy.deepcopy(self.recipe)
            r['parts'] = parts
            with self.assertRaises(PipelineError):
                validate(r)

    def test_variant_is_data(self):
        a = validate(self.recipe)
        self.recipe['parts'][0]['dimensions'][0] = .2
        b = validate(self.recipe)
        self.assertNotEqual(digest(a), digest(b))
        self.assertEqual(part_names(a), part_names(b))

    def test_material_id_bookkeeping_not_content(self):
        a = {'name': 'Fixture', 'settings': {'users': 2, 'use_fake_user': False,
                                          'roughness': .4}, 'graph': {'nodes': [1]}}
        b = copy.deepcopy(a)
        b['settings'].update(users=4, use_fake_user=True)
        self.assertEqual(material_content(a), material_content(b))
        self.assertEqual(a['settings']['users'], 2)
        b['settings']['roughness'] = .5
        self.assertNotEqual(material_content(a), material_content(b))
        b = copy.deepcopy(a)
        b['graph']['nodes'] = [2]
        self.assertNotEqual(material_content(a), material_content(b))

    def test_existing_runner_presets_are_data_only(self):
        root = FIXTURE.parents[3]
        directory = root / '.dev-shots/primitive-pure-test-unused'
        plan, jobs = stage_plan(FIXTURE, directory, 'unused.exe')
        self.assertEqual(len(plan['stages']), 8)
        self.assertEqual(plan['stages'][0]['args'][0], 'build')
        self.assertEqual(jobs, {})
        plan, jobs = stage_plan(FIXTURE, directory, 'unused.exe', 'appearance',
                                root / '.dev-shots/unused/prepared.blend')
        self.assertEqual(len(plan['stages']), 8)
        self.assertTrue(jobs['bake-job.json']['preserve_layout'])
        self.assertFalse(jobs['bake-job.json']['export'])


if __name__ == '__main__':
    unittest.main()
