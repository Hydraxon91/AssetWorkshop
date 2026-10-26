"""Synthetic local-only historical path audit fixtures."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    'historical_jobs', Path(__file__).resolve().parents[1] / 'scripts/audit_historical_jobs.py')
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def test_external_not_probed(self):
        with patch.object(Path, 'is_file', side_effect=AssertionError('external probe')):
            self.assertEqual(audit.inspect_path('/local', '/elsewhere/source.blend')['status'],
                             'external-uninspected')

    def test_local_inputs_and_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source.blend').write_bytes(b'fixture')
            p = root / 'job.json'
            raw = json.dumps({'source': 'source.blend', 'out_dir': 'new-output',
                              'tile_materials': {'M': {'base': 'missing.png'}}})
            p.write_text(raw)
            result = audit.audit(root, p)
            self.assertEqual(result['disposition'], 'archival-blocked')
            self.assertEqual(p.read_text(), raw)
            self.assertFalse((root / 'new-output').exists())

    def test_local_does_not_claim_runnable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source.blend').touch()
            p = root / 'job.json'
            p.write_text(json.dumps({'source': 'source.blend'}))
            self.assertEqual(audit.audit(root, p)['disposition'],
                             'declared-paths-local-execution-unverified')

    def test_implicit_scene_is_archival(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / 'job.json'
            p.write_text(json.dumps({'objects': ['Shell_Root'], 'out_dir': 'output'}))
            self.assertEqual(audit.audit(root, p)['disposition'],
                             'archival-requires-explicit-scene')


if __name__ == '__main__':
    unittest.main()
