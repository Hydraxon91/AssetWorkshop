"""Disposable Blender regression for evaluated retention.

blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python tools/asset-pipeline/fixtures/check_retention.py

Builds prefixed datablocks far from the startup cube. Never deletes, opens, saves,
renders or exports existing data. Raises on regression and prints a JSON summary.

The defect this fixture pins is the one demonstrated on the truck: a modifier-driven
collapse leaves the authored mesh byte-identical, so authored checks and mesh_health both
stay green while the evaluated body is gone.
"""
import json
from pathlib import Path
import sys
import tempfile
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.check import assembly_preservation, mesh_health
from pipeline.retention import compare, snapshot, validate_report, validate_snapshot

BASE = (200.0, 200.0, 200.0)


def cube(bpy, prefix, label, size, location):
    mesh = bpy.data.meshes.new(prefix + label + "Mesh")
    half = size / 2.0
    verts = [(x, y, z) for x in (-half, half) for y in (-half, half) for z in (-half, half)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.update()
    obj = bpy.data.objects.new(prefix + label, mesh)
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    return obj


def main():
    import bpy

    prefix = "RetentionFixture_" + uuid.uuid4().hex[:8]
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer
    scratch = Path(tempfile.mkdtemp(prefix="retention-fixture-"))

    def build(label, size, location, z_offset=0.0):
        return cube(bpy, prefix, label, size, (location[0], location[1], location[2] + z_offset))

    def authored_state():
        return {
            obj.name: (len(obj.data.vertices), len(obj.data.polygons),
                       tuple(round(v, 6) for vertex in obj.data.vertices for v in vertex.co))
            for obj in bpy.data.objects
            if obj.type == "MESH" and obj.name.startswith(prefix)
        }

    before_scene = {
        obj.name: (len(obj.data.vertices), len(obj.data.polygons))
        for obj in bpy.data.objects
        if obj.type == "MESH" and not obj.name.startswith(prefix)
    }
    before_ui = (scene.frame_current,
                 tuple(obj.name for obj in bpy.context.selected_objects),
                 view_layer.objects.active.name if view_layer.objects.active else None)

    try:
        # Target body and a cutter that mostly removes it but does not touch its authored
        # mesh. Boolean is chosen because it is the mechanism that produced the real defect.
        body = build("Body", 2.0, BASE)
        cutter = build("Cutter", 2.4, BASE)
        cutter.location.x = BASE[0] + 3.0          # clear of the body at the baseline
        boolean = body.modifiers.new(prefix + "Cut", "BOOLEAN")
        boolean.operation = "DIFFERENCE"
        boolean.object = cutter
        boolean.solver = "EXACT"

        # A second, independent body used for the "object vanished" and empty cases.
        witness = build("Witness", 1.0, (BASE[0] + 10.0, BASE[1], BASE[2]))

        bpy.context.view_layer.update()

        baseline = snapshot([body.name, witness.name])
        validate_snapshot(baseline)
        baseline_authored = authored_state()
        baseline_health = mesh_health([body], require_closed=False)

        # --- 1. intact: every criterion passes -------------------------------
        policy = {"version": 1,
                  "objects": {body.name: {"min_vertex_ratio": 0.85,
                                          "min_triangle_ratio": 0.85,
                                          "min_span_ratio": 0.99,
                                          "min_bbox_coverage": 0.995}}}
        intact = compare(baseline, baseline, policy)
        validate_report(intact)
        intact_ok = intact["status"] == "pass"

        # --- 2. collapse: evaluated body gone, authored identical ------------
        # A 2.4 cutter centred 0.3 to the -X side covers everything except a 0.1 slab.
        cutter.location.x = BASE[0] - 0.3
        bpy.context.view_layer.update()
        collapsed = snapshot([body.name, witness.name])
        report = compare(baseline, collapsed, policy)
        validate_report(report)
        record = report["objects"][0]
        measured = {item["criterion"]: item["actual"] for item in record["criteria"]}
        authored_unchanged = authored_state() == baseline_authored
        health_still_ok = mesh_health([body], require_closed=False)["ok"]
        collapse_ok = (report["status"] == "fail"
                       and measured["min_span_ratio"] < 0.99
                       and measured["min_bbox_coverage"] < 0.995
                       and authored_unchanged
                       and health_still_ok
                       and record["authored_changed"] is False)

        # --- 3. restore: the same stack measures intact again ---------------
        cutter.location.x = BASE[0] + 3.0
        bpy.context.view_layer.update()
        restored = compare(baseline, snapshot([body.name, witness.name]), policy)
        restored_ok = restored["status"] == "pass"

        # --- 4. total removal: zero after is a measured fail, not a crash ----
        cutter.location.x = BASE[0]                 # concentric 2.4 cutter swallows the body
        bpy.context.view_layer.update()
        empty_snapshot = snapshot([body.name, witness.name])
        gone = compare(baseline, empty_snapshot, policy)
        validate_report(gone)
        gone_record = gone["objects"][0]
        empty_after = empty_snapshot["objects"][body.name]["evaluated"]["vertices"] == 0
        zero_fraction_ok = (gone["status"] == "fail" and empty_after
                            and all(item["actual"] == 0.0 for item in gone_record["criteria"]))

        # --- 5. an empty source in assembly_preservation is a failure, not an exception
        assembly_doc = scratch / (prefix + "_assembly.json")
        assembly_doc.write_text(json.dumps({"groups": [{"source_objects": [body.name],
                                                        "parts": [witness.name]}]}))
        guard = assembly_preservation(str(assembly_doc), [scene.frame_current])
        assembly_guard_ok = (guard["ok"] is False and guard["failures"]
                             and guard["failures"][0]["max_bidirectional_distance_m"] is None)

        # --- 6. thresholds come from the policy, never from a default --------
        loud = {"version": 1, "objects": {body.name: {"min_vertex_ratio": 0.0}}}
        loose = compare(baseline, empty_snapshot, loud)
        unstated_ok = (set(loose["objects"][0]["unchecked"])
                       == {"min_triangle_ratio", "min_span_ratio", "min_bbox_coverage"})

        # --- 7. a missing object is a retention failure ----------------------
        missing = compare(snapshot([body.name]), snapshot([witness.name]),
                          {"version": 1, "objects": {body.name: {"min_vertex_ratio": 0.5}}})
        missing_ok = (missing["status"] == "fail"
                      and "missing" in missing["objects"][0]["error_reason"])

        # --- 8. an empty baseline is inconclusive ----------------------------
        inconclusive = compare(empty_snapshot, baseline, policy)
        inconclusive_ok = inconclusive["status"] == "error"

        expected = {
            "intact_passes": intact_ok,
            "collapse_fails_with_measured_ratios": collapse_ok,
            "authored_mesh_unchanged_by_collapse": authored_unchanged,
            "mesh_health_blind_to_collapse": health_still_ok,
            # The collapsed slab keeps all 8 authored vertices, so vertex count alone would
            # report "retained". Extents are what catch this shape of failure.
            "vertex_count_alone_would_miss_this": measured["min_vertex_ratio"] >= 0.85,
            "restore_measures_intact_again": restored_ok,
            "total_removal_is_zero_not_crash": zero_fraction_ok,
            "assembly_empty_source_reports_failure": assembly_guard_ok,
            "unstated_criteria_are_unchecked": unstated_ok,
            "missing_object_fails": missing_ok,
            "empty_baseline_is_error": inconclusive_ok,
        }

        measurements = {
            "baseline_vertices": baseline["objects"][body.name]["evaluated"]["vertices"],
            "collapsed_vertices": collapsed["objects"][body.name]["evaluated"]["vertices"],
            "baseline_spans": baseline["objects"][body.name]["evaluated"]["spans"],
            "collapsed_spans": collapsed["objects"][body.name]["evaluated"]["spans"],
            "measured": measured,
            "authored_unchanged": authored_unchanged,
            "health_still_ok": health_still_ok,
            "report_status": report["status"],
        }
        failed = sorted(name for name, ok in expected.items() if not ok)
        assert not failed, ("retention regressions: " + ", ".join(failed) + " :: "
                            + json.dumps(measurements, sort_keys=True))

        if assembly_doc.exists():
            assembly_doc.unlink()
        scratch.rmdir()

        after_scene = {
            obj.name: (len(obj.data.vertices), len(obj.data.polygons))
            for obj in bpy.data.objects
            if obj.type == "MESH" and not obj.name.startswith(prefix)
        }
        after_ui = (scene.frame_current,
                    tuple(obj.name for obj in bpy.context.selected_objects),
                    view_layer.objects.active.name if view_layer.objects.active else None)
        assert after_scene == before_scene, "fixture changed unrelated mesh data"
        assert after_ui == before_ui, "fixture changed frame/selection/active object"

        print(json.dumps({
            "status": "pass",
            "fixture": prefix,
            "checks": expected,
            "measurements": measurements,
            "limits": "Synthetic only; no asset, likeness or user acceptance.",
        }, indent=2, allow_nan=False))
    finally:
        for path in scratch.glob("*.json"):
            path.unlink()
        try:
            scratch.rmdir()
        except OSError:
            pass
        for obj in [candidate for candidate in bpy.data.objects if candidate.name.startswith(prefix)]:
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if data is not None and data.users == 0 and isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)


if __name__ == "__main__":
    main()
