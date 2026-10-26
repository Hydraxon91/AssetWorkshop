"""Evaluated-retention check: record a baseline, then compare a later state to it.

Two commands, because only one of them needs Blender:

  # record (inside Blender, on the scene the caller already loaded)
  blender --background --factory-startup --disable-autoexec asset.blend \
    --python-exit-code 1 --python tools/asset-pipeline/scripts/check_retention.py -- \
    snapshot --objects Truck_MainShell --out before.json

  # compare (plain Python; no Blender needed)
  python tools/asset-pipeline/scripts/check_retention.py compare \
    --before before.json --after after.json --policy retention.json --out report.json

Exit: 0 pass, 1 fail, 2 invalid input/output. Nothing is overwritten. The snapshot command
never opens or saves a .blend; the caller supplies the scene.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.common import PipelineError
from pipeline.preservation import strict_json
from pipeline.retention import compare, snapshot, validate_report, validate_snapshot


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("snapshot", help="record evaluated metrics in the current scene")
    record.add_argument("--objects", nargs="+", required=True)
    record.add_argument("--out", required=True)

    check = sub.add_parser("compare", help="compare two recorded snapshots")
    for key in ("before", "after", "policy", "out"):
        check.add_argument("--" + key, required=True)

    args = parser.parse_args(argv)
    try:
        out = Path(args.out).resolve()
        if args.command == "compare":
            inputs = [Path(getattr(args, key)).resolve() for key in ("before", "after", "policy")]
            if out in inputs or out.exists():
                raise PipelineError("output collides with an existing or input path")
            before, after, policy = (strict_json(path.read_text(encoding="utf-8"))
                                     for path in inputs)
            report = compare(before, after, policy)
            validate_report(report)
        else:
            if out.exists():
                raise PipelineError(f"refusing to overwrite {out}")
            report = snapshot(args.objects)
            validate_snapshot(report)

        _write(out, report)
        if args.command == "snapshot":
            summary = {
                "status": "recorded",
                "objects": [{"object": name, "evaluated": record["evaluated"]}
                            for name, record in report["objects"].items()],
            }
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 0
        summary = {
            "status": report["status"],
            "objects": [
                {
                    "object": item["object"],
                    "status": item["status"],
                    "criteria": {entry["criterion"]: entry["actual"] for entry in item["criteria"]},
                    "unchecked": item.get("unchecked", []),
                    "error_reason": item.get("error_reason"),
                }
                for item in report["objects"]
            ],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0 if report["status"] == "pass" else 1
    except (PipelineError, OSError, ValueError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None))
