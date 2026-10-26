"""Disposable Blender-only synthetic regression for the sampled exposure check.

blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python tools/asset-pipeline/fixtures/check_exposure.py

Builds new prefixed datablocks far from the startup cube, far from the world origin.
Never deletes, opens, saves or renders existing data. Raises on regression and prints a
JSON summary. Geometry state is asserted unchanged across every check.
"""
import json
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.exposure import sample_exposure, validate_report

# Far from the factory-startup cube at the origin, so "any" occluders stay meaningful.
BASE = (100.0, 100.0, 100.0)


def grid(verts, faces, x0, x1, z0, z1, nx=2, nz=2):
    start = len(verts)
    for iz in range(nz + 1):
        z = z0 + (z1 - z0) * iz / nz
        for ix in range(nx + 1):
            verts.append((x0 + (x1 - x0) * ix / nx, 0.0, z))
    for iz in range(nz):
        for ix in range(nx):
            a = start + iz * (nx + 1) + ix
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    return verts, faces


def plate():
    return grid([], [], -1.0, 1.0, 0.0, 2.0)


def frame(outer, hole, y):
    """Four flat bars around a rectangular opening, in one mesh."""
    ox0, ox1, oz0, oz1 = outer
    hx0, hx1, hz0, hz1 = hole
    verts, faces = [], []
    for x0, x1, z0, z1 in ((ox0, hx0, oz0, oz1), (hx1, ox1, oz0, oz1),
                           (hx0, hx1, oz0, hz0), (hx0, hx1, hz1, oz1)):
        if x1 - x0 <= 1e-9 or z1 - z0 <= 1e-9:
            continue
        start = len(verts)
        for x, z in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
            verts.append((x, y, z))
        faces.append((start, start + 1, start + 2, start + 3))
    return verts, faces


def main():
    import bpy

    prefix = "ExposureFixture_" + uuid.uuid4().hex[:8]
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer

    def snapshot(ours):
        return {
            obj.name: (len(obj.data.vertices), len(obj.data.polygons),
                       tuple(round(value, 6) for vertex in obj.data.vertices for value in vertex.co))
            for obj in bpy.data.objects
            if obj.type == "MESH" and obj.name.startswith(prefix) == ours
        }

    def build(label, verts, faces, location=BASE):
        mesh = bpy.data.meshes.new(prefix + label + "Mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.validate()
        mesh.update()
        obj = bpy.data.objects.new(prefix + label, mesh)
        obj.location = location
        scene.collection.objects.link(obj)
        return obj

    def reset():
        view_layer.update()
        return bpy.context.evaluated_depsgraph_get()

    def check(rules):
        report = sample_exposure({"version": 1, "targets": rules})
        validate_report(report)
        return report, {target["object"]: target for target in report["targets"]}

    before_state = snapshot(ours=False)
    before_selection = (scene.frame_current, tuple(obj.name for obj in bpy.context.selected_objects),
                        view_layer.objects.active.name if view_layer.objects.active else None)

    try:
        expected = {}

        # 1. Fully exposed target: pass.
        exposed = build("Exposed", *plate())
        # 2. Fully blocked target behind a wall: fail, blocker named.
        blocked = build("Blocked", *plate(), location=(BASE[0], BASE[1], BASE[2] + 3.0))
        build("Wall", *plate(), location=(BASE[0], BASE[1], BASE[2] + 3.0)).location.y -= 0.5
        # 3. Half blocked: fraction 0.5 decides the verdict.
        partial = build("Partial", *plate(), location=(BASE[0], BASE[1], BASE[2] + 6.0))
        half = build("HalfWall", *plate(), location=(BASE[0], BASE[1], BASE[2] + 6.0))
        half.location.y -= 0.5
        half.scale.x = 0.5
        half.location.x = BASE[0] - 0.5
        # 4. Small target seen through a frame opening (recess analogue): pass.
        recess = build("Recessed", *grid([], [], -0.4, 0.4, 0.6, 1.4),
                       location=(BASE[0], BASE[1], BASE[2] + 9.0))
        build("Frame", *frame((-1.5, 1.5, 0.0, 2.0), (-0.5, 0.5, 0.5, 1.5), -0.5),
              location=(BASE[0], BASE[1], BASE[2] + 9.0))
        # 5. Same target behind a misaligned opening: fail.
        hidden = build("Misaligned", *grid([], [], -0.4, 0.4, 0.6, 1.4),
                       location=(BASE[0], BASE[1], BASE[2] + 12.0))
        build("OffsetFrame", *frame((-1.5, 1.5, 0.0, 2.0), (0.5, 1.5, 0.5, 1.5), -0.5),
              location=(BASE[0], BASE[1], BASE[2] + 12.0))
        # 6. Occlusion created by a modifier, not by authored geometry.
        modified = build("Modified", *plate(), location=(BASE[0], BASE[1], BASE[2] + 15.0))
        array_wall = build("ArrayWall", *grid([], [], -0.8, 0.2, 0.0, 2.0, nx=1, nz=1),
                           location=(BASE[0], BASE[1], BASE[2] + 15.0))
        array_wall.location.y -= 0.5
        array = array_wall.modifiers.new(prefix + "Array", "ARRAY")
        array.count = 2
        array.use_relative_offset = True
        array.relative_offset_displace = (1.0, 0.0, 0.0)
        # 7. Transformed target: world-space sampling, not local coordinates.
        turned = build("Turned", *plate(), location=(BASE[0] + 30.0, BASE[1], BASE[2]))
        turned.rotation_euler[2] = 1.5707963267948966
        # 8. A blocker outside an explicit occluder list is surfaced, not accepted.
        unexpected = build("Unexpected", *plate(), location=(BASE[0], BASE[1], BASE[2] + 18.0))
        build("RoofPanel", *plate(), location=(BASE[0], BASE[1], BASE[2] + 18.0)).location.y -= 0.5
        # 9. Targets that cannot be sampled are errors, never passes.
        build("Empty", [], [])

        reset()
        authored = snapshot(ours=True)

        approach = [0.0, 1.0, 0.0]
        report, results = check([
            {"object": exposed.name, "approach": approach},
            {"object": blocked.name, "approach": approach, "occluders": [prefix + "Wall"]},
            {"object": partial.name, "approach": approach, "occluders": [prefix + "HalfWall"],
             "required_fraction": 0.5},
            {"object": recess.name, "approach": approach, "occluders": "any"},
            {"object": hidden.name, "approach": approach, "occluders": "any"},
            {"object": modified.name, "approach": approach, "occluders": "any"},
            {"object": turned.name, "approach": [-1.0, 0.0, 0.0], "occluders": "any"},
            {"object": unexpected.name, "approach": approach, "occluders": [prefix + "SomethingElse"]},
            {"object": prefix + "Missing", "approach": approach},
            {"object": prefix + "Empty", "approach": approach},
        ])

        expected["exposed"] = (results[exposed.name]["status"] == "pass"
                               and results[exposed.name]["visible"] == results[exposed.name]["samples_total"])
        expected["blocked"] = (results[blocked.name]["status"] == "fail"
                               and results[blocked.name]["blockers"]
                               == {prefix + "Wall": results[blocked.name]["samples_total"]})
        expected["partial_at_exactly_half"] = (results[partial.name]["status"] == "pass"
                                               and results[partial.name]["visible_fraction"] == 0.5)
        expected["recess_visible_through_opening"] = results[recess.name]["status"] == "pass"
        expected["misaligned_opening_blocks"] = results[hidden.name]["status"] == "fail"
        expected["modifier_occlusion_blocks_all"] = (results[modified.name]["blocked"]
                                                    == results[modified.name]["samples_total"])
        expected["transformed_target_passes"] = results[turned.name]["status"] == "pass"
        expected["unexpected_blocker_surfaced"] = (results[unexpected.name]["status"] == "fail"
                                                   and results[unexpected.name]["unexpected_blockers"] == [prefix + "RoofPanel"])
        expected["missing_target_is_error"] = results[prefix + "Missing"]["status"] == "error"
        expected["empty_target_is_error"] = results[prefix + "Empty"]["status"] == "error"
        expected["report_overall_error"] = report["status"] == "error"

        # The same run without the Array modifier must see through the right half, proving
        # that occlusion is read from evaluated geometry rather than authored vertices.
        array.show_viewport = False
        reset()
        _, without = check([{"object": modified.name, "approach": approach, "occluders": "any"}])
        expected["modifier_toggle_changes_result"] = (
            0 < without[modified.name]["blocked"] < results[modified.name]["blocked"])
        array.show_viewport = True
        reset()

        # Required fraction above the observed half must fail, not round up.
        _, strict = check([{"object": partial.name, "approach": approach,
                            "occluders": [prefix + "HalfWall"], "required_fraction": 0.6}])
        expected["fraction_boundary_is_fail"] = strict[partial.name]["status"] == "fail"

        # ignore_self governs whether the target's own geometry blocks its own samples.
        _, self_blocked = check([{"object": exposed.name, "approach": approach, "ignore_self": False}])
        expected["ignore_self_false_blocks_self"] = self_blocked[exposed.name]["status"] == "fail"

        # A surface that faces away from the viewer cannot be claimed as exposed.
        _, away = check([{"object": turned.name, "approach": [1.0, 0.0, 0.0]}])
        expected["facing_away_is_error"] = away[turned.name]["status"] == "error"
        _, away_all = check([{"object": turned.name, "approach": [1.0, 0.0, 0.0],
                              "sample_facing": "all"}])
        expected["sample_all_still_samples_rear_faces"] = away_all[turned.name]["samples_total"] > 0

        failed = sorted(name for name, ok in expected.items() if not ok)
        assert not failed, "exposure regressions: " + ", ".join(failed)
        assert snapshot(ours=False) == before_state, "fixture mutated unrelated mesh data"
        assert snapshot(ours=True) == authored, "exposure sampling mutated its own targets"
        assert before_selection == (scene.frame_current,
                                    tuple(obj.name for obj in bpy.context.selected_objects),
                                    view_layer.objects.active.name if view_layer.objects.active else None), \
            "fixture changed frame/selection/active object"

        print(json.dumps({
            "status": "pass",
            "fixture": prefix,
            "checks": expected,
            "counts": {name: {key: results[name][key] for key in
                              ("status", "visible", "blocked", "samples_total")}
                       for name in results},
            "limits": "Synthetic only; no asset, likeness or user acceptance.",
        }, indent=2, allow_nan=False))
    finally:
        for obj in [candidate for candidate in bpy.data.objects if candidate.name.startswith(prefix)]:
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if data is not None and data.users == 0 and isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)


if __name__ == "__main__":
    main()
