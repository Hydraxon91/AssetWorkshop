"""Bundled save/check/fixed-capture operations for a single-mesh review fixture.

Caller owns a disposable process and supplies the saved scene. No live-scene use.
Not a universal asset validator: check preserves authored geometry/transform only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector, Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mesh_diagnostics import health
from capture_review import capture_fixed


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def measured(obj):
    report = health(obj)
    keys = ('boundary_edges', 'nonmanifold_edges', 'wire_edges', 'loose_verts',
            'winding_conflicts', 'degenerate_faces')
    clean = all(all(part[key] == 0 for key in keys) and part['islands'] == 1
                and part['components'] and all(c['closed'] for c in part['components'])
                for part in (report['base'], report['evaluated']))
    base = dict(vertices=[list(v.co) for v in obj.data.vertices],
                polygons=[list(p.vertices) for p in obj.data.polygons])
    corners = [obj.matrix_world @ v.co for v in obj.data.vertices]
    bounds = [[min(v[i] for v in corners) for i in range(3)],
              [max(v[i] for v in corners) for i in range(3)]]
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        evaluated_bounds = [[min(v[i] for v in points) for i in range(3)],
                            [max(v[i] for v in points) for i in range(3)]]
    finally:
        evaluated.to_mesh_clear()
    return dict(health=report, clean=bool(clean),
                signature=hashlib.sha256(json.dumps(base, sort_keys=True).encode()).hexdigest(),
                matrix=[[float(v) for v in row] for row in obj.matrix_world], bounds=bounds,
                evaluated_bounds=evaluated_bounds,
                modifiers=[m.type for m in obj.modifiers])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['save', 'check', 'capture'])
    parser.add_argument('--out', required=True)
    parser.add_argument('--object', default='Trial_Panel')
    parser.add_argument('--baseline')
    parser.add_argument('--report')
    parser.add_argument('--metadata')
    parser.add_argument('--expected-modifier')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if not bpy.app.background:
        raise RuntimeError('disposable background only')
    out = Path(args.out).resolve()
    if out.exists():
        raise FileExistsError(out)
    source = Path(bpy.data.filepath)
    if not source.is_file():
        raise RuntimeError('need an already loaded saved scene')
    source_sha = sha(source)
    if args.operation == 'save':
        out.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(out), check_existing=False)
        print(json.dumps(dict(checkpoint=str(out), sha256=sha(out))))
        return
    obj = bpy.data.objects[args.object]
    bpy.context.view_layer.update()
    if args.operation == 'check':
        current = measured(obj)
        passed = current['clean']
        if args.baseline:
            baseline = json.loads(Path(args.baseline).read_text())
            if baseline['status'] != 'pass':
                raise RuntimeError('failed baseline')
            old = baseline['measured']
            passed = passed and all(current[k] == old[k] for k in ('signature', 'matrix', 'bounds'))
            passed = passed and all(abs(a-b) <= 1e-6
                                    for aa,bb in zip(current['evaluated_bounds'], old['evaluated_bounds'])
                                    for a,b in zip(aa,bb))
            if args.expected_modifier:
                passed = passed and current['health']['evaluated']['tris'] > old['health']['evaluated']['tris']
        passed = passed and current['modifiers'] == ([args.expected_modifier] if args.expected_modifier else [])
        dump(out, dict(status='pass' if passed else 'fail', blend=str(source.resolve()),
                       blend_sha256=source_sha, measured=current,
                       limits='Fixture health and authored geometry/transform only, not likeness/acceptance'))
        if not passed:
            raise RuntimeError('check failed; inspect report')
        return
    if not args.report or not args.metadata:
        raise RuntimeError('capture requires report and metadata output')
    report = json.loads(Path(args.report).read_text())
    if report['status'] != 'pass' or report['blend_sha256'] != source_sha:
        raise RuntimeError('capture needs passing check for these saved bytes')
    if Path(args.metadata).exists():
        raise FileExistsError(args.metadata)
    # Baseline fixes the camera, even if the after geometry later changes bounds.
    baseline = json.loads(Path(args.baseline or args.report).read_text())
    low, high = map(Vector, baseline['measured']['bounds'])
    center, size = (low + high) / 2, max(high - low)
    location = center + Vector((1,-1,0.65)).normalized() * 3
    rotation = (center-location).to_track_quat('-Z', 'Y')
    matrix = Matrix.Translation(location) @ rotation.to_matrix().to_4x4()
    capture_fixed(out, args.metadata, checkpoint=source, view='three_quarter',
                  resolution=[900,800], camera_spec=dict(matrix_world=[list(row) for row in matrix],
                                                        type='ORTHO', lens=50, ortho_scale=size*1.25))


if __name__ == '__main__':
    main()
