# Primitive-recipe adapter — technical fixture validated

The user explicitly authorized parent-direct implementation after worker write
permissions denied tool sources. DeepSeek reviewed the initial source independently;
later parent fixes and tests are disclosed in [adapter-result.md](adapter-result.md).
No agent permissions or existing tools changed.

## Interface

- `pipeline/primitive_recipe.py`: strict version1 data validation, built-in boxes
  with independently selectable meshes, a transformable assembly root, optional
  live bevel, fixed Object-coordinate checker/roughness/noise-bump material.
- `scripts/primitive_recipe.py`: plain-Python data-only `plan`, plus background-only
  `build`, `prepare`, `check`, `capture`. Every action takes `--recipe` and new `--out`. Loaded-checkpoint
  actions use the runner's source field; the CLI does not launch processes.
- `examples/primitive-recipe.fixture.json`: two separate calibration coupons,
  not a joined assembly, stool recipe or controller model. Metres, Z up. Grounded
  parts have centre origins; rotations are XYZ degrees. Max16 boxes, dimensions
  .001..10m, bevel at most quarter of smallest dimension, 1..4 segments.

Command arguments for `review_worker.py` generic stages (not new runner commands):

```text
build --recipe RECIPE --out NEW_WORK.blend --empty-startup
prepare --recipe RECIPE --out NEW_PREP_WORK.blend
check --recipe RECIPE --stage master|prepared|uv|baked --out NEW_REPORT.json
capture --recipe RECIPE --report REPORT.json --out NEW.png --metadata NEW.json
```

Generate a ready preset in ordinary Python, without launching Blender:

```powershell
python tools/asset-pipeline/scripts/primitive_recipe.py plan --recipe tools/asset-pipeline/examples/primitive-recipe.fixture.json --out .dev-shots/NEW_GEOMETRY/plan.json --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python tools/asset-pipeline/scripts/review_worker.py init --plan .dev-shots/NEW_GEOMETRY/plan.json --manifest .dev-shots/NEW_GEOMETRY/session.json
```

Invoke each returned next stage individually using `review_worker.py run`. After
geometry is checked, generate the separate atlas fixture preset with the same
`plan` command plus `--phase appearance --source PATH_TO_PREPARED.blend` and a NEW
plan directory. It emits UV/bake jobs with explicit 256-resolution technical
settings. The generated plan declares `execution_mode: scripted-disposable`; the
runner rejects any other mode. These are fixture defaults, not a final-quality atlas
policy. Each plan has eight operations with construction-stop5/deadline12; imported
dependencies are not exhaustively locked by the runner. No fake matched sheet:
master/prepared inventories differ, so preserve their actual metadata and compare
selected views.

`build --empty-startup` explicitly resets an **unsaved background startup** only;
loaded .blend files and foreground Blender are refused. Without that option, a
nonempty startup is refused. Source validation and output-existence checks precede
native mutations. `build`/`prepare` save work snapshots, then existing
`review_blender.py save` provides the separate final-save stage. Check reports
bridge the runner's `status`/`blend_sha256` contract without changing its checks.

`prepare` retains source objects/modifiers and verifies exact authored fields plus
evaluated shape. A second root carries single-user evaluated copies at the source
world transforms, local coordinates/origins retained for Object-space material
mapping. Source visibility is intentionally changed only in the new prepared file:
sources hidden viewport/render, not selection-locked or deleted. Bake copies have
no modifiers. No shared-data editing, source modifier application or join.

Preparation deliberately rejects a master changed since recipe construction.
Live parts remain editable in Blender, but the current controlled pipeline expects
parameter changes through a rebuilt recipe; it does not silently re-authorize an
arbitrarily hand-edited master. Material preservation excludes ID reference counts
and fake-user retention flags, not shader content.

Technical lessons: assigning a rotated `matrix_world` can decompose/recompose
float32 channels; this fixture copies object channels and verifies the evaluated
result instead of loosening the exact check. Material `users/use_fake_user` are
ownership/retention metadata, not shading content; their exclusion is scoped to
this recipe fingerprint, not permission to ignore arbitrary material changes.

Then reuse existing `pipeline.py uv` on named `Bake__*` parts with `unwrap:true`,
`pack:true`, explicit gap/resolution and a saved blend. Reuse `pipeline.py bake`
with `preserve_layout:true`, `alpha:false`, `export:false`. Check after reopening
each saved candidate. Do not use default bake (it unwraps anew).

## Tests and evidence

1. Pure contract tests: `python tools/asset-pipeline/fixtures/test_primitive_recipe.py`.
2. Owned disposable source → check → prepare → check fixture and explicit UV pack/
   preserved CPU bake completed. Source/code identities and initial independent
   review limitations are recorded in `adapter-result.md`.
3. `fixtures/verify_primitive_recipe_blender.py` takes `--recipe`, `--uv`, `--baked`,
   `--textures`, `--out`; runs only in an owned background process, reopens both
   checkpoints, checks exact corner/source correspondence and 256-square map data,
   saves no source. It is a fixture, not universal texture-transfer certification.
4. Parent inspected neutral and source/baked material captures. Low-resolution
   checker edges soften/alias. A report pass alone is not final appearance approval.

No high-to-low projection or universal shader conversion. The material recipe is
deliberately fixed. Health/structural checks do not establish Object Mode UI
responsiveness, good shading, mip safety, likeness or user acceptance. Full agent
A/repeat-A/B benchmark stays separate from this tool-development fixture.
