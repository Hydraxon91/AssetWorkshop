"""Background-only CLI for the reusable box adapter, not a process runner."""
import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / 'scripts'))
from pipeline import primitive_recipe as recipe_tool
from pipeline.common import PipelineError, sha256_file


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)


def main():
    args_in = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'build', 'prepare', 'check', 'capture'])
    parser.add_argument('--recipe', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--stage', choices=['master', 'prepared', 'uv', 'baked'], default='master')
    parser.add_argument('--empty-startup', action='store_true')
    parser.add_argument('--metadata')
    parser.add_argument('--report')
    parser.add_argument('--blender')
    parser.add_argument('--phase', choices=['geometry', 'appearance'], default='geometry')
    parser.add_argument('--source')
    args = parser.parse_args(args_in)
    recipe = recipe_tool.load(args.recipe)  # Validate data before any native mutation.
    out = Path(args.out).resolve()
    if out.exists():
        raise FileExistsError(out)
    if args.action == 'plan':
        if not args.blender or not Path(args.blender).is_file():
            raise PipelineError('plan requires explicit existing --blender executable')
        plan, jobs = recipe_tool.stage_plan(args.recipe, out.parent, args.blender,
                                           args.phase, args.source)
        if any((out.parent / key).exists() for key in jobs):
            raise FileExistsError('companion job exists')
        write_new(out, plan)
        for key, job in jobs.items():
            write_new(out.parent / key, job)
        return
    import bpy
    recipe_tool._background()
    if args.action in ('build', 'prepare'):
        if out.suffix != '.blend':
            raise PipelineError('work snapshot must end .blend')
        result = (recipe_tool.build(recipe, args.empty_startup) if args.action == 'build'
                  else recipe_tool.prepare(recipe))
        out.parent.mkdir(parents=True, exist_ok=True)
        # Working snapshot crosses process boundaries; final save is a separate stage.
        bpy.ops.wm.save_as_mainfile(filepath=str(out), check_existing=False)
        print(json.dumps(result))
        return
    source = Path(bpy.data.filepath)
    if not source.is_file():
        raise PipelineError('check/capture requires an explicitly loaded checkpoint')
    checksum = sha256_file(source)
    if args.action == 'check':
        result = recipe_tool.check(recipe, args.stage)
        result.update(blend=str(source.resolve()), blend_sha256=checksum)
        write_new(out, result)
        if result['status'] != 'pass':
            raise PipelineError(str(result['failures']))
        return
    if not args.report or not args.metadata:
        raise PipelineError('capture needs --report and --metadata')
    report = json.loads(Path(args.report).read_text())
    if (report.get('status') != 'pass' or report.get('blend_sha256') != checksum
            or report.get('recipe_digest') != recipe_tool.digest(recipe)):
        raise PipelineError('capture needs passing check for this recipe/checkpoint')
    from capture_review import capture_fixed, world_bounds
    from mathutils import Matrix, Vector
    baked = report['stage'] != 'master'
    objects = [bpy.data.objects[n] for n in recipe_tool.part_names(recipe, baked)]
    low, high = world_bounds(objects)
    center, size = (low + high) / 2, max(high - low)
    location = center + Vector((1, -1, .8)).normalized() * max(1, size * 3)
    rotation = (center - location).to_track_quat('-Z', 'Y')
    matrix = Matrix.Translation(location) @ rotation.to_matrix().to_4x4()
    capture_fixed(out, args.metadata, checkpoint=source, view='three_quarter',
                  resolution=[800, 700], camera_spec=dict(matrix_world=[list(r) for r in matrix],
                  type='ORTHO', lens=50, ortho_scale=size * 1.4))


if __name__ == '__main__':
    main()
