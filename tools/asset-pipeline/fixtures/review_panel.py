"""One standard cube + one unapplied bevel, only in a disposable trial process."""
import argparse
from pathlib import Path
import sys
import bpy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('role', choices=['before', 'after'])
    parser.add_argument('--out', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not bpy.app.background:
        raise RuntimeError('background only')
    out = Path(args.out)
    if out.exists():
        raise FileExistsError(out)
    if args.role == 'before':
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.object
        obj.name = 'Trial_Panel'
        obj.scale = (1.2, 0.12, 0.8)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obj.location = (0.25, -0.15, 0.45)
    else:
        obj = bpy.data.objects['Trial_Panel']
        if obj.modifiers:
            raise RuntimeError('expected unmodified before source')
        modifier = obj.modifiers.new('Trial_Bevel', 'BEVEL')
        modifier.width, modifier.segments, modifier.limit_method = 0.03, 3, 'ANGLE'
    bpy.context.view_layer.update()
    out.parent.mkdir(parents=True, exist_ok=True)
    # Working snapshot to cross the disposable process boundary; final checkpoint
    # save, checks and capture remain separate runner stages.
    bpy.ops.wm.save_as_mainfile(filepath=str(out), check_existing=False)


if __name__ == '__main__':
    main()
