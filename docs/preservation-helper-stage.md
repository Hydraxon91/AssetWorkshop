# Preservation and cost helpers — implementation stage

## Approved scope

User approved the first post-research helper stage: audit existing helpers,
implement task-aware preservation and geometry/material cost reporting, and test
positive and deliberately failing disposable fixtures. No asset optimization,
source saves, new downloads, ComfyUI, Verdant installation/code copying, destination
integration or approval-policy changes are included.

## Audit and design boundary

- `scripts/asset_fingerprint.py` is a rounded, combined fingerprint used by review
  and approval gates. It does not hash image byte contents and cannot explain
  which field changed. Its established semantics must remain unchanged.
- `pipeline/check.py:assembly_preservation` compares evaluated point sets with
  vertex counts and a distance threshold. It expressly does not establish vertex
  identities or topology, nor task-specific UV/material preservation.
- `scripts/audit_asset.py` and the existing texture inventory already report
  material slots, image dependencies and advisory projected density. The new cost
  report is a scoped accounting companion, not a replacement GPU-performance or
  texture-density measurement.
- The existing texture inventory does not recurse through node groups or hash
  packed image content. New snapshots must distinguish unsupported dependencies
  from verified preservation, not silently pass them.
- New helpers are separate snapshot/comparison APIs. No change to existing approval
  fingerprints, exporter gates, mesh-health thresholds or default pipeline behavior.
  Native exact equality is not correspondence-aware export equivalence or visual
  acceptance.

## Verification plan

1. Ordinary-Python policy tests: allowed material-only/UV-only changes; canopy-only
   ratio; protected-part and object-set failures; malformed inputs fail closed.
2. Disposable Blender fixtures: real mesh/UV/material/image/transform mutations,
   shared mesh costs, evaluated instances/modifiers and unrelated-data exclusion.
3. Parent independent review and additional negative probes, then reuse the three
   already acquired teapot/roof/tree source-output pairs as read-only acceptance
   examples. Keep third-party payloads ignored under `.dev-shots/`, not bundled in
   the portable synthetic test suite.
4. Re-run existing pipeline regressions and document exact coverage/limitations.

Baseline before implementation: `python3 tools/asset-pipeline/fixtures/test_pipeline.py`
passed **12 tests**. All project paths were untracked in Git at the scoped status
check; existing work is preserved and no commit/reset is authorized. Live Blender
ownership is not acquired; fixture/acceptance execution uses isolated factory-startup
processes with autoexec disabled, never the live scene.

## Status

Completed and independently reviewed. Added `pipeline/preservation.py`,
`pipeline/inspection.py`, `scripts/inspect_preservation.py`,
`fixtures/test_preservation.py`, and `fixtures/check_preservation.py` under
`tools/asset-pipeline/`. CLI examples and policy semantics are in its README.

Verification results:
- Final selected pure regressions: **48 passed** (34 fixture tests plus 14
  phase-1 document/density tests). Five protected approval/audit/pipeline source
  hashes match their pre-implementation baseline.
- 12 new pure-Python tests, including negative mutations, malformed policies,
  unsupported fields, output collisions and session-ID independence.
- Parent independently ran the Blender synthetic fixture successfully: shared
  meshes 8 unique versus 12 authored per-object triangles; evaluated vertex
  instances raise the scoped total to 28 triangles. Tiny coordinate, topology,
  UV, transform, shader, slot and packed-image mutations are detected. Unrelated
  state checks pass. Collection/nested ownership is not certified.
- Parent read-only real-pair checks pass for teapot, roof and tree under explicit
  scoped policies; each also rejects an injected protected-geometry mismatch.
  All six source/output files retained their byte hashes. Roof shader equality
  is outside this acceptance subset; roof images/geometry/transforms and non-roof
  UVs are protected. Canopy face-material assignments are permitted to change with
  topology; Trunk protects all fields. No visual acceptance is implied.
- Evidence: `.dev-shots/helper-stage-01/acceptance-03/summary.json`, with snapshots,
  policies and positive/negative reports alongside it. Earlier acceptance-01/02
  failures remain preserved, not rewritten as successes.

Parent review caught and corrected image animation-property compatibility and
runtime `session_uid` pollution of shader hashes. Fixture correction replaced an
invalid mesh collection-instancing setup with actual vertex instancing. None of
these changes modify the old approval hash. A broad ordinary-Python discovery run
also hit an existing Blender-only test (`bpy` unavailable); run pure and Blender
test entrypoints separately, not all `test_*.py` under ordinary Python.

Limits: exact representation, not reordered-export equivalence; authored base
geometry, not modifiers/animation/shape-key preservation; conservative unsupported
material dependencies; immediate instance ownership and viewport-only evaluated
cost. No GPU performance claim or production polygon target. ComfyUI availability
was reported by the user during this stage; it was not contacted or used.

All workers/processes stopped. No source asset saves or live Blender access.
