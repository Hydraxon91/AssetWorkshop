"""One stable CLI for reviewed disposable Blender stage plans; no shell fallback."""
import argparse
import json
from pathlib import Path
import sys
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import review_runner as runner
from pipeline.common import PipelineError


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    source = init.add_mutually_exclusive_group(required=True)
    source.add_argument('--plan')
    source.add_argument('--fixture-panel', action='store_true')
    init.add_argument('--blender')
    run = sub.add_parser('run')
    run.add_argument('--stage', required=True)
    run.add_argument('--timeout', type=float, default=90)
    status = sub.add_parser('status')
    for p in (init, run, status):
        p.add_argument('--manifest', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            plan = args.plan
            if args.fixture_panel:
                if not args.blender:
                    raise PipelineError('--fixture-panel requires explicit --blender')
                plan = str(Path(args.manifest).resolve().with_name('plan.json'))
                runner.review.write_new(plan, runner.panel_plan(args.manifest, args.blender))
            runner.prepare(args.manifest, plan)
            result = runner.status(args.manifest)
        elif args.command == 'run':
            result = runner.run(args.manifest, args.stage, args.timeout)
        else:
            result = runner.status(args.manifest)
        print(json.dumps(result, indent=2))
        return 0
    except (PipelineError, OSError, ValueError, KeyError, TypeError, TimeoutError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
