# Disposable Blender construction tests

Review exact scripts/inputs before using this standard-library-only runner.
Use before unproven native mesh operations reach interactive Blender.

```sh
python3 tools/blender-safe/run.py \
  --blender /Applications/Blender.app/Contents/MacOS/Blender \
  --script path/to/reviewed.py --mesh path/to/mesh.json \
  --run-dir .dev-shots/asset/unique-test-01 --timeout 30 --threads 1
```

Mesh JSON: `vertices: [[x,y,z],...]`, `faces: [[index,...],...]`. The script
receives the copied mesh path after `--` in `sys.argv` and must use it. Retain
profiles/parameters alongside the script. Outputs belong in the new run directory;
never open user baselines or run integration in a construction test.

## Enforced

- Refuses existing run directories; snapshots and hashes script/mesh inputs.
- Blocks invalid indices, nonfinite coordinates, duplicate face vertex sets,
  repeated face vertices, zero area vectors, branching edges, inconsistent winding,
  disconnected parts, loose vertices and unexpected boundaries. Pilot budget:
  5000vertices/10000faces. Open shells require explicit `--allow-boundary`.
- Starts factory/background Blender, autoexec disabled, 1–2 threads.
- Wall-clock timeout (default30s, max120s), kills/reaps only its owned process group.
  Removes lingering descendants on completion. No automatic retry or live signals.
- Logs stdout/stderr, command, hashes, timestamps, elapsed time and exit status.

## Limits

Process isolation is **not a security sandbox**. Reviewed Python still has normal
filesystem/process privileges and can ignore inputs. Thread settings do not cap
every library's CPU/GPU use or memory. Preflight is not proof against intersecting
surfaces, inward normals, poor n-gon triangulation, wrong thickness or wrong shape.

Exit0 means process completed, NOT approved geometry. Reports leave geometry,
shape and integration approval false. Independently inspect Blender health and
captures; parent authorizes separate integration after shape, health and protected
state gates pass. Successful tests do not authorize arbitrary live scripts.

Tests use stub processes, never Blender:

```sh
python3 -m unittest discover -s tools/blender-safe -p 'test_*.py' -v
```
