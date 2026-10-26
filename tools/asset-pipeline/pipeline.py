"""Single entry point for asset preparation.

    python3 tools/asset-pipeline/pipeline.py <verb> --job jobs/<name>.job.json

Verbs: inspect, uv, bake, check, render, export, verify.
Jobs are JSON; the code path is shared, so an asset variant is data, not a new script.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline.common import (  # noqa: E402
    PipelineError,
    blender_objects,
    load_job,
    mesh_objects,
    names,
    new_path,
    prepared_out_dir,
    sha256_file,
    stamped,
    world_bounds,
    write_json,
)


def report_path(args, out_dir, default):
    return Path(args.report) if args.report else out_dir / default


def verb_inspect(job, args):
    import bpy

    roots = blender_objects(names(job))
    exclude = job.get("exclude", [])
    objects = mesh_objects(roots, exclude)
    out_dir = prepared_out_dir(job)
    report = stamped({
        "verb": "inspect",
        "source": bpy.data.filepath,
        "source_sha256": sha256_file(bpy.data.filepath) if bpy.data.filepath else None,
        "objects": [obj.name for obj in objects],
        "bounds": world_bounds(objects),
        "uv_layers": {obj.name: [layer.name for layer in obj.data.uv_layers] for obj in objects},
        "materials": sorted({slot.material.name for obj in objects
                             for slot in obj.material_slots if slot.material}),
    })
    write_json(report_path(args, out_dir, "inspect.json"), report)
    print("PIPELINE", json.dumps({"verb": "inspect", "objects": len(objects)}))
    return 0


def verb_uv(job, args):
    """Unwrap optionally, then legacy shrink or opt-in shared-sheet packing.

    Packing is deliberately not used: ``bpy.ops.uv.pack_islands`` reported FINISHED
    while creating overlapping islands. ``gaps`` (default on with ``unwrap``)
    applies per-island shrink and measures the real result unless `pack` is true.
    Legacy shrink can plateau
    below the requested gap; `ok` does not enforce minimum spacing or global
    shared-atlas disjointness. `pack:true` uses packing.py and global chart-box
    gap, triangle-overlap and degeneracy gates; it never shrinks in place.
    """
    import bpy
    from pipeline import uv as uv_module

    roots = blender_objects(names(job))
    objects = mesh_objects(roots, job.get("exclude", []))
    out_dir = prepared_out_dir(job)
    layer = job.get("uv_layer", "AtlasUV")
    margin = float(job.get("unwrap_margin", 0.02))
    gap_margin = float(job.get("gap_margin", min(margin, 0.008)))
    resolution = int(job.get("overlap_resolution", 2048))
    unwrap = bool(job.get("unwrap"))
    apply_gaps = bool(job.get("gaps", unwrap))
    shared = bool(job.get('pack'))

    gaps = []
    if unwrap:
        for obj in objects:
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            if obj.data.uv_layers.get(layer) is None:
                obj.data.uv_layers.new(name=layer)
            obj.data.uv_layers.active = obj.data.uv_layers[layer]
            obj.data.uv_layers[layer].active_render = True
            uv_module.smart_unwrap(obj, margin=margin)
    packing = None
    if shared:
        from pipeline import atlas_layout
        packing = atlas_layout.repack(objects, layer, gap_margin)
    elif apply_gaps:
        for obj in objects:
            if obj.data.uv_layers.get(layer) is None:
                continue
            gaps.append(uv_module.ensure_island_gaps(obj, layer, margin=gap_margin))

    bounds = uv_module.uv_report(objects, layer)
    overlaps = uv_module.island_overlap_report(objects, layer, resolution=resolution)
    spacing = uv_module.min_island_gap(objects, layer, step_uv=max(gap_margin / 4.0, 0.0005))

    limit = job.get("max_overlap_fraction")
    require_disjoint = bool(job.get("require_disjoint", False))
    failures = []
    global_layout = None
    if shared:
        global_layout = atlas_layout.validate(objects, layer, resolution,
                                             float(job.get('min_gap_px', gap_margin * resolution)))
        failures.extend(global_layout['failures'])
    if bounds["out_of_bounds"]:
        failures.append("uv_out_of_bounds")
    if overlaps["truncated"]:
        failures.append("overlap_report_truncated")
    if require_disjoint and overlaps["total_pairs"] > 0:
        failures.append("overlaps_present")
    if limit is not None and overlaps["total_px2"] > float(limit) * resolution * resolution:
        failures.append("overlap_fraction_over_limit")

    checkpoint = None
    if shared and not failures and job.get('blend'):
        checkpoint = new_path(out_dir, job['blend'])
        bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

    report = stamped({
        "verb": "uv",
        "configuration": {"layer": layer, "unwrap": unwrap, "unwrap_margin": margin,
                          "gaps": apply_gaps, "gap_margin": gap_margin,
                          "overlap_resolution": resolution,
                          "require_disjoint": require_disjoint,
                          "max_overlap_fraction": limit},
        "report": bounds,
        "gaps": gaps,
        "packing": packing,
        "global_layout": global_layout,
        "blend": str(checkpoint) if checkpoint else None,
        "overlaps": overlaps,
        "spacing": spacing,
        "failures": failures,
        "ok": not failures,
    })
    write_json(report_path(args, out_dir, "uv.json"), report)
    print("PIPELINE", json.dumps({"verb": "uv", "ok": report["ok"],
                                  "overlap_pairs": overlaps["total_pairs"],
                                  "truncated": overlaps["truncated"],
                                  "min_gap_uv": spacing["min_gap_uv"],
                                  "failures": failures}))
    return 0 if report["ok"] else 1


def verb_bake(job, args):
    import bpy
    from pipeline import bake as bake_module, export as export_module

    roots = blender_objects(names(job))
    objects = mesh_objects(roots, job.get("exclude", []))
    source_path = bpy.data.filepath
    from pipeline.common import resolve_path
    output = resolve_path(job['out_dir'])
    if output.exists():
        raise PipelineError(f'Refusing to reuse bake output directory: {output}')
    out_dir = prepared_out_dir(job)
    resolution = int(job.get("resolution", 2048))
    preserve = bool(job.get('preserve_layout'))
    if preserve and job.get('export'):
        raise PipelineError('preserve_layout is review-only; export separately')
    bake_function = bake_module.bake_preserved_atlas if preserve else bake_module.bake_atlas
    options = {'uv_layer': job.get('uv_layer', 'AtlasUV')} if preserve else {
        'alpha': bool(job.get('alpha', True)),
        'unwrap_margin': float(job.get('unwrap_margin', 0.02))}
    atlas, report = bake_function(
        objects, out_dir,
        resolution=resolution,
        margin=int(job.get("margin", 8)),
        samples=int(job.get("samples", 8)),
        **options,
    )
    blend_path = new_path(out_dir, job.get("blend", "atlas_source_001.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    # Baking produces a review candidate, never an implicit delivery export.
    glb_path = None
    export_report = None
    audit = None
    if job.get('export'):
        glb_path = new_path(out_dir, job['export'])
        export_report = export_module.export_glb(
            blender_objects(report['assembly_roots'] or report['parts']), glb_path,
            gate=job.get('gate'), tangents=bool(job.get('tangents')))
        audit = export_module.audit_glb(glb_path)

    payload = stamped({
        "verb": "bake",
        "source": source_path,
        "atlas": report,
        "export": export_report,
        "audit": audit,
        "blend": str(blend_path),
    })
    payload["ok"] = audit['ok'] if audit is not None else None
    payload['status'] = 'review_candidate' if audit is None else 'structural_check_only'
    write_json(report_path(args, out_dir, "bake-report.json"), payload)
    print("PIPELINE", json.dumps({"verb": "bake", "ok": payload["ok"],
                                  "glb": str(glb_path), "channels": sorted(report["channels"])}))
    return 0 if audit is None or payload["ok"] else 1


def verb_check(job, args):
    from pipeline import check as check_module
    report = stamped({"verb": "check", **check_module.check(job)})
    out_dir = prepared_out_dir(job) if job.get("out_dir") else Path(".")
    write_json(report_path(args, out_dir, "check.json"), report)
    print("PIPELINE", json.dumps({"verb": "check", "ok": report["ok"]}))
    return 0 if report["ok"] else 1


def verb_hybrid(job, args):
    import bpy
    from pipeline.hybrid import bake_hybrid
    from pipeline.common import resolve_path
    source = bpy.data.filepath
    output = resolve_path(job['out_dir'])
    if output.exists():
        raise PipelineError(f'Refusing to reuse hybrid output directory: {output}')
    objects = mesh_objects(blender_objects(names(job)), job.get('exclude', []))
    root, reports = bake_hybrid(objects, job, prepared_out_dir(job))
    checkpoint = new_path(output, job.get('blend', 'hybrid_review.blend'))
    bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))
    write_json(output / 'hybrid-report.json', stamped({
        'status': 'review_candidate', 'source': source, 'blend': str(checkpoint),
        'root': root.name, 'groups': reports,
        'limits': ['No export or acceptance implied', 'Normals remain baked; repeated base colour and roughness preserve source sampling']}))
    print('PIPELINE', json.dumps({'verb': 'hybrid', 'status': 'review_candidate', 'blend': str(checkpoint)}))
    return 0


def verb_render(job, args):
    from pipeline import render as render_module
    roots = blender_objects(names(job))
    objects = mesh_objects(roots, job.get("exclude", []))
    out_dir = prepared_out_dir(job)
    result = render_module.capture(job, objects, out_dir / job.get('subdir', 'renders'))
    payload = stamped({"verb": "render", "views": result["views"]})
    write_json(report_path(args, out_dir, "render.json"), payload)
    print("PIPELINE", json.dumps({"verb": "render", "views": len(result["views"])}))
    return 0


def verb_export(job, args):
    from pipeline import export as export_module
    roots = blender_objects(names(job))
    objects = mesh_objects(roots, job.get("exclude", []))
    out_dir = prepared_out_dir(job)
    glb_path = new_path(out_dir, job.get("export", "export_001.glb"))
    result = export_module.export_glb(objects, glb_path, gate=job.get('gate'),
                                      tangents=bool(job.get('tangents')))
    audit = export_module.audit_glb(glb_path)
    payload = stamped({"verb": "export", "export": result, "audit": audit})
    payload["ok"] = audit["ok"]
    write_json(report_path(args, out_dir, "export-report.json"), payload)
    print("PIPELINE", json.dumps({"verb": "export", "ok": payload["ok"], "glb": str(glb_path)}))
    return 0 if payload["ok"] else 1


def verb_verify(job, args):
    from pipeline import verify as verify_module
    out_dir = prepared_out_dir(job) if job.get("out_dir") else Path(".")
    result = stamped({"verb": "verify", **verify_module.verify(job["glb"])})
    write_json(report_path(args, out_dir, "verify.json"), result)
    print("PIPELINE", json.dumps({"verb": "verify", "ok": result["ok"]}))
    return 0 if result["ok"] else 1


VERBS = {
    "inspect": verb_inspect,
    "uv": verb_uv,
    "bake": verb_bake,
    "check": verb_check,
    "render": verb_render,
    "export": verb_export,
    "verify": verb_verify,
    "hybrid": verb_hybrid,
}


def find_blender():
    """Locate a Blender install that is not on PATH.

    Portability fallback only: `--blender` and a PATH lookup win. Kept because
    Blender on Windows/macOS installs outside PATH by default.
    """
    import os
    candidates = [Path('/Applications/Blender.app/Contents/MacOS/Blender')]
    for variable in ('PROGRAMFILES', 'PROGRAMW6432'):
        root = os.environ.get(variable)
        if not root:
            continue
        foundation = Path(root) / 'Blender Foundation'
        if foundation.is_dir():
            candidates.extend(sorted(foundation.glob('Blender */blender.exe'), reverse=True))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def main(argv=None):
    if argv is None:
        argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("verb", choices=sorted(VERBS))
    parser.add_argument("--job", help="job JSON describing the operation")
    parser.add_argument("--glb", help="GLB for the verify verb")
    parser.add_argument("--report", help="override the report path")
    parser.add_argument('--blender', help='Blender executable for ordinary Python invocation')
    parser.add_argument('--dry-run', action='store_true', help='Validate only; no files or Blender process')
    args = parser.parse_args(argv)
    try:
        if args.glb:
            job = {"glb": args.glb}
        elif args.job:
            job = load_job(args.job)
        else:
            raise PipelineError("--job is required")
        if args.verb == 'verify':
            job.setdefault('out_dir', '.')
        from pipeline.job import validate
        validate(job, args.verb)
        if args.dry_run:
            print('PIPELINE_VALID', json.dumps({'verb': args.verb, 'job': args.job}))
            return 0
        import importlib.util
        if importlib.util.find_spec('bpy') is None:
            import shutil
            import subprocess
            from pipeline.common import resolve_path
            executable = args.blender or shutil.which('blender') or find_blender()
            if executable is None:
                raise PipelineError('Blender not found; pass --blender')
            command = [executable, '--background']
            if job.get('source'):
                source = resolve_path(job['source'])
                if not source.is_file():
                    raise PipelineError(f'Missing source: {source}')
                command.append(str(source))
            elif args.verb == 'verify':
                command.append('--factory-startup')
            else:
                raise PipelineError('Job source is required when running outside Blender')
            command.extend(['--python-exit-code', '1', '--python', str(Path(__file__).resolve()), '--', *argv])
            return subprocess.run(command, check=False).returncode
        if args.verb == "verify":
            if not job.get("glb"):
                raise PipelineError("verify needs --glb")
            job.setdefault("out_dir", ".")
        return VERBS[args.verb](job, args)
    except PipelineError as exc:
        print(f"PIPELINE_ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
