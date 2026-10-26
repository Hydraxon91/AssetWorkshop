"""Evaluated retention: did an edit remove the body while the sources stayed healthy?

This is not authored preservation (``pipeline.preservation`` compares authored fields and
states that no evaluated equivalence is established) and not assembly transfer
(``pipeline.check:assembly_preservation`` asks whether a split part matches the source it
came from — a collapsed source transfers perfectly). It answers one question: compared
with a recorded baseline, how much of the **evaluated** body is still there?

Two halves, matching the established ``inspect_preservation`` split:

- :func:`snapshot` runs in Blender and records per-object evaluated metrics.
- :func:`compare` is pure and compares two snapshot documents against a policy.

There is no default threshold. A legitimate decimation pass drops vertex counts on
purpose, so the required ratios belong to the asset, not to this module.
"""
from __future__ import annotations

import math

from .common import PipelineError

VERSION = 1

CRITERIA = ("min_vertex_ratio", "min_triangle_ratio", "min_span_ratio", "min_bbox_coverage")

LIMITS = [
    "Retention compares extents and counts; it does not compare vertex positions or topology.",
    "A body can lose internal detail, holes or shape while keeping its bbox and counts.",
    "Retained metrics are not visual acceptability, clearance, contact or user approval.",
    "Thresholds are supplied by the caller; this helper has no default and makes no art judgement.",
    "Frame-dependent and animated stacks compare only the frame each snapshot recorded.",
    "A listed object must exist in both snapshots; a deliberate deletion does not belong in a retention policy.",
]


def finite(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PipelineError(f"{field} must be a number")
    if not math.isfinite(value):
        raise PipelineError(f"{field} must be finite")
    return float(value)


def _unique_names(value, field, allow_empty=True):
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise PipelineError(f"{field} must be a list of non-empty names")
    if not value and not allow_empty:
        raise PipelineError(f"{field} must not be empty")
    if len(set(value)) != len(value):
        raise PipelineError(f"{field} has duplicate names")
    return list(value)


def validate_policy(policy):
    """Return the policy unchanged, or raise PipelineError.

    Every listed object must state at least one criterion. A criterion that is not stated
    is not checked, and the report says so rather than implying it passed. An object that
    is listed must exist in both snapshots: a deliberate deletion does not belong here.
    """
    if not isinstance(policy, dict):
        raise PipelineError("policy must be a JSON object")
    if set(policy) != {"version", "objects"}:
        raise PipelineError("policy must contain exactly version and objects")
    if type(policy["version"]) is not int or policy["version"] != VERSION:
        raise PipelineError("unsupported policy version")
    objects = policy["objects"]
    if not isinstance(objects, dict) or not objects:
        raise PipelineError("policy.objects must be a non-empty object")
    for name, rule in objects.items():
        if not isinstance(name, str) or not name.strip():
            raise PipelineError("policy.objects keys must be non-empty names")
        where = f"policy.objects[{name!r}]"
        if not isinstance(rule, dict):
            raise PipelineError(f"{where} must be an object")
        unknown = set(rule) - set(CRITERIA)
        if unknown:
            raise PipelineError(f"{where} has unknown criteria: {sorted(unknown)}")
        if not rule:
            raise PipelineError(f"{where} must state at least one criterion")
        for criterion, value in rule.items():
            number = finite(value, f"{where}.{criterion}")
            if not 0.0 <= number <= 1.0:
                raise PipelineError(f"{where}.{criterion} is a retained fraction and must be within 0..1")
    return policy


def validate_snapshot(document):
    """Validate a recorded snapshot; raises PipelineError on malformed input."""
    if not isinstance(document, dict) or set(document) != {"version", "context", "objects", "limits"}:
        raise PipelineError("snapshot must contain exactly version, context, objects, limits")
    if type(document["version"]) is not int or document["version"] != VERSION:
        raise PipelineError("unsupported snapshot version")
    context = document["context"]
    if not isinstance(context, dict) or set(context) != {"frame", "view_layer", "source_path"}:
        raise PipelineError("invalid snapshot context")
    if type(context["frame"]) is not int or not isinstance(context["view_layer"], str) or not context["view_layer"]:
        raise PipelineError("invalid snapshot context values")
    if not isinstance(context["source_path"], str):
        raise PipelineError("invalid snapshot source_path")
    objects = document["objects"]
    if not isinstance(objects, dict) or not objects:
        raise PipelineError("snapshot objects must be a non-empty object")
    for name, record in objects.items():
        if not isinstance(name, str) or not name.strip():
            raise PipelineError("snapshot object names must be non-empty")
        if not isinstance(record, dict) or set(record) != {"authored", "evaluated"}:
            raise PipelineError(f"snapshot object {name!r} must contain authored and evaluated")
        authored = record["authored"]
        if not isinstance(authored, dict) or set(authored) != {"vertices", "polygons", "modifiers"}:
            raise PipelineError(f"snapshot object {name!r} has an invalid authored record")
        for key in ("vertices", "polygons"):
            if type(authored[key]) is not int or authored[key] < 0:
                raise PipelineError(f"snapshot object {name!r} has an invalid authored count")
        _unique_names(authored["modifiers"], f"snapshot object {name!r} modifiers")
        evaluated = record["evaluated"]
        required = {"vertices", "triangles", "spans", "bbox", "components"}
        if not isinstance(evaluated, dict) or set(evaluated) != required:
            raise PipelineError(f"snapshot object {name!r} has an invalid evaluated record")
        for key in ("vertices", "triangles", "components"):
            if type(evaluated[key]) is not int or evaluated[key] < 0:
                raise PipelineError(f"snapshot object {name!r} has an invalid evaluated count")
        spans = evaluated["spans"]
        if not isinstance(spans, list) or len(spans) != 3:
            raise PipelineError(f"snapshot object {name!r} spans must be three numbers")
        for value in spans:
            if finite(value, "span") < 0.0:
                raise PipelineError("span must be nonnegative")
        bbox = evaluated["bbox"]
        if bbox is not None:
            if (not isinstance(bbox, list) or len(bbox) != 2
                    or any(not isinstance(corner, list) or len(corner) != 3 for corner in bbox)):
                raise PipelineError(f"snapshot object {name!r} has an invalid bbox")
            for corner in bbox:
                for value in corner:
                    finite(value, "bbox")
        if evaluated["vertices"] == 0 and bbox is not None:
            raise PipelineError(f"snapshot object {name!r} has an empty body but a bbox")
    if not isinstance(document["limits"], list) or any(not isinstance(item, str) for item in document["limits"]):
        raise PipelineError("invalid snapshot limits")
    return document


def _coverage(after_bbox, before_bbox):
    """Overlap volume of the after bbox inside the before bbox, as a fraction of before."""
    if after_bbox is None or before_bbox is None:
        return 0.0
    inside = 1.0
    outside = 1.0
    for axis in range(3):
        low = max(after_bbox[0][axis], before_bbox[0][axis])
        high = min(after_bbox[1][axis], before_bbox[1][axis])
        overlap = max(0.0, high - low)
        length = max(before_bbox[1][axis] - before_bbox[0][axis], 1e-9)
        inside *= overlap
        outside *= length
    return inside / outside


def _span_ratio(after_spans, before_spans):
    ratios = [after / before for after, before in zip(after_spans, before_spans) if before > 0.0]
    return min(ratios) if ratios else None


def compare(before, after, policy):
    """Compare two recorded snapshots. Inconclusive measures are errors, never passes."""
    validate_snapshot(before)
    validate_snapshot(after)
    validate_policy(policy)

    records = []
    for name, rule in policy["objects"].items():
        baseline = before["objects"].get(name)
        if baseline is None:
            records.append({"object": name, "status": "error",
                            "error_reason": "object not present in the before snapshot",
                            "criteria": [], "unchecked": [], "authored_changed": None})
            continue
        current = after["objects"].get(name)
        if current is None:
            records.append({"object": name, "status": "fail",
                            "error_reason": "object missing from after snapshot",
                            "criteria": [], "unchecked": list(rule), "authored_changed": None})
            continue

        old, new = baseline["evaluated"], current["evaluated"]
        if old["vertices"] == 0:
            records.append({"object": name, "status": "error",
                            "error_reason": "before snapshot has an empty evaluated body; ratios are undefined",
                            "criteria": [], "unchecked": [], "authored_changed": None})
            continue

        measures = {
            "min_vertex_ratio": new["vertices"] / old["vertices"],
            "min_triangle_ratio": (new["triangles"] / old["triangles"]) if old["triangles"] else None,
            "min_span_ratio": _span_ratio(new["spans"], old["spans"]),
            "min_bbox_coverage": _coverage(new["bbox"], old["bbox"]),
        }
        criteria = []
        unchecked = []
        inconclusive = False
        for criterion in CRITERIA:
            if criterion not in rule:
                unchecked.append(criterion)
                continue
            actual = measures[criterion]
            if actual is None:
                criteria.append({"criterion": criterion, "required": rule[criterion],
                                 "actual": None, "status": "error"})
                inconclusive = True
                continue
            actual = round(actual, 6)
            criteria.append({"criterion": criterion, "required": rule[criterion], "actual": actual,
                             "status": "pass" if actual + 1e-9 >= rule[criterion] else "fail"})

        statuses = {item["status"] for item in criteria}
        status = "error" if "error" in statuses else ("fail" if "fail" in statuses else "pass")
        record = {
            "object": name,
            "status": status,
            "criteria": criteria,
            "unchecked": unchecked,
            "evaluated_before": {"vertices": old["vertices"], "triangles": old["triangles"],
                                 "spans": old["spans"], "components": old["components"]},
            "evaluated_after": {"vertices": new["vertices"], "triangles": new["triangles"],
                                "spans": new["spans"], "components": new["components"]},
            "authored_changed": baseline["authored"] != current["authored"],
        }
        if status == "error":
            record["error_reason"] = "inconclusive measure (zero baseline count)"
        records.append(record)

    statuses = {record["status"] for record in records}
    overall = "error" if "error" in statuses else ("fail" if "fail" in statuses else "pass")
    return {
        "version": VERSION,
        "context": {"before": before["context"], "after": after["context"]},
        "objects": records,
        "status": overall,
        "limits": list(LIMITS),
    }


def validate_report(report):
    if not isinstance(report, dict) or set(report) != {"version", "context", "objects", "status", "limits"}:
        raise PipelineError("report must contain exactly version, context, objects, status, limits")
    if type(report["version"]) is not int or report["version"] != VERSION:
        raise PipelineError("unsupported report version")
    if report["status"] not in ("pass", "fail", "error"):
        raise PipelineError("invalid report status")
    if not isinstance(report["objects"], list) or not report["objects"]:
        raise PipelineError("report objects must be a non-empty list")
    for record in report["objects"]:
        if not isinstance(record, dict) or record.get("status") not in ("pass", "fail", "error"):
            raise PipelineError("invalid object status")
        if not isinstance(record.get("object"), str) or not record["object"]:
            raise PipelineError("invalid object name")
        if not isinstance(record.get("criteria"), list):
            raise PipelineError("invalid criteria list")
        for item in record["criteria"]:
            if not isinstance(item, dict) or set(item) != {"criterion", "required", "actual", "status"}:
                raise PipelineError("invalid criterion record")
            if item["criterion"] not in CRITERIA or item["status"] not in ("pass", "fail", "error"):
                raise PipelineError("invalid criterion")
            finite(item["required"], "required")
            if item["actual"] is not None:
                finite(item["actual"], "actual")
    statuses = {record["status"] for record in report["objects"]}
    expected = "error" if "error" in statuses else ("fail" if "fail" in statuses else "pass")
    if report["status"] != expected:
        raise PipelineError("report status disagrees with object statuses")
    return report


def _components(mesh):
    parent = list(range(len(mesh.vertices)))
    if not parent:
        return 0

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for edge in mesh.edges:
        left, right = find(edge.vertices[0]), find(edge.vertices[1])
        if left != right:
            parent[left] = right
    return len({find(index) for index in range(len(parent))})


def snapshot(object_names):
    """Record evaluated metrics for named meshes in the caller's current scene.

    Read-only: no object, modifier or scene state is modified. The caller owns the
    process and supplies the scene; this function never opens or saves a file.
    """
    import bpy

    if not isinstance(object_names, list) or not object_names:
        raise PipelineError("snapshot needs at least one object name")
    _unique_names(object_names, "objects", allow_empty=False)
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()

    objects = {}
    for name in object_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise PipelineError(f"object not found: {name}")
        if obj.type != "MESH":
            raise PipelineError(f"object is not a mesh: {name}")
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            matrix = evaluated.matrix_world
            coords = [matrix @ vertex.co for vertex in mesh.vertices]
            if coords:
                low = [round(min(point[axis] for point in coords), 6) for axis in range(3)]
                high = [round(max(point[axis] for point in coords), 6) for axis in range(3)]
                bbox = [low, high]
                spans = [round(high[axis] - low[axis], 6) for axis in range(3)]
            else:
                bbox = None
                spans = [0.0, 0.0, 0.0]
            objects[name] = {
                "authored": {
                    "vertices": len(obj.data.vertices),
                    "polygons": len(obj.data.polygons),
                    "modifiers": [modifier.name for modifier in obj.modifiers],
                },
                "evaluated": {
                    "vertices": len(mesh.vertices),
                    "triangles": len(mesh.loop_triangles),
                    "spans": spans,
                    "bbox": bbox,
                    "components": _components(mesh),
                },
            }
        finally:
            evaluated.to_mesh_clear()

    return {
        "version": VERSION,
        "context": {
            "frame": scene.frame_current,
            "view_layer": bpy.context.view_layer.name,
            "source_path": bpy.data.filepath or "",
        },
        "objects": objects,
        "limits": list(LIMITS),
    }
