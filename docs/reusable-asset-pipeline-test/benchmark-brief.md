# Benchmark brief — four-legged stool, A / repeat-A / B (completed, parent-executed)

Status: **COMPLETED by the parent; the named model was not invoked.** See
`results.md` for the toolchain result and the unverified agent operation. Current
approved operator: `deepseek/deepseek-flash` (see repository `docs/operators.md`).
The historical `refuseless/...abliterated` identifier appears in archived records, not
here. Parent plans/reviews; a worker, when approved, operates existing tools only.

## Capability fit, checked against the reviewed adapter

Checked against `tools/asset-pipeline/pipeline/primitive_recipe.py` (strict version1 box
recipe), not assumed:

| Proposed requirement | Adapter fact | Fit |
| --- | --- | --- |
| Seat + 4 legs = 5 parts | max 16 boxes | yes |
| 40 mm smallest dimension, 360 mm largest | dims 0.001–10 m | yes |
| Vertical legs, no rotation needed | optional XYZ rotation | yes |
| "Small bevels" | width ≤ min-dim/4 (≤0.010 m), segments 1..4 | yes, 0.002 m / 2 seg |
| Inset legs, exact underside contact | absolute part `location` | yes |
| Independent seat/leg selection | one mesh object per part | yes |
| Useful origins | box **centre** origins | yes, disclosed limit |
| One assembly control | single transformable root empty | yes, root `Stool` |
| Variant B by legs to 510 mm | dimensions are recipe parameters | yes |

**Disclosed unsupported / limited (not developed here):**

1. **Centre origins, not base/end origins.** Legs pivot about their middle, so rotating a leg
   swings about z≈205 mm rather than the foot. Useful, but not furniture-style pivots.
2. **Butt contact only.** Boxes meet the seat underside exactly (leg top z = seat bottom
   z = 0.410); there are no tenons, shoulders or joints.
3. **Seat and legs share the fixed recipe material** (Object-coordinate checker/bump). No
   per-part materials, no high-to-low projection, no shader conversion.
4. **Atlas plan defaults are 256 px technical settings**, not final texture quality; checker
   edges alias/soften at that size. Low-mip safety stays uncertified.
5. **UV unwrap/pack and bake are existing tools with fixed modes**; the worker may not author
   seams or per-asset UV code.
6. **No UI proof.** Editability is checked by data/`bpy` inspection (selection, locks, origins,
   dependence motion, evaluated retention) plus parent visual inspection. Real mouse interaction
   in a live Blender is unverified and stated as such.
7. `.blend` reopen/resave reproducibility is not claimed byte-identical; equivalence is judged
   numerically (below).

## Inputs

Recipe A (`stool-a.json`, new): version 1, root `Stool`, material `{"scale": 25, "bump": 0.0005}`.

| Part | dimensions (m) | location (m) | bevel |
| --- | --- | --- | --- |
| Seat | 0.36, 0.36, 0.04 | 0, 0, 0.430 | 0.002 / 2 |
| Leg A–D | 0.04, 0.04, 0.41 | ±0.130, ±0.130, 0.205 | 0.002 / 2 |

Derivation: overall 0.450 → leg 0.410 on the ground, seat underside 0.410, seat top 0.450;
inset 0.030 → leg centre at 0.180 − 0.030 − 0.020 = 0.130.

Recipe B (`stool-b.json`): **only** the vertical figures change — leg `dimensions` z 0.41 → 0.51,
leg `location` z 0.205 → 0.255, and seat `location` z 0.430 → 0.530. Seat underside and leg tops
then meet at z 0.510, overall 0.550. Seat dimensions, leg X/Y cross-sections and all bevels are
unchanged. (Correction: leaving the seat at 0.430 would drive the taller legs through it.)

Recipe identity checked by SHA-256 each run; module/CLI identities must equal the recorded
revision: `pipeline/primitive_recipe.py` `991d5f62…31399`, `scripts/primitive_recipe.py`
`4018b884…feb0e`, plus the three fixtures — no source edits mid-trial.

## Exact commands (worker runs, from workspace root)

Per run, replacing `RUN` and `RECIPE`:

```text
python tools/asset-pipeline/scripts/primitive_recipe.py plan --recipe RECIPE --out .dev-shots/reusable-pipeline-test-01/RUN/geometry/plan.json --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python tools/asset-pipeline/scripts/review_worker.py init --plan .dev-shots/reusable-pipeline-test-01/RUN/geometry/plan.json --manifest .dev-shots/reusable-pipeline-test-01/RUN/geometry/session.json
# then each plan-reported next stage individually until the master is saved and checked
python tools/asset-pipeline/scripts/primitive_recipe.py plan --recipe RECIPE --phase appearance --source .dev-shots/reusable-pipeline-test-01/RUN/geometry/prepared.blend --out .dev-shots/reusable-pipeline-test-01/RUN/atlas/plan.json --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python tools/asset-pipeline/scripts/review_worker.py init --plan .dev-shots/reusable-pipeline-test-01/RUN/atlas/plan.json --manifest .dev-shots/reusable-pipeline-test-01/RUN/atlas/session.json
# then each atlas next stage (prepare → uv pack → preserved-layout bake → reopen checks)
& "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/fixtures/verify_primitive_recipe_blender.py -- --recipe RECIPE --uv .dev-shots/reusable-pipeline-test-01/RUN/atlas/uv.blend --baked .dev-shots/reusable-pipeline-test-01/RUN/atlas/baked.blend --textures .dev-shots/reusable-pipeline-test-01/RUN/atlas/bake/textures --out .dev-shots/reusable-pipeline-test-01/RUN/verify/reopen.json
```

Worker may create only `stool-a.json`, `stool-b.json` and the runner/CLI JSON. No wrappers.

## Output paths (all new; nothing overwritten)

`.dev-shots/reusable-pipeline-test-01/` + `benchmark-stool-a-01/`, `benchmark-stool-a-02/`,
`benchmark-stool-b-01/` (each `geometry/`, `atlas/`, `verify/`), and parent captures in
`benchmark-review-01/`.

## Gate 1 stop (shape approval)

After A geometry: stop. Require saved master, passing health/evaluated checks, independent-part
and assembly-control evidence, neutral whole-stool views (front, side, three-quarter) and the
editability check. Parent inspects against the dimensions above. Only on approval: UV, bake,
UV/map inspection, source-vs-baked matched views. Then repeat A and B identically.

## Acceptance and predeclared tolerances (A vs repeat A)

Pass requires, per run: 5 independent mesh parts, 1 root, no locks/hidden-select on user parts,
expected evaluated triangle count, seat/leg dimensions within 1e-6 m of the table, exact seat
underside contact, zero runner-failed operations, UV audit zero global overlaps/degenerates,
five non-empty 256 maps, reopen verification pass.

Repeat A vs A: equal object/part names, counts, origins, dimensions and UV charts/orientations
within 1e-6; coverage within ±1.0 pp; map PNGs may differ in bytes; geometry/UV fingerprints must
match. B vs A: only leg height, leg z-location, seat z-location and derived overall height differ;
seat and leg X/Y and bevels within 1e-6.

## Budget and stop rules

Owned disposable Blender processes only (no live MCP). Two diagnostic attempts per blocker, then
return it. Runner caps 5 construction / 12 deadline operations per plan. One worker session, stop
at the gate. A held BLOCKED/STOPPED handoff ends the allowance. Any implementation-code edit or
manual geometry rescue is recorded and disqualifies the autonomy claim for that run; an
exact retry of identical inputs is allowed and recorded (compare shrink).

## Approvals requested

1. Dimensions/inset/bevel and centre-origin limitations above.
2. Adapter's fixed material and 256 atlas settings for this technical benchmark.
3. Creation of the three new run directories and the two recipe files.
4. The 30 mm inset measured from the seat's outer edge (leg outer face), not the leg centre.
