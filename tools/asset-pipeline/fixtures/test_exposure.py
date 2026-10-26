"""Portable contract tests: python -m unittest discover -s fixtures -p test_exposure.py."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.common import PipelineError
from pipeline.exposure import RULE_FIELDS, summarise, validate_policy, validate_report


def policy(**overrides):
    rule = {"object": "Speaker_Face", "approach": [0, 1, 0]}
    rule.update(overrides)
    return {"version": 1, "targets": [rule]}


def report(targets, status=None):
    statuses = {target["status"] for target in targets}
    return {
        "version": 1,
        "context": {"frame": 1, "view_layer": "ViewLayer", "source_path": ""},
        "targets": targets,
        "status": status or ("error" if "error" in statuses else ("fail" if "fail" in statuses else "pass")),
        "limits": ["fixture"],
    }


def target(**overrides):
    record = {
        "object": "Speaker_Face", "status": "pass", "samples_total": 2,
        "visible": 2, "blocked": 0, "miss": 0, "error": 0,
        "required_fraction": 1.0, "visible_fraction": 1.0,
        "blockers": {}, "unexpected_blockers": [],
        "samples": [{"status": "visible"}, {"status": "visible"}],
    }
    record.update(overrides)
    return record


class PolicyTests(unittest.TestCase):
    def test_defaults_applied(self):
        rule = validate_policy(policy())[0]
        self.assertEqual(rule["occluders"], "any")
        self.assertEqual(rule["samples"], 16)
        self.assertEqual(rule["required_fraction"], 1.0)
        self.assertIs(rule["ignore_self"], True)
        self.assertIs(rule["require_front_facing"], False)
        self.assertEqual(rule["sample_facing"], "target")
        self.assertIsNone(rule["backoff"])
        self.assertEqual(rule["approach"], [0.0, 1.0, 0.0])

    def test_approach_is_normalised(self):
        rule = validate_policy(policy(approach=[0, 4, 0]))[0]
        self.assertAlmostEqual(sum(value * value for value in rule["approach"]), 1.0, places=12)

    def test_every_rule_field_round_trips(self):
        rule = {"object": "Speaker_Face", "approach": [0, 1, 0], "occluders": ["Body_Enclosure"],
                "samples": 4, "required_fraction": 0.5, "ignore_self": False,
                "require_front_facing": True, "sample_facing": "all", "backoff": 2.0}
        self.assertEqual(set(rule), set(RULE_FIELDS), "RULE_FIELDS and the parsed contract disagree")
        parsed = validate_policy({"version": 1, "targets": [rule]})[0]
        self.assertEqual(parsed["occluders"], ["Body_Enclosure"])
        self.assertEqual(parsed["samples"], 4)
        self.assertEqual(parsed["required_fraction"], 0.5)
        self.assertIs(parsed["ignore_self"], False)
        self.assertIs(parsed["require_front_facing"], True)
        self.assertEqual(parsed["sample_facing"], "all")
        self.assertEqual(parsed["backoff"], 2.0)

    def test_rejects_malformed_policies(self):
        cases = {
            "not an object": [],
            "extra top key": {"version": 1, "targets": [], "extra": 1},
            "bad version": {"version": 2, "targets": [{"object": "A", "approach": [0, 1, 0]}]},
            "bool version": {"version": True, "targets": [{"object": "A", "approach": [0, 1, 0]}]},
            "empty targets": {"version": 1, "targets": []},
            "target not object": {"version": 1, "targets": ["A"]},
            "missing approach": {"version": 1, "targets": [{"object": "A"}]},
            "missing object": {"version": 1, "targets": [{"approach": [0, 1, 0]}]},
            "unknown field": {"version": 1, "targets": [{"object": "A", "approach": [0, 1, 0], "nope": 1}]},
            "blank object": {"version": 1, "targets": [{"object": " ", "approach": [0, 1, 0]}]},
            "two-element approach": {"version": 1, "targets": [{"object": "A", "approach": [0, 1]}]},
            "string approach": {"version": 1, "targets": [{"object": "A", "approach": "up"}]},
            "zero approach": {"version": 1, "targets": [{"object": "A", "approach": [0, 0, 0]}]},
            "nonfinite approach": {"version": 1, "targets": [{"object": "A", "approach": [0, float("inf"), 0]}]},
            "bool approach": {"version": 1, "targets": [{"object": "A", "approach": [0, True, 0]}]},
            "duplicate target": {"version": 1, "targets": [{"object": "A", "approach": [0, 1, 0]},
                                                           {"object": "A", "approach": [0, 1, 0]}]},
            "zero samples": policy(samples=0),
            "float samples": policy(samples=1.5),
            "huge samples": policy(samples=4097),
            "fraction above one": policy(required_fraction=1.5),
            "fraction below zero": policy(required_fraction=-0.1),
            "bool fraction": policy(required_fraction=True),
            "string ignore_self": policy(ignore_self="yes"),
            "string front facing": policy(require_front_facing="yes"),
            "bad sample facing": policy(sample_facing="front"),
            "zero backoff": policy(backoff=0),
            "negative backoff": policy(backoff=-1),
            "occluder string": policy(occluders="Body"),
            "occluder duplicates": policy(occluders=["Body", "Body"]),
            "occluder blank": policy(occluders=[""]),
            "occluder is target": policy(occluders=["Speaker_Face"]),
        }
        for label, data in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(PipelineError):
                    validate_policy(data)

    def test_policy_is_not_mutated(self):
        data = policy(occluders=["Body"], samples=4, approach=[0, 2, 0])
        before = copy.deepcopy(data)
        validate_policy(data)
        self.assertEqual(data, before)


class SummaryTests(unittest.TestCase):
    def test_all_visible_passes(self):
        result = summarise([{"status": "visible"}, {"status": "visible"}], 1.0)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["visible_fraction"], 1.0)

    def test_blocked_reports_blocker_counts(self):
        samples = [{"status": "blocked", "blocker": "Body_Enclosure"}] * 3 + [{"status": "visible"}]
        result = summarise(samples, 0.5)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["blockers"], {"Body_Enclosure": 3})
        self.assertEqual(result["visible_fraction"], 0.25)

    def test_partial_fraction_boundary(self):
        samples = [{"status": "visible"}, {"status": "blocked", "blocker": "Wall"}]
        self.assertEqual(summarise(samples, 0.5)["status"], "pass")
        self.assertEqual(summarise(samples, 0.51)["status"], "fail")

    def test_zero_samples_is_error(self):
        result = summarise([], 1.0)
        self.assertEqual(result["status"], "error")
        self.assertIsNone(result["visible_fraction"])

    def test_miss_or_error_never_passes(self):
        visible_only = [{"status": "visible"}, {"status": "visible"}]
        for bad in ("miss", "error"):
            with self.subTest(status=bad):
                result = summarise(visible_only + [{"status": bad}], 0.1)
                self.assertEqual(result["status"], "error")
                self.assertIsNone(result["visible_fraction"])

    def test_unexpected_blockers_are_surfaced(self):
        samples = [{"status": "blocked", "blocker": "Roof_Panel", "unexpected_blocker": True}]
        result = summarise(samples, 1.0)
        self.assertEqual(result["unexpected_blockers"], ["Roof_Panel"])

    def test_rejects_unknown_status_and_nameless_blocker(self):
        for samples in ([{"status": "hidden"}], [{"status": "blocked"}]):
            with self.subTest(samples=samples):
                with self.assertRaises(PipelineError):
                    summarise(samples, 1.0)


class ReportTests(unittest.TestCase):
    def test_accepts_pass_and_fail(self):
        validate_report(report([target()]))
        validate_report(report([target(status="fail", visible=0, blocked=2, visible_fraction=0.0,
                                       blockers={"Wall": 2},
                                       samples=[{"status": "blocked", "blocker": "Wall"}] * 2)]))

    def test_status_must_match_targets(self):
        with self.assertRaises(PipelineError):
            validate_report(report([target()], status="fail"))

    def test_error_target_dominates(self):
        good = target()
        bad = target(object="Screen", status="error", samples_total=1, visible=0, error=1,
                     visible_fraction=None, samples=[{"status": "error"}])
        data = report([good, bad])
        self.assertEqual(data["status"], "error")
        validate_report(data)

    def test_rejects_inconsistent_counts(self):
        cases = {
            "counts do not sum": target(visible=1),
            "sample list length": target(samples=[{"status": "visible"}]),
            "bad status": target(status="unknown"),
            "negative count": target(visible=-1),
            "missing field": {key: value for key, value in target().items() if key != "blockers"},
        }
        for label, record in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(PipelineError):
                    validate_report(report([record]))

    def test_rejects_malformed_envelope(self):
        base = report([target()])
        cases = {
            "extra key": {**base, "extra": 1},
            "bad version": {**base, "version": 2},
            "empty targets": {**base, "targets": []},
            "bad context": {**base, "context": {"frame": "1", "view_layer": "V", "source_path": ""}},
            "bad limits": {**base, "limits": [1]},
        }
        for label, data in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(PipelineError):
                    validate_report(data)


if __name__ == "__main__":
    unittest.main()
