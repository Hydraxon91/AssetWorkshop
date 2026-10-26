"""Read-only path audit of pipeline jobs; never opens Blender or follows external paths.

Paths use the pipeline's repository-root semantics. This checks declared source,
GLB, gate and tile-image inputs and output destinations, not Blender internals,
object names, schema validity, image bytes or destination compatibility.
"""
import argparse
import hashlib
import json
from pathlib import Path


def inspect_path(root, value):
    root = Path(root).resolve()
    candidate = Path(value).expanduser()
    candidate = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        local = str(candidate.relative_to(root))
    except ValueError:
        # Do not probe an old repository, even for existence.
        return {'value': value, 'status': 'external-uninspected'}
    return {'value': value, 'local': local,
            'status': 'exists' if candidate.is_file() else 'missing'}


def audit(root, path):
    root, path = Path(root).resolve(), Path(path).resolve()
    raw = path.read_bytes()
    result = {'job': str(path.relative_to(root)),
              'sha256': hashlib.sha256(raw).hexdigest(), 'inputs': [], 'outputs': []}
    try:
        job = json.loads(raw)
        if not isinstance(job, dict):
            raise ValueError('job must be an object')
    except (ValueError, UnicodeError) as error:
        return dict(result, disposition='invalid-json', error=str(error))
    for key in ('source', 'glb'):
        if isinstance(job.get(key), str):
            result['inputs'].append(dict(inspect_path(root, job[key]), field=key))
    gate = job.get('gate')
    if isinstance(gate, dict):
        for key, value in gate.items():
            if isinstance(value, str):
                result['inputs'].append(dict(inspect_path(root, value), field='gate.' + key))
    tiles = job.get('tile_materials')
    if isinstance(tiles, dict):
        for name, spec in tiles.items():
            if isinstance(spec, dict) and isinstance(spec.get('base'), str):
                result['inputs'].append(dict(inspect_path(root, spec['base']),
                                             field='tile_materials.' + name + '.base'))
    if isinstance(job.get('out_dir'), str):
        output = inspect_path(root, job['out_dir'])
        if output['status'] != 'external-uninspected':
            output['status'] = 'local-destination-not-executed'
        result['outputs'].append(dict(output, field='out_dir'))
    blocked = any(x['status'] in ('missing', 'external-uninspected')
                  for x in result['inputs'] + result['outputs'])
    result['disposition'] = ('archival-blocked' if blocked else
                             'declared-paths-local-execution-unverified' if result['inputs']
                             else 'archival-requires-explicit-scene')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    root = args.root.resolve()
    jobs = sorted((root / 'tools/asset-pipeline/jobs').glob('*.job.json'))
    records = [audit(root, path) for path in jobs]
    summary = {status: sum(r['disposition'] == status for r in records)
               for status in sorted({r['disposition'] for r in records})}
    print(json.dumps({'scope': 'top-level pipeline jobs; originals unchanged',
                      'destination_compatibility': 'UNVERIFIED',
                      'summary': summary, 'jobs': records}, indent=2))


if __name__ == '__main__':
    main()
