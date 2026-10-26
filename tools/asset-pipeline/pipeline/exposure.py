"""Sampled viewing exposure: is the declared surface the first thing seen?

This is not an authored-preservation check (``pipeline.preservation`` asks whether
protected fields changed) and not an interface/contact check. It answers one narrow
question per declared target: along a declared viewing direction, is the first surface
met on each sample ray the target, or something else?

Policy (``version: 1``)::

    {"version": 1,
     "targets": [{"object": "Speaker_Face", "approach": [0, 1, 0],
                  "occluders": ["Body_Enclosure"], "samples": 16,
                  "required_fraction": 1.0}]}

``approach`` is the direction the viewer looks along. Ray origins sit ``backoff`` behind
each sample point, so a larger backoff starts further outside the asset.
"""
from __future__ import annotations

import math

from .common import PipelineError

VERSION = 1

RULE_FIELDS = ("object", "approach", "occluders", "samples", "required_fraction",
               "ignore_self", "require_front_facing", "sample_facing", "backoff")

STATUSES = ("visible", "blocked", "miss", "error")
RULE_STATUSES = ("pass", "fail", "error")

LIMITS = [
    "Sample rays answer only whether the first surface met from a declared direction is the target.",
    "Transparent materials are not considered; a window pane blocks a ray.",
    "Backface orientation is recorded, and only blocks when the rule requires front faces.",
    "A pass does not prove full surface exposure, recess depth, clearances or visual quality.",
    "Sample count is a coverage choice; more samples reduce missed occlusion, they do not certify it.",
]


def finite(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PipelineError(f"{field} must be a number")
    if not math.isfinite(value):
        raise PipelineError(f"{field} must be finite")
    return float(value)


def _unique_names(value, field, allow_empty=False):
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise PipelineError(f"{field} must be a list of non-empty names")
    if not value and not allow_empty:
        raise PipelineError(f"{field} must not be empty")
    if len(set(value)) != len(value):
        raise PipelineError(f"{field} has duplicate names")
    return list(value)


def validate_policy(policy):
    """Return normalised rules with defaults applied, or raise PipelineError."""
    if not isinstance(policy, dict) or set(policy) != {"version", "targets"}:
        raise PipelineError("policy must contain exactly version and targets")
    if type(policy["version"]) is not int or policy["version"] != VERSION:
        raise PipelineError("unsupported policy version")
    raw = policy["targets"]
    if not isinstance(raw, list) or not raw:
        raise PipelineError("policy.targets must be a non-empty list")

    rules = []
    seen = set()
    for index, rule in enumerate(raw):
        where = f"policy.targets[{index}]"
        if not isinstance(rule, dict):
            raise PipelineError(f"{where} must be an object")
        unknown = set(rule) - set(RULE_FIELDS)
        if unknown:
            raise PipelineError(f"{where} has unknown fields: {sorted(unknown)}")
        for required in ("object", "approach"):
            if required not in rule:
                raise PipelineError(f"{where}.{required} is required")

        name = rule["object"]
        if not isinstance(name, str) or not name.strip():
            raise PipelineError(f"{where}.object must be a non-empty name")
        if name in seen:
            raise PipelineError(f"{where}.object duplicates target {name}")
        seen.add(name)

        approach = rule["approach"]
        if not isinstance(approach, list) or len(approach) != 3:
            raise PipelineError(f"{where}.approach must be three numbers")
        vector = [finite(value, f"{where}.approach") for value in approach]
        length = math.sqrt(sum(value * value for value in vector))
        if length <= 1e-9:
            raise PipelineError(f"{where}.approach must be non-zero")

        occluders = rule.get("occluders", "any")
        if occluders != "any":
            occluders = _unique_names(occluders, f"{where}.occluders")
            if name in occluders:
                raise PipelineError(f"{where}.occluders must not repeat the target")

        samples = rule.get("samples", 16)
        if type(samples) is not int or not 1 <= samples <= 4096:
            raise PipelineError(f"{where}.samples must be an integer in 1..4096")

        fraction = finite(rule.get("required_fraction", 1.0), f"{where}.required_fraction")
        if not 0.0 <= fraction <= 1.0:
            raise PipelineError(f"{where}.required_fraction must be within 0..1")

        for key, default in (("ignore_self", True), ("require_front_facing", False)):
            if not isinstance(rule.get(key, default), bool):
                raise PipelineError(f"{where}.{key} must be a boolean")

        backoff = rule.get("backoff")
        if backoff is not None:
            backoff = finite(backoff, f"{where}.backoff")
            if backoff <= 0:
                raise PipelineError(f"{where}.backoff must be positive")

        facing = rule.get("sample_facing", "target")
        if facing not in ("target", "all"):
            raise PipelineError(f"{where}.sample_facing must be 'target' or 'all'")

        rules.append({
            "object": name,
            "approach": [value / length for value in vector],
            "occluders": occluders,
            "samples": samples,
            "required_fraction": fraction,
            "ignore_self": rule.get("ignore_self", True),
            "require_front_facing": rule.get("require_front_facing", False),
            "sample_facing": facing,
            "backoff": backoff,
        })
    return rules


def summarise(samples, required_fraction):
    """Classify a target's samples. Inconclusive samples never produce a pass."""
    counts = {status: 0 for status in STATUSES}
    blockers = {}
    unexpected = set()
    for item in samples:
        status = item.get("status")
        if status not in counts:
            raise PipelineError(f"unknown sample status: {status!r}")
        counts[status] += 1
        if status == "blocked":
            blocker = item.get("blocker")
            if not isinstance(blocker, str) or not blocker:
                raise PipelineError("blocked sample must name its blocker")
            blockers[blocker] = blockers.get(blocker, 0) + 1
            if item.get("unexpected_blocker"):
                unexpected.add(blocker)
    total = len(samples)
    result = {
        "samples_total": total,
        "visible": counts["visible"],
        "blocked": counts["blocked"],
        "miss": counts["miss"],
        "error": counts["error"],
        "required_fraction": required_fraction,
        "visible_fraction": None,
        "blockers": {name: blockers[name] for name in sorted(blockers)},
        "unexpected_blockers": sorted(unexpected),
        "status": "error",
    }
    if total == 0:
        result["error_reason"] = "no samples"
        return result
    if counts["miss"] or counts["error"]:
        # An inconclusive run must not be scored as a fraction of a partial surface.
        result["error_reason"] = "inconclusive samples (miss or evaluation error)"
        return result
    fraction = counts["visible"] / total
    result["visible_fraction"] = round(fraction, 6)
    result["status"] = "pass" if fraction + 1e-9 >= required_fraction else "fail"
    return result


def validate_report(report):
    """Validate a produced report; raises PipelineError on malformed input."""
    if not isinstance(report, dict) or set(report) != {"version", "context", "targets", "status", "limits"}:
        raise PipelineError("report must contain exactly version, context, targets, status, limits")
    if type(report["version"]) is not int or report["version"] != VERSION:
        raise PipelineError("unsupported report version")
    context = report["context"]
    if not isinstance(context, dict) or set(context) != {"frame", "view_layer", "source_path"}:
        raise PipelineError("invalid report context")
    if type(context["frame"]) is not int or not isinstance(context["view_layer"], str) or not context["view_layer"]:
        raise PipelineError("invalid report context values")
    if not isinstance(context["source_path"], str):
        raise PipelineError("invalid report source_path")
    if not isinstance(report["targets"], list) or not report["targets"]:
        raise PipelineError("report targets must be a non-empty list")
    if report["status"] not in RULE_STATUSES:
        raise PipelineError("invalid report status")
    if not isinstance(report["limits"], list) or any(not isinstance(item, str) for item in report["limits"]):
        raise PipelineError("invalid report limits")
    for target in report["targets"]:
        required = {"object", "status", "samples_total", "visible", "blocked", "miss", "error",
                    "required_fraction", "blockers", "unexpected_blockers", "samples"}
        if not isinstance(target, dict) or not required <= set(target):
            raise PipelineError("incomplete target record")
        if target["status"] not in RULE_STATUSES:
            raise PipelineError("invalid target status")
        if not isinstance(target["object"], str) or not target["object"]:
            raise PipelineError("invalid target object")
        if any(type(target[key]) is not int or target[key] < 0
               for key in ("samples_total", "visible", "blocked", "miss", "error")):
            raise PipelineError("invalid target counts")
        if sum(target[key] for key in ("visible", "blocked", "miss", "error")) != target["samples_total"]:
            raise PipelineError("target counts do not sum to samples_total")
        if len(target["samples"]) != target["samples_total"]:
            raise PipelineError("sample list length disagrees with samples_total")
        if not isinstance(target["blockers"], dict) or not isinstance(target["unexpected_blockers"], list):
            raise PipelineError("invalid blocker report")
        finite(target["required_fraction"], "required_fraction")
    statuses = {target["status"] for target in report["targets"]}
    expected = "error" if "error" in statuses else ("fail" if "fail" in statuses else "pass")
    if report["status"] != expected:
        raise PipelineError("report status disagrees with target statuses")
    return report


def _sample_points(obj, depsgraph, limit, direction, facing):
    """Deterministic evaluated sample points: (world point, world normal) pairs.

    With ``facing == 'target'`` only triangles presenting to the viewer are sampled.
    Sampling a rear or side face asks whether a surface that cannot face the viewer is
    visible, which is not a defect; ``facing == 'all'`` keeps every triangle.
    """
    import bpy  # noqa: F401  (consumer supplies the Blender runtime)

    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        triangles = mesh.loop_triangles
        if not triangles:
            return None
        matrix = evaluated.matrix_world
        normal_matrix = matrix.to_3x3().inverted_safe().transposed()
        view = -direction
        candidates = []
        for triangle in triangles:
            normal = (normal_matrix @ triangle.normal).normalized()
            if facing == "target" and normal.dot(view) <= 1e-6:
                continue
            candidates.append((matrix @ triangle.center, normal))
        if not candidates:
            return []
        step = max(1, len(candidates) // limit)
        return candidates[::step][:limit]
    finally:
        evaluated.to_mesh_clear()


def _bounds_diagonal(obj):
    from mathutils import Vector

    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return max(
        (max(c[i] for c in corners) - min(c[i] for c in corners)) for i in range(3)
    )


def _original_name(hit_object):
    base = getattr(hit_object, "original", hit_object)
    return getattr(base, "name", None)


def _inconclusive(rule, reason):
    """A target that could not be sampled is an error record, never a silent pass."""
    return {
        "object": rule["object"], "status": "error", "error_reason": reason,
        "samples_total": 1, "visible": 0, "blocked": 0, "miss": 0, "error": 1,
        "required_fraction": rule["required_fraction"], "visible_fraction": None,
        "blockers": {}, "unexpected_blockers": [],
        "samples": [{"status": "error", "reason": reason}],
        "backoff": rule["backoff"],
        "sample_facing": rule["sample_facing"],
    }


def sample_exposure(policy):
    """Sample declared targets in the caller's current scene.

    Read-only: no object, modifier or scene state is modified. The caller owns the
    process and supplies the scene; this function never opens or saves a file.
    """
    import bpy
    from mathutils import Vector

    rules = validate_policy(policy)
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    context = {
        "frame": scene.frame_current,
        "view_layer": bpy.context.view_layer.name,
        "source_path": bpy.data.filepath or "",
    }

    targets = []
    for rule in rules:
        target = bpy.data.objects.get(rule["object"])
        if target is None or target.type != "MESH":
            targets.append(_inconclusive(rule, "mesh target not found"))
            continue

        direction = Vector(rule["approach"])
        points = _sample_points(target, depsgraph, rule["samples"], direction, rule["sample_facing"])
        if points is None:
            targets.append(_inconclusive(rule, "target has no evaluated triangles"))
            continue
        if not points:
            targets.append(_inconclusive(
                rule, "no evaluated triangles face the approach direction"))
            continue

        backoff = rule["backoff"] if rule["backoff"] is not None else max(1.0, 2.0 * _bounds_diagonal(target))
        occluders = rule["occluders"]

        samples = []
        for point, normal in points:
            origin = point - direction * backoff
            hit, location, hit_normal, _index, hit_object, _matrix = scene.ray_cast(
                depsgraph, origin, direction, distance=backoff * 4.0
            )
            is_self = False
            blocker = None
            alignment = None
            unexpected = False
            if not hit:
                status = "miss"
            else:
                name = _original_name(hit_object)
                is_self = name == rule["object"]
                alignment = round((-direction).dot(hit_normal), 6)
                if is_self and rule["ignore_self"]:
                    status = "visible"
                else:
                    status = "blocked"
                    blocker = name
                    unexpected = not is_self and occluders != "any" and name not in occluders
                if status == "visible" and rule["require_front_facing"] and alignment <= 0.0:
                    status = "blocked"
                    blocker = name
            record = {
                "point": [round(value, 6) for value in point],
                "status": status,
                "target_facing": round(normal.dot(-direction), 6),
                "front_facing": None if alignment is None else alignment > 0.0,
                "hit_normal_alignment": alignment,
            }
            if blocker is not None:
                record["blocker"] = blocker
            if unexpected:
                record["unexpected_blocker"] = True
            if hit:
                record["hit_location"] = [round(value, 6) for value in location]
            samples.append(record)

        summary = summarise(samples, rule["required_fraction"])
        targets.append({
            "object": rule["object"],
            "backoff": round(backoff, 6),
            "sample_facing": rule["sample_facing"],
            "samples": samples,
            **summary,
        })

    statuses = {target["status"] for target in targets}
    overall = "error" if "error" in statuses else ("fail" if "fail" in statuses else "pass")
    return {
        "version": VERSION,
        "context": context,
        "targets": targets,
        "status": overall,
        "limits": list(LIMITS),
    }
