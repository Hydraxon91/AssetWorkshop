"""Standalone inspection; never opens/saves blends or mutates source objects.

In a Blender process whose caller has already supplied trusted named meshes:
  this.py -- snapshot --objects Trunk Canopy --out NEW.json
Factory startup alone does not provide these objects. This helper never loads a scene.
python this.py compare --before before.json --after after.json --policy policy.json --out NEW.json
Exit: 0 success, 1 comparison failed, 2 invalid input/output. No overwrite.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.common import PipelineError
from pipeline.preservation import compare, strict_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    snap = sub.add_parser('snapshot')
    snap.add_argument('--objects', nargs='+', required=True)
    snap.add_argument('--external-image', action='append', default=[], help='explicit exact external image path allowed for reading')
    snap.add_argument('--out', required=True)
    comp = sub.add_parser('compare')
    for key in ('before', 'after', 'policy', 'out'):
        comp.add_argument('--' + key, required=True)
    args = parser.parse_args(argv)
    try:
        out = Path(args.out).resolve()
        inputs = [Path(getattr(args, k)).resolve() for k in ('before', 'after', 'policy')] if args.command == 'compare' else [Path(p).resolve() for p in args.external_image]
        if out in inputs or out.exists():
            raise PipelineError('output collides with existing/input path')
        if args.command == 'compare':
            result = compare(*(strict_json(p.read_text(encoding='utf-8')) for p in inputs))
        else:
            from pipeline.inspection import snapshot
            result = snapshot(args.objects, external_images=args.external_image)
        payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n'
        with out.open('x', encoding='utf-8') as stream:
            stream.write(payload)
        return 1 if result.get('status') == 'fail' else 0
    except (PipelineError, OSError, ValueError, ImportError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None))
