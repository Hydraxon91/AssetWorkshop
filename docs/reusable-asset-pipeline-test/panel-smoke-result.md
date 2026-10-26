# Fixed-panel smoke — completed, 2026-10-26

> Historical operator note: the worker below is not the current approved operator. See
> repository `docs/operators.md`.

**PASS for the bounded execution-plumbing test.** Not user asset acceptance,
parameter-selection validation or an end-to-end UV/bake benchmark.

## Scope and result

- User approved the unchanged `review_worker.py --fixture-panel` preset.
- Worker: `opencode/deepseek-v4.1-flash-free`, session
  `ses_e882f5bacffelGmKNGqqMVWfbX`, now STOPPED. No new builder/wrapper code.
- Manifest: `.dev-shots/reusable-pipeline-test-01/panel-smoke-01/session.json`.
- Nine stages completed within twelve-operation budget; construction at operations
  1 and 5, final save/check/capture/sheet at 6–9. Eight owned Blender processes exit0;
  sheet is a non-process runner operation. No failed operation or rescue.
- Parent read the manifest, both saved-check reports and both capture metadata
  files, independently re-hashed all eleven declared operation outputs (all match),
  and inspected both PNGs. Camera, shading, resolution and visibility metadata
  match exactly; only checkpoint hash differs.
- Visible result: sharp panel becomes a rounded-edge panel in matched neutral
  three-quarter views. Faceted bevel strips are visible; appropriate to this fixed
  fixture, not an unplanned surface-polish task.
- Both reports pass closed single-component base/evaluated health. Authored
  signature, transforms and bounds match. Base remains 8 vertices/12 triangles;
  after evaluated result is 96 vertices/188 triangles with one unapplied bevel.
- Saved checkpoint correspondence is supported by runner reopen/check/capture
  stages and parent artifact/metadata review; parent did not launch another Blender
  inspection process. Object Mode interaction/responsiveness was not tested.

## Saved evidence

All paths below relative to `.dev-shots/reusable-pipeline-test-01/panel-smoke-01/`:

| File | SHA-256 / purpose |
| --- | --- |
| `before.blend` | `950e89cb650d2c6cf21b7d669748bb7055f00a78f6871d782653841f3a3c1b9e` |
| `after.blend` | `3383f08994bc6179e6e2552d0a4cde9792a60970cfa131512b4187fcac42f28f` |
| `before_check.json`, `after_check.json` | Passing scoped fixture checks linked to those saved bytes |
| `before.png`, `after.png` | Parent-inspected matched 900×800 Workbench views |
| `before_capture.json`, `after_capture.json` | Actual camera, shading, visibility and checkpoint metadata |
| `comparison.html` | Local before/after sheet |

## Budget/process finding

The worker invoked the ready preset rather than writing implementation scripts.
First construction was runner operation1. Worker reports a midpoint status after
operation4 resuming at `after_build`; no baseline rerun appears in the manifest.
Sum of runner-recorded stage durations: **12.694 seconds**, not total conversation
or agent wall time. Model turns, token cost and full elapsed agent time were not
independently measured. No conclusion about broad model reliability follows.

## Not tested / next gate

Parameter-driven variants, multi-part editable assemblies, UI editability,
UV unwrap/packing, materials, baking, mip behavior and exports are untested here.
No source/tool/permission edits, dependencies, live MCP or unrelated asset changes.
Interactive filepath/dirty state remains unknown/untouched. Worker has stopped;
runner records all its Blender children exited normally.

Next proposed scope: approve the bounded reusable parameter/preparation/report
adapter development identified in `tooling-audit.md`, and agree the small assembly
benchmark. No automatic controller continuation or adapter implementation authorized.
