"""Pure tests; synthetic files are not Blender evidence."""
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import review_session as r
from pipeline.common import PipelineError


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = self.root / 'session.json'
        r.create(self.manifest, 'synthetic review', 12, 20, ['junction'])

    def file(self, name, content='fixture'):
        path = self.root / name
        path.write_text(content, encoding='utf-8')
        return path

    def populate(self, role):
        blend = self.file(role + '.blend', role)
        check = self.file(role + '-check.json', '{"status":"pass"}')
        image = self.file(role + '.svg', '<svg xmlns="http://www.w3.org/2000/svg"/>')
        r.record(self.manifest, 'checkpoint', role, blend, 1)
        r.record(self.manifest, 'check', role, check, 2, 'pass')
        meta = dict(checkpoint_sha256=r.digest(blend), view='junction',
                    camera=dict(matrix_world=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], type='ORTHO', lens=50,
                                ortho_scale=2), resolution=[900, 700],
                    shading={'engine': 'fixture'}, visibility=['Body'])
        path = self.file(role + '-meta.json', json.dumps(meta))
        r.record(self.manifest, 'capture', role, image, 3, view='junction', metadata=path)
        return blend, path, image

    def test_resume_and_reserve(self):
        self.assertEqual(r.status(self.manifest, 1)['phase'], 'construction')
        self.populate('before')
        resumed = r.status(self.manifest, 12)
        self.assertEqual(resumed['phase'], 'evidence-only')
        self.assertEqual(resumed['pending'], ['after: checkpoint'])
        self.assertEqual(r.status(self.manifest, 20)['phase'], 'stopped')

    def test_complete_is_not_acceptance(self):
        self.populate('before')
        self.populate('after')
        state = r.status(self.manifest, 15)
        self.assertTrue(state['evidence_complete'])
        self.assertEqual(state['acceptance'], 'unjudged')
        output = self.root / 'sheet.html'
        r.sheet(self.manifest, output)
        self.assertIn('before', output.read_text(encoding='utf-8'))
        with self.assertRaises(FileExistsError):
            r.sheet(self.manifest, output)

    def test_changed_artifact_is_rejected(self):
        blend, _, _ = self.populate('before')
        blend.write_text('mutated')
        with self.assertRaises(PipelineError):
            r.status(self.manifest, 4)

    def test_missing_artifact_is_rejected(self):
        with self.assertRaises(PipelineError):
            r.record(self.manifest, 'checkpoint', 'before', self.root / 'missing', 1)

    def test_capture_requires_check(self):
        blend = self.file('source.blend')
        r.record(self.manifest, 'checkpoint', 'before', blend, 1)
        with self.assertRaises(PipelineError):
            r.record(self.manifest, 'capture', 'before', blend, 2)

    def test_replacement_checkpoint_invalidates_old_evidence(self):
        self.populate('before')
        replacement = self.file('replacement.blend', 'different')
        r.record(self.manifest, 'checkpoint', 'before', replacement, 5)
        self.assertIn('before: passing check', r.status(self.manifest, 6)['pending'])
        self.assertEqual(len(r.load(self.manifest)['events']), 4)

    def test_later_failed_check_blocks_sheet(self):
        self.populate('before')
        self.populate('after')
        r.record(self.manifest, 'check', 'after', self.file('failed.json'), 8, 'fail')
        with self.assertRaises(PipelineError):
            r.sheet(self.manifest, self.root / 'sheet.html')

    def test_mismatched_camera_refuses_sheet(self):
        self.populate('before')
        _, metadata, image = self.populate('after')
        data = r.load(metadata)
        data['camera']['lens'] = 85
        other = self.file('changed-meta.json', json.dumps(data))
        r.record(self.manifest, 'capture', 'after', image, 9,
                 view='junction', metadata=other)
        with self.assertRaisesRegex(PipelineError, 'camera'):
            r.sheet(self.manifest, self.root / 'sheet.html')

    def test_mismatched_checkpoint_refuses_capture(self):
        self.populate('before')
        _, metadata, image = self.populate('after')
        data = r.load(metadata)
        data['checkpoint_sha256'] = 'wrong'
        other = self.file('wrong.json', json.dumps(data))
        with self.assertRaises(PipelineError):
            r.record(self.manifest, 'capture', 'after', image, 9,
                     view='junction', metadata=other)

    def test_changed_capture_bytes_block_sheet(self):
        self.populate('before')
        _, _, image = self.populate('after')
        image.write_text('replaced')
        with self.assertRaises(PipelineError):
            r.sheet(self.manifest, self.root / 'sheet.html')

    def test_invalid_camera_matrix_is_rejected(self):
        _, metadata, image = self.populate('before')
        data = r.load(metadata)
        data['camera']['matrix_world'] = [1, 2, 3]
        other = self.file('bad-matrix.json', json.dumps(data))
        with self.assertRaisesRegex(PipelineError, '4x4'):
            r.record(self.manifest, 'capture', 'before', image, 4,
                     view='junction', metadata=other)

    def test_no_overwrite_and_invalid_reserve(self):
        with self.assertRaises(FileExistsError):
            r.create(self.manifest, 'x', 1, 2, ['front'])
        with self.assertRaises(PipelineError):
            r.create(self.root / 'invalid.json', 'x', 20, 12, ['front'])

    def test_cli_resume_sheet_and_failure_exit(self):
        self.populate('before')
        cli = Path(__file__).resolve().parents[1] / 'scripts' / 'review_session.py'
        def run(*args):
            return subprocess.run([sys.executable, str(cli), *args,
                                   '--manifest', str(self.manifest)], capture_output=True, text=True)
        resumed = run('status', '--step', '12')
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(json.loads(resumed.stdout)['pending'], ['after: checkpoint'])
        self.populate('after')
        output = self.root / 'cli-sheet.html'
        self.assertEqual(run('sheet', '--out', str(output)).returncode, 0)
        self.assertEqual(run('sheet', '--out', str(output)).returncode, 2)
        self.assertEqual(run('record', '--kind', 'check', '--role', 'after',
                             '--file', str(self.root / 'missing'), '--step', '18',
                             '--outcome', 'pass').returncode, 2)


if __name__ == '__main__':
    unittest.main()
