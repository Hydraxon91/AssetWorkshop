"""Runner bookkeeping/argv tests without Blender; real fixture trial is separate."""
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import review_runner as runner, review_session as review
from pipeline.common import PipelineError, REPO_ROOT


class RunnerTests(unittest.TestCase):
    def setUp(self):
        scratch = REPO_ROOT / '.dev-shots'
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='review-runner-test-', dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = self.root / 'session.json'
        self.executable = self.root / 'fake-blender.exe'
        self.executable.write_bytes(b'test-only')
        self.plan = self.root / 'plan.json'
        review.write_new(self.plan, runner.panel_plan(self.manifest, self.executable))
        runner.prepare(self.manifest, self.plan)

    def test_initial_status_and_plan(self):
        state = runner.status(self.manifest)
        self.assertEqual(state['next'], ['before_build'])
        self.assertEqual(state['used'], 0)
        self.assertEqual(state['budget_unit'], 'runner_operations')
        self.assertEqual(state['deadline'], 12)
        self.assertEqual(len(review.load(self.manifest)['runner']['stages']), 9)

    def test_plan_requires_scripted_execution_mode(self):
        missing = review.load(self.plan)
        missing.pop('execution_mode')
        missing_path = self.root / 'missing-mode.json'
        review.write_new(missing_path, missing)
        with self.assertRaisesRegex(PipelineError, 'invalid plan fields'):
            runner.prepare(self.root / 'missing-mode-session.json', missing_path)

        invalid = review.load(self.plan)
        invalid['execution_mode'] = 'mcp-edit'
        invalid_path = self.root / 'invalid-mode.json'
        review.write_new(invalid_path, invalid)
        with self.assertRaisesRegex(PipelineError, 'scripted-disposable plans only'):
            runner.prepare(self.root / 'invalid-mode-session.json', invalid_path)

    def test_no_caller_step_override(self):
        with self.assertRaises(PipelineError):
            review.status(self.manifest, 1)

    def test_budget_revision_preserves_history(self):
        review.start_operation(self.manifest, 'example')
        review.finish_operation(self.manifest, 'example', True)
        review.begin_budget(self.manifest, 'resume_01', 2, 5, 'explicit parent continuation')
        state = review.status(self.manifest)
        self.assertEqual((state['used'], state['deadline'], state['continuation']), (0,5,'resume_01'))
        document = review.load(self.manifest)
        self.assertEqual(len(document['budgets']), 2)
        self.assertEqual(document['events'][0]['step'], 1)

    def test_duplicate_revision_rejected(self):
        with self.assertRaises(PipelineError):
            review.begin_budget(self.manifest, 'initial', 2, 5, 'duplicate')

    def test_current_budget_not_legacy_mirror_is_authoritative(self):
        document = review.load(self.manifest)
        document['deadline'] = 999
        document['construction_stop'] = 998
        review._update(self.manifest, document)
        state = review.status(self.manifest)
        self.assertEqual((state['construction_stop'], state['deadline']), (5,12))

    def test_reserve_enforced_for_construction_only(self):
        review.begin_budget(self.manifest, 'small', 1, 3, 'test reserve')
        review.start_operation(self.manifest, 'construct', True)
        review.finish_operation(self.manifest, 'construct', True)
        self.assertEqual(review.status(self.manifest)['phase'], 'evidence-only')
        with self.assertRaises(PipelineError):
            review.start_operation(self.manifest, 'extra_construct', True)
        review.start_operation(self.manifest, 'check')
        review.finish_operation(self.manifest, 'check', True)
        review.start_operation(self.manifest, 'capture')
        review.finish_operation(self.manifest, 'capture', True)
        self.assertEqual(review.status(self.manifest)['phase'], 'stopped')
        with self.assertRaises(PipelineError):
            review.start_operation(self.manifest, 'late')

    def test_running_and_failed_block_retry(self):
        review.start_operation(self.manifest, 'work')
        with self.assertRaises(PipelineError):
            review.start_operation(self.manifest, 'work')
        with self.assertRaises(PipelineError):
            review.begin_budget(self.manifest, 'resume', 2, 5, 'cannot abandon live execution')
        review.finish_operation(self.manifest, 'work', False, error='test failure')
        with self.assertRaises(PipelineError):
            review.start_operation(self.manifest, 'retry')
        self.assertEqual(runner.status(self.manifest)['next'], [])

    def test_dependencies_and_existing_output_rejected_before_launch(self):
        with self.assertRaises(PipelineError):
            runner.run(self.manifest, 'after_build')
        (self.root / 'before_work.blend').write_bytes(b'partial')
        with self.assertRaisesRegex(PipelineError, 'output exists'):
            runner.run(self.manifest, 'before_build')
        self.assertEqual(review.status(self.manifest)['used'], 0)

    def test_changed_script_is_rejected(self):
        document = review.load(self.manifest)
        document['runner']['stages'][0]['script_artifact']['sha256'] = 'wrong'
        review._update(self.manifest, document)
        with self.assertRaisesRegex(PipelineError, 'changed'):
            runner.run(self.manifest, 'before_build')

    def test_no_shell_or_python_expression_in_command(self):
        stage = review.load(self.manifest)['runner']['stages'][1]
        argv = runner.command(str(self.executable), stage)
        self.assertIsInstance(argv, list)
        self.assertIn('--background', argv)
        self.assertNotIn('--python-expr', argv)
        self.assertEqual(argv[0], str(self.executable))
        self.assertIn(str(self.root / 'before_work.blend'), argv)

    def test_process_failure_is_durable_not_rerun(self):
        class Child:
            pid = 123
            returncode = 1
            def wait(self, timeout=None):
                return self.returncode
        with patch.object(runner.subprocess, 'Popen', return_value=Child()) as popen:
            with self.assertRaisesRegex(PipelineError, 'exited 1'):
                runner.run(self.manifest, 'before_build')
            self.assertNotIn('shell', popen.call_args.kwargs)
        operation = review.load(self.manifest)['events'][0]
        self.assertEqual(operation['state'], 'failed')
        self.assertEqual(operation['exit_code'], 1)
        self.assertEqual(review.status(self.manifest)['used'], 1)

    def test_record_step_cannot_lie_about_runner_count(self):
        artifact = self.root / 'example.blend'
        artifact.write_bytes(b'fixture')
        with self.assertRaises(PipelineError):
            review.record(self.manifest, 'checkpoint', 'before', artifact, 8)

    def test_timeout_terminates_only_owned_child_and_records_failure(self):
        class Child:
            pid = 123
            returncode = None
            waits = 0
            def wait(self, timeout=None):
                self.waits += 1
                if self.waits == 1:
                    raise subprocess.TimeoutExpired('fixture', timeout)
                self.returncode = -1
                return -1
            def poll(self):
                return self.returncode
        child = Child()
        with patch.object(runner.subprocess, 'Popen', return_value=child), patch.object(runner, 'terminate') as kill:
            with self.assertRaises(subprocess.TimeoutExpired):
                runner.run(self.manifest, 'before_build', 1)
            kill.assert_called_once_with(child)
        self.assertEqual(review.load(self.manifest)['events'][0]['state'], 'failed')

    def test_output_outside_task_directory_rejected(self):
        data = review.load(self.plan)
        data['stages'][0]['outputs'] = ['README.md']
        other = self.root / 'invalid-plan.json'
        review.write_new(other, data)
        with self.assertRaisesRegex(PipelineError, 'outputs must'):
            runner.prepare(self.root / 'other-session.json', other)

    def test_script_missing_or_plan_mutated_blocks_execution(self):
        self.plan.write_text('{}')
        with self.assertRaisesRegex(PipelineError, 'changed'):
            runner.run(self.manifest, 'before_build')

    def test_completed_stage_not_repeated(self):
        review.start_operation(self.manifest, 'before_build', True)
        review.finish_operation(self.manifest, 'before_build', True)
        with self.assertRaisesRegex(PipelineError, 'already complete'):
            runner.run(self.manifest, 'before_build')


if __name__ == '__main__':
    unittest.main()
