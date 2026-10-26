# Reusable adapter development — completed, 2026-10-26

**Technical two-box fixture passed build → evaluated copies → UV pack → CPU bake
→ reopen verification.** This is tool-development evidence, not the frozen
DeepSeek A/repeat-A/B benchmark, UI editability acceptance or controller likeness.

## Implemented

New files under `tools/asset-pipeline/`:

- `pipeline/primitive_recipe.py`: strict data-only box recipe, optional live bevel,
  fixed Object-coordinate procedural material, independently selectable parts and
  root controls, evaluated bake-copy preparation, generic scoped check and
  data-only presets for the existing runner.
- `scripts/primitive_recipe.py`: `plan/build/prepare/check/capture` interface.
- `examples/primitive-recipe.fixture.json`: two separate calibration coupons,
  one rotated; not a stool/controller model or an attachment test.
- `fixtures/test_primitive_recipe.py`: eight pure tests.
- `fixtures/verify_primitive_recipe_blender.py`: reopened source/corner/map fixture.

Existing runner, UV, baking, health and capture implementations were reused without
source changes. No dependencies, permissions, environment or service changes.

## Selected saved checkpoints

Paths relative to `.dev-shots/reusable-pipeline-test-01/`:

| Checkpoint | SHA-256 |
| --- | --- |
| `adapter-fixture-02/master.blend` | `b425d7f41fa820a3252abc13d8bf98d208f535709a46a15d6a1ec1a33eeb8f48` |
| `adapter-fixture-02/prepared.blend` | `989c2d7513695cca5b6006a4c6a685a59a046eef87d717ef9a86e7b7901090ae` |
| `adapter-atlas-01/uv.blend` | `6ef8cf06f9ce71336c396ab5ca3ebaf0d9551492e435ad122affdf1894194c23` |
| `adapter-atlas-01/baked.blend` | `6b2820e8a6bdbd2ca9e7d543e1483dcd269d2583390d0634c6a45771c0121ba0` |

Master has two independent parts with live bevels (188 evaluated triangles each,
376 total), centre origins and one assembly root. Prepared/baked files also retain
these source objects hidden viewport/render, not selection-locked; separate
`Bake__*` parts have single-user meshes and no modifiers. Reveal originals in the
Outliner if editing the retained master; don't display source and copies together.

## Verification and inspected evidence

- `adapter-fixture-02/session.json`: 8/12 runner operations, no failed operations;
  recorded stage-time sum 12.404 s. Master and prepared reopened checks pass.
  Parent inspected `master.png` and `prepared.png`: shape/position retained.
- `adapter-atlas-01/session.json`: 8/12 operations, no failed operations; stage-time
  sum 13.159 s. Reopened UV and baked checks pass. Twelve UV charts, 376 triangles,
  zero reported global overlap pairs or UV degenerates; ~50.21% coverage and
  ~12 px conservative chart-box gap at 256. Bake dilation4 px.
- `adapter-verify-01/reopen.json`: separate owned process opened UV and baked
  checkpoints, compared **exact indexed mesh/corner UVs and retained source state**,
  decoded all five 256-square PNGs and checked actual assigned shader image paths/
  colour-space tags. Input bytes unchanged, no saves during verification.
- Maps: base colour, roughness, metallic, tangent normal and ORM under
  `adapter-atlas-01/bake/textures/`. Metallic is correctly constant0; normal is
  near-flat with small bump variation (observed R/G range roughly .49–.506).
- Parent inspected the base-colour and normal maps and these selected material
  captures from `adapter-appearance-review-01/`:
  `source/renders/uv_three_quarter_material.png` and
  `baked/renders/baked_three_quarter_material.png`.
  Checker placement/colours broadly transfer; baked boundaries visibly soften/
  alias at this deliberately low resolution. Not final texture-quality acceptance.
  Capture manifests identify saved sources; neither capture saved a checkpoint.
- Neutral master/prepared captures use identical evaluated framing, but actual
  visibility inventories differ intentionally. No standard matched-sheet pass was
  claimed or fabricated. The two material captures use the same existing render
  helper/target names/direction/resolution; quantitative shader error is unmeasured.
- Parent re-hashed all declared outputs from the two failed initial runs and four
  selected successful run manifests: no mismatches. Map hashes/finite decoded pixel
  ranges are in `adapter-verify-01/reopen.json`.
- Portable regressions: new recipe8 + existing pipeline12 + atlas-mode jobs2 +
  review-runner16 = **38 passing tests**. `git diff --check` no errors (Windows
  line-ending warning only). No live Blender/MCP access at any stage.

Stage-time sums are subprocess/runner time, not total development/agent time.
Diagnostic/render-only manifests use temporary native `construct` stages to invoke
existing helpers and do not contain full before/after acceptance ledgers; their
`evidence_complete:false` is not a hidden benchmark pass. Geometry and atlas plans
do contain complete saved/check/capture evidence.

## Failures retained and fixes tested

1. `adapter-fixture-01`: first master passed, prepare exited1 before save. Rotation
   matrix assignment changed float32 bits by `1.49e-8`; vertices/faces matched.
   `copy-diagnostic.json` proved copying object transform channels instead yields
   exact matrices and geometry. Exact copy assertion was retained, not loosened.
2. `adapter-recovery-01`: prepare then stopped because generic material fingerprint
   included `users` (2→4 after copying). `preservation-diagnostic.json` found only
   material-reference metadata changes; geometry/transforms/modifiers matched.
   Fixed-recipe content fingerprints now exclude **only** `users/use_fake_user`,
   preserving exact graph/settings and assignments. Pure tests ensure roughness
   and graph changes are still detected. Changed fingerprint schema required a new
   fixture master; old sources/results remain untouched.
3. First diagnostic-plan initialization rejected an empty governing-view list
   before any Blender process. Corrected before its first native run.

These were tool-development repairs with parent intervention. This run **must not
be counted as a no-rescue agent-operated success**.

## Operator/ownership record and limits

User authorized parent-direct implementation after modeller source-edit denial.
DeepSeek Free independently reviewed the initial code (session
`ses_e879dc44bffeBkd4lnQ30WNUxR`), found no fixture blocker and proposed bounded
robustness/material checks; parent addressed them. Reviewer reported 13 reads
against an eight-call brief. Later execution request hit the provider Free usage
limit before any new work. Parent inspected partial state and performed direct
verification; no silent model substitution. **Post-review fixes/preset generator
and final verification code have parent review/tests, not a fresh independent
DeepSeek review at that time.** Subsequently the user requested Abliterated, which
successfully reviewed the final source: [final-code-review.md](final-code-review.md).
No blocker for a fixed-revision parameter-only trial; scoped material-slot,
dependency-identity and independent-verifier limits are recorded there.

All owned Blender processes exited; no timeout or interactive signals. Parent and
workers STOPPED. Interactive filepath/dirty state unknown/untouched. Original
controller/barrel work and existing tools/checkpoints preserved.

Unverified: UI interaction/responsiveness and dependency-motion tests, repeated A,
variant B, general complex shapes, high-to-low transfer, quantitative shader error,
lower-mip safety, engine portability and user appearance acceptance. Existing bake
image dependencies were found in this workspace; no self-contained packaging claim.

## Recorded final source identities

SHA-256; selected sources, not an exhaustive dependency lock:

```text
pipeline/primitive_recipe.py               991d5f623611a0e0fdc6bf4162e8e00c6567489f5723c7e9d6c13e31b9331399
scripts/primitive_recipe.py                4018b88455cbd1ec067cc4eaa75194fc5cf54d5b7c161113653a861bef8feb0e
fixtures/test_primitive_recipe.py          b271d50f81354e89f511e7f0ebc03ee557e99ca5ff0e808428ec915d486ac0a4
fixtures/verify_primitive_recipe_blender.py 01b8a47e1766e2d677bf730a904371ec6c092ee80743f9bdf6a85cdaa4a75013
examples/primitive-recipe.fixture.json     ee93a53c2cee71ed596f16e4551d1872a1cd2d261c5a468718cd0ab075e6a9cf
```

Next gate: agree the parameter-only A/repeat-A/B benchmark and actual editability
checks before claiming an agent trial. Abliterated responded successfully to the
subsequent final static review; runtime/model-operation success is not inferred.
No automatic new asset, provider switch, controller progression or export.
