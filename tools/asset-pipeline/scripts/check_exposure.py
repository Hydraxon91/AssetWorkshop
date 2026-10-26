"""Sampled exposure check for an already-open Blender scene.

The caller supplies the scene; this helper never opens, saves or renders a file and
never modifies objects. Run inside Blender after the scene is loaded:

  blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
    --python tools/asset-pipeline/scripts/check_exposure.py -- \
    --policy policy.json --out report.json

Exit: 0 pass, 1 fail, 2 invalid input/output. Reports are never overwritten.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.common import PipelineError
from pipeline.exposure import sample_exposure, validate_report
from pipeline.preservation import strict_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True, help="exposure policy JSON")
    parser.add_argument("--out", required=True, help="new report path")
    args = parser.parse_args(argv)
    try:
        policy_path = Path(args.policy).resolve()
        out = Path(args.out).resolve()
        if out == policy_path or out.exists():
            raise PipelineError("output collides with an existing or input path")
        report = sample_exposure(strict_json(policy_path.read_text(encoding="utf-8")))
        validate_report(report)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
        summary = [
            {
                "object": target["object"],
                "status": target["status"],
                "visible": target["visible"],
                "blocked": target["blocked"],
                "samples_total": target["samples_total"],
                "blockers": target["blockers"],
            }
            for target in report["targets"]
        ]
        print(json.dumps({"status": report["status"], "targets": summary}, indent=2))
        return 0 if report["status"] == "pass" else 1
    except (PipelineError, OSError, ValueError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None))
