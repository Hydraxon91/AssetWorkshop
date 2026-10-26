"""Record checkpoint/check/capture evidence without rerunning completed work."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import review_session as review
from pipeline.common import PipelineError


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--goal', required=True)
    init.add_argument('--construction-stop', type=int, required=True)
    init.add_argument('--deadline', type=int, required=True)
    init.add_argument('--views', nargs='+', required=True)
    rec = sub.add_parser('record')
    rec.add_argument('--kind', choices=['checkpoint', 'check', 'capture'], required=True)
    rec.add_argument('--role', choices=['before', 'after'], required=True)
    rec.add_argument('--file', required=True)
    rec.add_argument('--step', type=int, required=True)
    rec.add_argument('--outcome', choices=['pass', 'fail', 'error'])
    rec.add_argument('--view')
    rec.add_argument('--metadata')
    stat = sub.add_parser('status')
    stat.add_argument('--step', type=int)
    budget = sub.add_parser('budget')
    budget.add_argument('--continuation', required=True)
    budget.add_argument('--construction-stop', type=int, required=True)
    budget.add_argument('--deadline', type=int, required=True)
    budget.add_argument('--reason', required=True)
    sheet = sub.add_parser('sheet')
    sheet.add_argument('--out', required=True)
    for command in (init, rec, stat, sheet, budget):
        command.add_argument('--manifest', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            review.create(args.manifest, args.goal, args.construction_stop, args.deadline, args.views)
        elif args.command == 'record':
            review.record(args.manifest, args.kind, args.role, args.file, args.step,
                          args.outcome, args.view, args.metadata)
        elif args.command == 'budget':
            review.begin_budget(args.manifest, args.continuation, args.construction_stop,
                                args.deadline, args.reason)
        elif args.command == 'status':
            print(json.dumps(review.status(args.manifest, args.step), indent=2))
        else:
            review.sheet(args.manifest, args.out)
        return 0
    except (PipelineError, OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
