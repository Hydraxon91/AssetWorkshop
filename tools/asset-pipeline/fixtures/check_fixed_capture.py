"""Disposable saved-scene regression for shared fixed capture. No source save.

Run on trial02 before.blend, or another explicit saved scene with Trial_Panel.
Output directories are new names; injected failure tests restore temporary state.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from capture_review import StateSnapshot, capture_fixed


def state():
    snapshot = StateSnapshot()
    return dict(engine=snapshot.engine, camera=snapshot.camera.name if snapshot.camera else None,
                frame=snapshot.frame, resolution=snapshot.resolution, image=snapshot.image,
                filepath=snapshot.filepath, film=snapshot.film_transparent, aa=snapshot.render_aa,
                shading=snapshot.shading, view=snapshot.view, selected=snapshot.selected,
                active=snapshot.active.name if snapshot.active else None,
                object_names=sorted(o.name for o in bpy.data.objects),
                camera_data=sorted(c.name for c in bpy.data.cameras),
                matrices={o.name:[list(row) for row in o.matrix_world] for o in bpy.data.objects})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not bpy.app.background:
        raise RuntimeError('owned disposable process only')
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    checkpoint = Path(bpy.data.filepath)
    checksum = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    obj = bpy.data.objects['Trial_Panel']
    corners = [obj.matrix_world @ v.co for v in obj.data.vertices]
    low = Vector(min(v[i] for v in corners) for i in range(3))
    high = Vector(max(v[i] for v in corners) for i in range(3))
    center = (low+high)/2
    location = center+Vector((1,-1,0.65)).normalized()*3
    rotation = (center-location).to_track_quat('-Z','Y')
    matrix = Matrix.Translation(location)@rotation.to_matrix().to_4x4()
    spec = dict(matrix_world=[list(row) for row in matrix], type='ORTHO', lens=50,
                ortho_scale=max(high-low)*1.25)
    before = state()
    capture_fixed(out/'explicit.png', out/'explicit.json', checkpoint=checkpoint,
                  view='three_quarter', resolution=[900,800], camera_spec=spec)
    assert state() == before, 'explicit camera capture did not restore scene'
    # Existing camera branch must not alter that camera or leak temporary data.
    data = bpy.data.cameras.new('FixtureExistingCamera')
    camera = bpy.data.objects.new('FixtureExistingCamera',data)
    bpy.context.scene.collection.objects.link(camera)
    camera.matrix_world = matrix
    data.type, data.ortho_scale = 'ORTHO', spec['ortho_scale']
    bpy.context.view_layer.update()
    named_before = state()
    capture_fixed(out/'named.png',out/'named.json', checkpoint=checkpoint, view='three_quarter',
                  resolution=[900,800],camera=camera,
                  workbench={'color_type':'MATERIAL','curvature_ridge_factor':1.5},
                  color_management={'view_transform':'Standard','look':'None'},render_aa='8')
    assert state() == named_before, 'existing camera/style did not restore'
    try:
        def fail():
            raise RuntimeError('injected render failure')
        capture_fixed(out/'failure.png',out/'failure.json',checkpoint=checkpoint,
                      view='three_quarter',resolution=[900,800],camera_spec=spec,renderer=fail)
    except RuntimeError as exc:
        assert str(exc) == 'injected render failure'
    else:
        raise AssertionError('failure swallowed')
    assert state() == named_before, 'exception did not restore'
    assert not (out/'failure.json').exists()
    try:
        capture_fixed(out/'explicit.png',out/'collision.json',checkpoint=checkpoint,
                      view='three_quarter',resolution=[900,800],camera_spec=spec)
    except FileExistsError:
        pass
    else:
        raise AssertionError('overwrote prior capture')
    assert state() == named_before
    bpy.data.objects.remove(camera,do_unlink=True)
    bpy.data.cameras.remove(data)
    bpy.context.view_layer.update()
    assert state() == before
    assert hashlib.sha256(checkpoint.read_bytes()).hexdigest() == checksum
    report = dict(status='pass', checks=['explicit_camera_restore','existing_camera_unchanged',
                                       'custom_shading_restore','exception_restore','no_overwrite',
                                       'temporary_data_cleanup','source_bytes_unchanged'],
                  source=str(checkpoint),source_sha256=checksum)
    (out/'result.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))


if __name__ == '__main__':
    main()
