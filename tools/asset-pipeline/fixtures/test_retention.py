"""Portable contract tests: python -m unittest discover -s fixtures -p test_retention.py."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.common import PipelineError
from pipeline.retention import (CRITERIA, compare, validate_policy, validate_report,
                                validate_snapshot)


def evaluated(vertices=1000, triangles=2000, spans=(2.0, 1.0, 0.5), bbox="default", components=1):
    if bbox == "default":
        bbox = [[0.0, 0.0, 0.0], [spans[0], spans[1], spans[2]]]
    return {"vertices": vertices, "triangles": triangles, "spans": list(spans),
            "bbox": bbox, "components": components}


def record(ev=None, authored=None):
    return {
        "authored": authored or {"vertices": 100, "polygons": 120, "modifiers": ["Bevel"]},
        "evaluated": ev or evaluated(),
    }


def snap(objects=None, frame=1):
    return {
        "version": 1,
        "context": {"frame": frame, "view_layer": "ViewLayer", "source_path": ""},
        "objects": objects if objects is not None else {"Body": record()},
        "limits": ["fixture"],
    }


def policy(rule=None):
    return {"version": 1, "objects": {"Body": rule if rule is not None
                                      else {"min_vertex_ratio": 0.85}}}


class PolicyTests(unittest.TestCase):
    def test_accepts_each_criterion(self):
        for criterion in CRITERIA:
            with self.subTest(criterion=criterion):
                validate_policy(policy({criterion: 0.5}))

    def test_rejects_malformed_policies(self):
        cases = {
            "not an object": [],
            "missing objects": {"version": 1},
            "extra top key": {"version": 1, "objects": {"Body": {"min_vertex_ratio": 0.5}}, "nope": 1},
            "bad version": {"version": 2, "objects": {"Body": {"min_vertex_ratio": 0.5}}},
            "empty objects": {"version": 1, "objects": {}},
            "rule not object": {"version": 1, "objects": {"Body": 0.5}},
            "empty rule": {"version": 1, "objects": {"Body": {}}},
            "unknown criterion": {"version": 1, "objects": {"Body": {"min_volume": 0.5}}},
            "above one": {"version": 1, "objects": {"Body": {"min_vertex_ratio": 1.5}}},
            "below zero": {"version": 1, "objects": {"Body": {"min_vertex_ratio": -0.1}}},
            "bool threshold": {"version": 1, "objects": {"Body": {"min_vertex_ratio": True}}},
            "string threshold": {"version": 1, "objects": {"Body": {"min_vertex_ratio": "0.9"}}},
            "infinite threshold": {"version": 1, "objects": {"Body": {"min_vertex_ratio": float("inf")}}},
            "allow_missing is not a supported field": {"version": 1, "objects": {"Body": {"min_vertex_ratio": 0.5}},
                                                       "allow_missing": ["Body"]},
        }
        for label, data in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(PipelineError):
                    validate_policy(data)

    def test_policy_has_no_default_threshold(self):
        with self.assertRaises(PipelineError):
            validate_policy({"version": 1, "objects": {"Body": {}}})

    def test_policy_is_not_mutated(self):
        data = policy({"min_vertex_ratio": 0.5})
        before = copy.deepcopy(data)
        validate_policy(data)
        self.assertEqual(data, before)


class SnapshotTests(unittest.TestCase):
    def test_accepts_recorded_snapshot(self):
        validate_snapshot(snap())

    def test_accepts_empty_body_without_bbox(self):
        validate_snapshot(snap({"Body": record(evaluated(vertices=0, triangles=0,
                                                        spans=(0, 0, 0), bbox=None,
                                                        components=0))}))

    def test_rejects_malformed_snapshots(self):
        base = snap()
        cases = {
            "extra key": {**base, "extra": 1},
            "bad version": {**base, "version": 2},
            "bad context": {**base, "context": {"frame": "1", "view_layer": "V", "source_path": ""}},
            "empty objects": {**base, "objects": {}},
            "object missing evaluated": {**base, "objects": {"Body": {"authored": record()["authored"]}}},
            "negative vertices": {**base, "objects": {"Body": record(evaluated(vertices=-1))}},
            "two spans": {**base, "objects": {"Body": record({**evaluated(), "spans": [1.0, 2.0]})}},
            "negative span": {**base, "objects": {"Body": record(evaluated(spans=(-1.0, 1.0, 1.0)))}},
            "empty body with bbox": {**base, "objects": {"Body": record(evaluated(vertices=0, triangles=0))}},
            "bad modifiers": {**base, "objects": {"Body": record(
                authored={"vertices": 1, "polygons": 1, "modifiers": [1]})}},
        }
        for label, data in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(PipelineError):
                    validate_snapshot(data)


class CompareTests(unittest.TestCase):
    def test_unchanged_body_passes(self):
        report = compare(snap(), snap(), policy({"min_vertex_ratio": 1.0,
                                                 "min_span_ratio": 1.0,
                                                 "min_bbox_coverage": 1.0}))
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["objects"][0]["unchecked"], ["min_triangle_ratio"])

    def test_collapsed_body_fails_with_measured_values(self):
        collapsed = evaluated(vertices=182, triangles=300, spans=(0.527, 0.6, 0.227),
                              bbox=[[0.0, 0.0, 0.0], [0.527, 0.6, 0.227]], components=8)
        report = compare(snap(), snap({"Body": record(collapsed)}),
                         policy({"min_vertex_ratio": 0.85, "min_span_ratio": 0.99,
                                 "min_bbox_coverage": 0.995}))
        self.assertEqual(report["status"], "fail")
        measured = {item["criterion"]: item["actual"] for item in report["objects"][0]["criteria"]}
        self.assertAlmostEqual(measured["min_vertex_ratio"], 0.182, places=6)
        self.assertAlmostEqual(measured["min_span_ratio"], 0.2635, places=4)
        self.assertLess(measured["min_bbox_coverage"], 0.15)

    def test_threshold_boundary_is_inclusive(self):
        half = evaluated(vertices=500, triangles=1000, spans=(1.0, 0.5, 0.25))
        self.assertEqual(compare(snap(), snap({"Body": record(half)}),
                                 policy({"min_vertex_ratio": 0.5}))["status"], "pass")
        self.assertEqual(compare(snap(), snap({"Body": record(half)}),
                                 policy({"min_vertex_ratio": 0.51}))["status"], "fail")

    def test_unstated_criteria_are_reported_unchecked(self):
        report = compare(snap(), snap(), policy({"min_vertex_ratio": 0.5}))
        self.assertEqual(sorted(report["objects"][0]["unchecked"]),
                         sorted(set(CRITERIA) - {"min_vertex_ratio"}))

    def test_missing_object_fails(self):
        report = compare(snap(), snap({"Other": record()}), policy())
        self.assertEqual(report["status"], "fail")
        self.assertIn("missing", report["objects"][0]["error_reason"])

    def test_empty_baseline_is_error_not_pass(self):
        empty = record(evaluated(vertices=0, triangles=0, spans=(0, 0, 0), bbox=None, components=0))
        report = compare(snap({"Body": empty}), snap(), policy())
        self.assertEqual(report["status"], "error")
        self.assertIn("undefined", report["objects"][0]["error_reason"])

    def test_zero_after_is_zero_fraction_not_crash(self):
        gone = record(evaluated(vertices=0, triangles=0, spans=(0, 0, 0), bbox=None, components=0))
        report = compare(snap(), snap({"Body": gone}), policy({"min_vertex_ratio": 0.1}))
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["objects"][0]["criteria"][0]["actual"], 0.0)

    def test_zero_baseline_triangles_is_inconclusive(self):
        flat = record(evaluated(vertices=10, triangles=0))
        report = compare(snap({"Body": flat}), snap(), policy({"min_triangle_ratio": 0.9}))
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["objects"][0]["criteria"][0]["status"], "error")

    def test_growth_passes_and_exceeds_one(self):
        grown = evaluated(vertices=2000, triangles=4000, spans=(4.0, 2.0, 1.0),
                          bbox=[[0.0, 0.0, 0.0], [4.0, 2.0, 1.0]])
        report = compare(snap(), snap({"Body": record(grown)}),
                         policy({"min_vertex_ratio": 0.5, "min_bbox_coverage": 0.5}))
        measured = {item["criterion"]: item["actual"] for item in report["objects"][0]["criteria"]}
        self.assertEqual(measured["min_vertex_ratio"], 2.0)
        self.assertEqual(measured["min_bbox_coverage"], 1.0)

    def test_authored_change_is_reported(self):
        authored = {"vertices": 101, "polygons": 120, "modifiers": ["Bevel"]}
        report = compare(snap(), snap({"Body": record(authored=authored)}), policy())
        self.assertTrue(report["objects"][0]["authored_changed"])

    def test_offscreen_body_is_a_retention_failure(self):
        moved = evaluated(spans=(2.0, 1.0, 0.5), bbox=[[100.0, 100.0, 100.0],
                                                       [102.0, 101.0, 100.5]])
        report = compare(snap(), snap({"Body": record(moved)}),
                         policy({"min_bbox_coverage": 0.99}))
        self.assertEqual(report["objects"][0]["criteria"][0]["actual"], 0.0)
        self.assertEqual(report["status"], "fail")


class ReportTests(unittest.TestCase):
    def test_accepts_produced_reports(self):
        for rule in ({"min_vertex_ratio": 1.0}, {"min_bbox_coverage": 0.99}):
            validate_report(compare(snap(), snap(), policy(rule)))

    def test_rejects_malformed_reports(self):
        base = compare(snap(), snap(), policy())
        cases = {
            "extra key": {**base, "extra": 1},
            "bad status": {**base, "status": "unknown"},
            "status disagrees": {**base, "status": "fail"},
            "empty objects": {**base, "objects": []},
            "bad criterion": {**base, "objects": [{**base["objects"][0],
                                                   "criteria": [{"criterion": "min_nope"}]}]},
        }
        for label, data in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(PipelineError):
                    validate_report(data)


if __name__ == "__main__":
    unittest.main()
