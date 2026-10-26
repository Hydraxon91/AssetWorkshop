# Benchmark results — four-legged stool A / repeat-A / B, 2026-10-26

**Verdict: PASS for tool reuse and parameter-only variation. Agent operation UNTESTED.**
A, repeat-A and B completed the frozen pipeline with no implementation-code change and no
manual geometry rescue.

Operator: `deepseek/deepseek-flash` is the current approved operator (see
`docs/operators.md`). It was **not invoked** in this run. The parent executed every
operation directly with the reviewed adapter and runner. See "Operator and autonomy"
below: this measures tool reuse and parameter-only variation, **not** operator operation
success. The historical `refuseless/...abliterated` identifier belongs to the earlier
plan and review, not to this run.

## Checkpoints selected

Paths relative to `.dev-shots/reusable-pipeline-test-01/`. SHA-256 first 16 hex.

| Run | Checkpoint | SHA-256 |
| --- | --- | --- |
| A | `benchmark-stool-a-01/geometry/master.blend` | `0add93c0d87da4cc` |
| A | `benchmark-stool-a-01/geometry/prepared.blend` | `35c666c679197c4d` |
| A | `benchmark-stool-a-01/atlas/uv.blend` | `261f1a1aae0828a1` |
| A | `benchmark-stool-a-01/atlas/baked.blend` | `22c074d6149d0121` |
| repeat A | `benchmark-stool-a-02/geometry/master.blend` | `f3d0fa5c66c9fd64` |
| repeat A | `benchmark-stool-a-02/atlas/uv.blend` | `eb0dfeaa133f75ae` |
| repeat A | `benchmark-stool-a-02/atlas/baked.blend` | `b19b5c00f03074f9` |
| B | `benchmark-stool-b-01/geometry/master.blend` | `447738c0608fb5dc` |
| B | `benchmark-stool-b-01/atlas/uv.blend` | `075928634182ef3e` |
| B | `benchmark-stool-b-01/atlas/baked.blend` | `8ba5563d55758108` |

Editable master for A is `benchmark-stool-a-01/geometry/master.blend` (live bevel modifiers,
five independently selectable parts, one `Stool` root). `atlas/baked.blend` and `atlas/uv.blend`
additionally contain hidden `Bake__*` single-user copies without modifiers.

## A / repeat-A / B comparison

| Criterion | A | repeat A | B |
| --- | --- | --- | --- |
| Recipe SHA-256 | `24863331…48fed1` | `24863331…48fed1` (identical file) | `07506b9c…8ae8e00` |
| Runner operations | 8 geometry + 8 atlas, 0 failed | 8 + 8, 0 failed | 8 + 8, 0 failed |
| `evidence_complete` | true | true | true |
| Objects | Seat + 4 legs + root | same | same |
| Evaluated tris | 540 | 540 | 540 |
| Seat dimensions | 0.360 × 0.360 × 0.040 | identical | 0.360 × 0.360 × 0.040 (unchanged) |
| Leg dimensions | 0.040 × 0.040 × 0.410 | identical | 0.040 × 0.040 × 0.510 |
| Leg centres | (±0.130, ±0.130, 0.205) | identical | (±0.130, ±0.130, 0.255) |
| Seat centre z | 0.430 | 0.430 | 0.530 |
| Overall height | 0.450 | 0.450 | 0.550 |
| Leg top − seat underside | 0.0 (all 4) | 0.0 | 0.0 (all 4) |
| Leg outer face / seat edge | 0.150 / 0.180 = 30 mm inset | identical | identical |
| Bevels | 0.002 m / 2 seg, all parts | identical | identical |
| Origins | box centre, all parts | identical | identical |
| Root / dependence | `Stool` empty parents all 5; root move carried children; leg move left seat fixed | identical | identical |
| UV islands | 30 | 30 | 30 |
| Global overlap pairs | 0 | 0 | 0 |
| UV degenerates | 0 | 0 | 0 |
| Coverage | 23.343 % | 23.343 % | 22.382 % |
| Chart gap at 2048 | 96.0 px | 96.0 px | 95.99997 px |
| Bake | 5 maps at 256², dilation 4 px | 5 maps at 256² | 5 maps at 256² |
| Reopen verifier | pass | pass | pass |

### A vs repeat A, within predeclared tolerances
- Part names, counts, parents, modifier types/widths/segments, dimensions, origins, material
  assignment: **exactly identical** (byte-level JSON comparison of the extracted fields).
- Packed `AtlasUV` corner coordinates: **exactly identical** across all 5 bake copies, 216 corners
  each.
- Pre-existing `UVMap` layer: max delta **6.0e-8** (float32 rounding), inside the 1e-6 tolerance.
- Layout metrics identical; coverage delta 0.000 pp (tolerance ±1.0 pp).
- All five baked PNGs **pixel-identical** (basecolor, roughness, metallic, normal, ORM).
- `.blend` file hashes differ (A `22c074d6…`, repeat `b19b5c00…`): file bytes are not
  reproducible. Equivalence was judged on content, per the declared method.

### B vs A
- Only intended changes: leg z-dimension 0.410 → 0.510, leg z-origin 0.205 → 0.255, seat
  z-origin 0.430 → 0.530.
- Unchanged: seat dimensions, all leg X/Y cross-sections, all leg X/Y positions, all bevels,
  all material and UV settings, tool and module identities.
- The B correction was applied: the seat moved to z 0.530 so the 510 mm legs meet the seat
  underside at 0.510 instead of passing through a seat left at 0.430.

## Module, CLI and recipe identities (recorded per run)

Unchanged across all three runs; the first four match the values already recorded in
`adapter-result.md` exactly.

```
pipeline/primitive_recipe.py                 991d5f623611a0e0fdc6bf4162e8e00c6567489f5723c7e9d6c13e31b9331399
scripts/primitive_recipe.py                  4018b88455cbd1ec067cc4eaa75194fc5cf54d5b7c161113653a861bef8feb0e
scripts/review_worker.py                     23d6a2f42976ceb2f8606e711fbb5da6837d70e1be2f4c0afab00cd11a22f851
scripts/review_blender.py                    3aa4c578ed7efa950816e8bfdd5191d77ae67e8160afa269bb5ead50edcf535c
fixtures/verify_primitive_recipe_blender.py  01b8a47e1766e2d677bf730a904371ec6c092ee80743f9bdf6a85cdaa4a75013
pipeline/uv.py                               041b1f3b02abd41f5bef0736420d6c1fd40a1aa19e59bad4fbd5c2e33ec6efd4
pipeline/bake.py                             f651c4d1ecaabdfa9343801e9e6fe4e1daa2e64c07950a03f4dbc1564308c465
pipeline/packing.py                          36f1225dbbec817184696885360d70948e76bf364afb1eab35fce3387d22f138
pipeline/atlas_layout.py                     b98646dbf7253ee7afca0d5aa1eef0028b78845d93c19e96dc4711906c7e8f2f
pipeline/preservation.py                     485df9a96c5fa8a67eaa016db000660429d046f57ad1dab988ea0a26c940b611
recipe A / repeat A                           24863331b40e7a6cf5295c6e8937c0142b9189bc8b226a75b47b085f4148fed1
recipe B                                     07506b9c09c766d4ef0871d8cb37b79ca3c4231c1ef31132d7c7033238ae8e00
```

At the time of the benchmark, `git status` showed no modification to any file under
`tools/asset-pipeline/` during the run. The adapter sources and this docs folder were
pre-existing but untracked; the only tracked change recorded then was `BLENDER_OWNER.md`.
**Provenance limit:** the repository has a single commit and the adapter remains untracked.
The hashes above were re-verified against the working tree on 2026-10-26 and match, but a
clone cannot reproduce the run until the adapter and this record are committed or a
versioned toolchain lock is added. The working tree also contains later
documentation/permission edits; they do not change the recorded hashes.

## Inspected evidence

- Geometry: `benchmark-stool-a-01/geometry/master.png` (three-quarter),
  `benchmark-stool-a-01/views/stool-a-master_front_solid.png` and `_side_solid.png` (700×900),
  `benchmark-stool-b-01/views/stool-b-master_{three_quarter,front,side}_solid.png`.
  Parent inspected all: level seat, four upright legs, even 30 mm inset, no leg through seat.
- UV: `benchmark-stool-a-01/uv-layout/Bake__Seat/1024/color_layout.png` and
  `Bake__Leg_A/1024/color_layout.png` from the existing `uv-layout-extractor`
  (`uv_color_layout.py`, layer `AtlasUV`). Seat shows 6 distinct charts; leg shows 6 with the
  four narrow side charts. All charts inside the 0–1 frame, no overlap.
- Maps: `benchmark-stool-a-01/atlas/bake/textures/atlas_basecolor.png` and `atlas_normal.png`.
  Basecolour is populated across all 30 charts. Normal is near-flat with small bump variation
  (R/G 0.478–0.522), metallic constant 0, ORM present.
- Source vs baked, matched camera/target/direction/resolution:
  `appearance/source/stool-a-source-03_three_quarter_material.png` and
  `appearance/baked/stool-a-baked_three_quarter_material.png`; front pair likewise.
  Checker placement and colours transfer. Baked edges visibly soften/alias, as declared for
  256 px. Quantitative shader error is unmeasured.
- Data-level editability: `benchmark-stool-a-01/editability/editability.json` and
  `benchmark-stool-b-01/editability/editability.json` — root parenting, origins, locks,
  hide-select, mesh users, dependence motion, evaluated retention, selection.

## Passed / failed / unverified

**Passed**
1. Complete supported asset: five parts, 540 evaluated tris, one assembly control.
2. Geometry health: all parts closed, 1 island, zero non-manifold/boundary/degenerate/loose/winding
   faults, base and evaluated, every stage and every run.
3. Part independence: five single-user meshes, no locks, no hidden-select, individually
   selectable with an active object.
4. Assembly control: `Stool` empty parents all five; moving it moves children exactly; moving
   one leg does not move the seat.
5. Dimensions and contact: seat 360×360×40, legs 40×40, 30 mm inset, 450 mm overall, leg tops
   exactly at the seat underside, all four corners, in A and B.
6. UV: 30 islands, 0 global overlaps, 0 degenerates, 96 px chart gap at 2048, 23.3 % coverage.
7. Bake: five non-empty 256² maps, preserved layout, dilation 4 px, correct shader image
   bindings and colour-space tags.
8. Reopen verification: exact source state, exact indexed geometry and UV corners, baked shader
   images, decoded maps — for all three runs.
9. A ≡ repeat A within predeclared tolerances.
10. B differs from A only in the declared dimensional parameters.
11. No implementation-code change; no manual rescue; no export, controller or destination work.

**Failed**
- None in the pipeline itself. Two operational notes, neither a pipeline failure and neither a
  rescue: (a) the first source-capture attempt collided with the extractor's own
  refuse-to-overwrite guard and was re-run under a new name; (b) PowerShell reported exit code 1
  for the material captures because Blender writes a `World.use_nodes` deprecation warning to
  stderr, while the captures themselves completed and printed `CAPTURE_REVIEW` with 2 captures.

**Unverified**
- Real mouse interaction, viewport responsiveness and click-select in a live Blender session.
  Editability was established at data level and by rendered inspection only.
- Quantified shader transfer error and lower-mip safety. 256 px padding is not proof of mip
  safety; the maps are certified at native 256 only.
- Self-contained texture packaging: images live in the workspace and are not embedded.
- Production furniture quality. This is a box-built stool: centre-origin pivots, butt contact
  with no tenons or shoulders, one shared procedural material, no fillets, no taper, no joinery.
- Byte-reproducible `.blend` output.
- `bake/baked.blend` (the pipeline's own bake output) differs from `atlas/baked.blend` (the
  runner-saved final). Both pass their checks; the final selected checkpoint is `atlas/baked.blend`.

## Operator, autonomy and interventions — recorded separately

- **Operator turns: 0.** The parent (this session) executed every command. The current
  approved operator `deepseek/deepseek-flash` was never invoked, so this run provides
  **no evidence about that operator's ability to operate the pipeline**. The historical
  `refuseless/...abliterated` worker was also not used. The A/repeat-A/B question about
  *tool reuse and parameter-only variation* is answered; the question about *operator
  operation success* is **untested**. The parent offered to delegate; the user asked to proceed.
- **Runner operations: 48** total (16 per run × 3 runs), all exit 0, plus 8 owned disposable
  Blender invocations for probes and captures outside the runner (editability probe ×2, capture
  review ×3 sessions, UV layout sheets ×6, reopen verifier ×3).
- **Elapsed time: roughly 25 minutes** of wall clock for the full three-run benchmark including
  inspection, dominated by process startup and renders.
- **Interventions by parent:** (1) corrected the B recipe seat height — a user-identified
  dimension error, caught before execution; (2) wrote two new *harness* scripts under
  `.dev-shots/`: `probe_editability.py` (read-only data-level editability probe) and
  `compare_extract.py` / `compare_extract_raw.py` (cross-run comparison). These are benchmark
  measurement tools, not asset implementation: they neither build, unwrap, bake nor modify the
  asset, and no production source file was touched.
- **Unplanned manual rescue of the asset: none.** Every asset byte came from the reviewed
  adapter, runner, UV and bake tools driven by recipe parameters.

## Next authorized action

User decision only. No further action underway; all owned processes exited; interactive Blender
untouched and its filepath/dirty state unknown.
