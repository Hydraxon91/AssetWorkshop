# AssetWorkshop handoff

> **Archived (2026-10-23 watering can).** Not a current handoff. Use root `HANDOFF.md`,
> the current card in `BLENDER_OWNER.md`, and `docs/execution-modes.md`. Commands,
> checkpoints and MCP precautions below apply only to that past task.

Updated: 2026-10-23. Intended for a new OpenCode/Astra session on this machine.
This is a state summary, not permission to bypass `AGENTS.md` or overwrite work.

## 1. Purpose and scope

AssetWorkshop is a standalone Blender authoring workspace, not a game repository.
We are developing a reference-led watering can while improving reusable local
authoring, reference-comparison, material, UV and delivery tools. Current work is
the watering-can assembly; no destination/game integration is approved.

User wants minimal routine intervention, editable construction, meaningful visual
review and saved progress. They dislike repeated replanning, workers exhausting
their steps without building, parent doing modelling instead of delegation, and
being asked to diagnose contours themselves.

User's latest instruction: **fix the rose rim first, then proceed to
shell/thickness**. This handoff pauses implementation before that sequence.

## 2. Start here

Workspace: `/Users/hydraxon/Documents/GitHub/AssetWorkshop`.

Read:
1. `AGENTS.md` — scope, preservation, ownership, delegation and evidence rules.
2. `BLENDER_OWNER.md` — ownership coordination; older sections are historical.
3. Load skill `gummy-3d-authoring` as the routing index, then only active-stage
   references: stage review, reference review, curved products, assembly as needed.
4. `.dev-shots/asset-pipeline/wateringcan_v2/curve_fit_01/current.md` — asset record.
   It contains historical sections and some suspect measurements; see below.

Do not inherit instructions from another repository. Do not preload unrelated
game contracts or the whole skill handbook. No paid generation, external services,
uploads, installs, dependency changes, commits or pushes are authorized.

## 3. How the workspace works

| Path | Role |
| --- | --- |
| `.opencode/agents/modeller.md` | Bounded implementation worker instructions |
| `.opencode/skills/gummy-3d-authoring/` | Authoring skill and targeted references |
| `tools/asset-pipeline/` | Experimental Python/job pipeline, Blender builders, audits and tests |
| `tools/asset-pipeline/scripts/reference_compare.py` | Shared calibrated plane/camera/overlay mapping |
| `tools/asset-pipeline/fixtures/` | Asset builders and regression fixtures; do not blindly rerun historical jobs |
| `.dev-shots/asset-pipeline/` | Ignored references, source checkpoints, captures and scratch evidence |
| `docs/` | Migration, operations, pipeline inventory and validation history |
| `contracts/` | Opt-in destination delivery contracts; none assumed for this can |
| `scripts/` | Preview and verification helpers |

`README.md`, `docs/migration.md`, `docs/pipeline-migration-inventory.md` and
`tools/asset-pipeline/README.md` explain the broader pipeline. Some introductory
status text is stale: historical context reports the pinned glTF validator was
subsequently provisioned/tested (9/9 smoke tests), while the pipeline README still
says it is not provisioned. Verify actual state before relying on that claim.
Live ComfyUI, destination intake and game integration remain deferred/unverified.

The pipeline entry is `tools/asset-pipeline/pipeline.py`; supported verbs include
inspect/uv/bake/hybrid/check/render/export/verify. Historical jobs can depend on
uncopied assets or old paths. Do not run them unchanged. Export helpers and tests
do not authorize export or prove likeness. `python3 launch.py --localhost` serves
the standalone preview, but starting a service is not part of the current task.

Git currently reports the root project files/directories as untracked. No commits
or pushes have been made. Ignored `.blend` checkpoints are NOT recoverable through
Git and must be preserved separately. A handoff to another machine needs these
ignored assets copied explicitly; a repository clone alone is insufficient.

## 4. Blender access and operating rules

Blender previously reported 5.2.2 LTS, MCP addon 1.8.6, protocol 14. External
libraries and paid generators were off. Use Blender MCP through the available
tool catalog (`execute` -> `tools.blender.*`); inspect addon and scene first.

Parent plans and independently reviews; `modeller` implements bounded geometry
stages. One Blender owner globally. Require explicit STOPPED handback before
parent review or another worker. Never drive Blender concurrently.

User most recently authorized using **the running Blender via MCP**, with no need
for headless. Workers have encountered shell permission denials. A denial is a
blocker, not permission to try command variants, interpreters or alternate tools.
Return it once. Parent has previously used separate background Blender for
read-only verification; do not assume this grants a worker shell access.

**Do not call `bpy.ops.wm.open_mainfile()` from MCP code.** File opening coincided
with a lost connection/Blender exit. It is a precaution, NOT a proven crash cause.
User opens checkpoints through Blender's UI. Inspect filepath and unsaved state
before work. Never load over unsaved work.

Save OFTEN, under NEW names: before edits, after each meaningful construction
step, before evidence. Avoid combined edit/open/render batches. No overwriting
baselines or user checkpoints. Keep scripts in files via file-edit tools.
Look up shader nodes by type; inspect enum choices instead of assuming identifiers.

## 5. Watering-can decisions (authoritative)

- User selected **`CF_Body_A`**. No A/B/C reranking or return to older B preferences.
- User-corrected body/cutter/root pose is authoritative. Original corrected source:
  `curve_fit_01/manual_control_01/model_control_working_02.blend`.
- `Model_Control` is rotated approximately +90 degrees Z. Do not reset it.
- A, profiles, cutters and original body shape stay protected during attachments.
- B/C remain hidden backups, not deleted.
- New parts and editable source controls follow `Model_Control`; reference/cameras
  stay independent. Convert world/reference targets through the actual root inverse.
- Body height **298 mm** is the scale anchor. Former 180 mm OD was superseded by
  reference-led proportions. Other width/shoulder/base/opening proportions are
  provisional; do not resurrect the old OD constraint.
- Shape/whole-assembly silhouette before final joins, topology, UVs and optimization.
- The open bottom is explicitly deferred to shell/thickness, not an approved final
  feature. User approved rose refinement **then** shell/thickness.

## 6. Reference and orientation

Sole reference:
`.dev-shots/asset-pipeline/wateringcan_body_trial/reference/derived/plane_profile.png`
(402 x 327, stylized elevated side drawing, not a full orthographic reconstruction).

Registration record:
`.dev-shots/asset-pipeline/wateringcan_v2/curve_fit_01/reference_record_orientation_fixed.json`.
It holds source hash, trace, crop, uncertainty and mapping history.

- Pixel coordinates: top-left origin, image origin datum `(220,315)`.
- Uniform scale: `1.0996309963 mm/px` (298/271).
- Camera on world -X looking +X; image-right world -Y; image-left/spout world +Y;
  image-up world +Z.
- Reference world mapping in mm: Y=(220-u)*scale, Z=(315-v)*scale.
- Locked, uniformly scaled `CF_Ref_Plane` remains enabled in scene and render-hidden.
- The side camera is near-level, but drawing is elevated: rose face appearance in
  the overlay is not conclusive. Inspect real three-quarter head views too.

Registration tools have tested subpixel alignment; that proves pixel mapping,
not that a single elevated drawing establishes hidden depth or all viewing angles.

## 7. Current saved and live state

Asset folder:
`.dev-shots/asset-pipeline/wateringcan_v2/curve_fit_01/assembly_01/`.

**Latest confirmed live file:** `assembly_corrected_02.blend`, clean at the worker's
last stopped handoff. Parent then made two read-only MCP diagnostic calls. No new
geometry has been authored since. Inspect current live state afresh before editing.

| File | Meaning / SHA-256 |
| --- | --- |
| `assembly_baseline_01.blend` | Actual user pose before attachments; `0a1c3e0b76a42efd5efb188f87177bce8cb4951f20fe8aca5b81d45088dbd8f1` |
| `assembly_review_01.blend` | First complete assembly; `58ddf1b4eb32e90390972590e5e7fbb2a679c16e5f4cf864de4c060f9b2e547c` |
| `assembly_corrected_01_pre_handle.blend` | Spout-only intermediate, retained |
| `assembly_corrected_01.blend` | Separate taper profile + handle correction; `d2fefec3100ac54819d03ea681bca2139db013a5452c90615fe30ebefa181ced` |
| `assembly_working_02.blend` | User's later unsaved changes preserved before further work |
| `assembly_corrected_02_spout.blend` | Head-only intermediate; `0034eac69eaa465d6dc216bc50d360a8e8426df594384c7e0eeaf5182963d7b9` |
| **`assembly_corrected_02.blend`** | Latest assembly; **`bc6767c3775e567546f93a4f217ad2753da1e3d101e781fb6699fa4e5f02d863`** |

Verify hashes if transfer/state matters. No worker currently owns Blender.

## 8. Construction and known geometry

### Body

`CF_Body_A` derives from an editable shared profile with live Screw, Subdivision
and Boolean cutter. `CF_Profile_A` and body share source mesh data: editing the
profile affects the body. Do not rebuild from an old builder.

Evaluated body: 1,764 vertices / 3,364 triangles. Exactly two observed open loops:
- Intended slanted mouth: 84 vertices, z about 279.5–298 mm.
- **Entire bottom open:** 80 vertices, radius about 43.8 mm, z=0.

No shell, wall, floor or mouth rim thickness exists yet. Zero nonmanifold edges
with more than two faces was observed, but open boundaries mean it is not watertight.

### Spout and head

`CF_Spout_Path`: editable 16-point Bezier axis, round bevel, per-point radii unity,
bevel depth 1, resolution_u 12, bevel_resolution 4, fill caps on.
`CF_Spout_Taper`: separate editable Bezier profile, X normalized distance along
axis, Y radius in metres, no material, render-hidden, under `Model_Control`.
It is still a round sweep, now with a separate radius profile — NOT an independent
upper/lower contour loft or a separately authored rose half-section.

Current taper `(fraction, radius_mm)` from last read:
`(0,26),(.08785,23.2),(.19810,20.5),(.32395,18.5),(.44980,17.6),
(.57565,17),(.68348,18.8),(.76885,20.4),(.82317,21.6),(.86637,22.6),
(.90052,23.4),(.92768,23.8),(.94579,23.8),(.96540,23.7),(.98316,23),
(1,19.8)`.

All taper handles AUTO. Changing Y legitimately recomputes handle X/Y; one worker
failed by asserting those handles stayed fixed. Do not repeat that diagnostic.
No bore or sprinkler holes. Evaluated spout 4,340 triangles.

### Handle

`CF_Handle_Path`: editable 14-point Bezier sweep. Current mid control radius about
12 mm, ends about 14 mm. Axis retained from correction 1; only section thickened
in correction 2. Evaluated handle 3,764 triangles. Both ends overlap the body, but
nearest vertex distances alone do not prove complete contact or a sound union.

## 9. What is verified, what is NOT

Independent saved-file checks for correction 1 found original source meshes and
parents preserved; evaluated A difference ~7e-6 mm; root/reference/material state
preserved. Correction 2 worker reported zero protected coordinate/matrix change;
parent independently rendered the saved result but did not repeat every hash check.

Inspected latest images:
- `assembly_corrected_02_side_overlay.png`
- `assembly_corrected_02_side_neutral.png`
- `assembly_corrected_02_tq_spout_neutral.png`
- `assembly_corrected_02_tq_handle_neutral.png`

Assembly is recognizable. Handle is more substantial and lower attachment raised;
spout/body overlap wider. Head still visually reads flat with little rim relief.
Visual likeness, geometric health, fit and user acceptance are separate claims.
No final-topology, wall thickness, water containment, portability or game-readiness
claim is justified.

### IMPORTANT: rose diagnostics are suspect

Previous parent report called the evaluated cap ~47.0 mm against ~47.8 mm rim and
concluded the taper endpoint was not reaching the cap. That was NOT a reliable
cap measurement: helper `_spout_radial_metrics` selects vertices by nearest-axis
polyline projection; rim vertices can be classified at t≈1 as well. The intended
endpoint radius is 19.8 mm. Determine the actual cap ring/plane before changing it.

The most recent ad-hoc MCP projection function also contained a clear bug:
it returned `best[0], t` instead of `best`, using the LAST segment's t for every
vertex. Its result selecting all 2,196 vertices as the tip region is invalid.
Discard that probe entirely. Do not encode its output as geometry evidence.

Likewise, prior figures named "radius at one third" (~20.7 mm) used maximum nearest
polyline distances over a broad fraction band, not an exact evaluated cross-section.
Treat them as approximate sampling, not authoritative radii.

Earlier docs say radius 31 mm gives 56 mm diameter: arithmetic error, it gives
62 mm (which was the actual first-blockout measurement). Historical prose is not
reliable dimension authority. Some current-record language incorrectly says the
original sweep had uniform radii; it already had varying per-point radii.

## 10. Failures and recovery lessons

- Repeated workers hit their step caps (often 24 steps) despite narrower briefs.
  Use small bounded tasks and save before evidence. Do not spend entire runs
  inspecting the same known metadata or building a general framework.
- Blender exited/disconnected during earlier continuations. No crash report was
  located in the searched locations; absence is not proof no report exists anywhere.
  Cause remains unproven. MCP file switching is a suspected risk, not established
  explanation for every crash. User reopened the corrected file and found it stable.
- Shell denials caused a worker to try another invocation and search permissions.
  This violated the return-blocker rule. Do not repeat it.
- `assembly_proof.json` has false flags from 1e-9 comparisons and hidden-object
  cached world matrices. Inspect authored basis/parent state and use float-aware
  congruence (~0.01 mm) rather than exact matrix equality after decomposition.
- A worker restored an unsuccessful AUTO-handle edit and re-saved the working
  checkpoint. Preserve existing files now; do not casually repeat restoration or
  overwrite a baseline. No automatic rollback/replacement worker after interruption.
- Parent previously returned to headless captures even after the user requested
  live Blender. Do not use that history as fresh authorization to switch methods.

## 11. Immediate next actions

User approved **1. rose rim, then 2. shell/thickness**. Do not ask the same broad
choice again or rerank body candidates.

### A. Diagnose and repair the rose

1. Inspect live filepath/dirty and ownership; preserve any new unsaved user edits
   to a fresh checkpoint. No file switching through MCP.
2. Read-only identify actual cap polygon/ring and evaluate its plane/radius, or
   inspect an isolated head close-up from a meaningful angle. Do not keep tuning
   taper stations based on the broken projection tests.
3. Modeller makes one bounded head-only change with a hypothesis and measurable
   expected change. Retain editable axis/profile and preserve body/handle/root.
   If a separate editable rose section is needed, state the method and preserve
   superseded construction hidden; no deletion. No sprinkler holes yet.
4. Save a new-name checkpoint BEFORE evidence. Inspect clear head close-up and
   assembly three-quarter. Stop on regression or two failed diagnostics.

### B. Shell/thickness after the rose works

The user authorized this next stage, including closing the bottom. Exact wall and
floor thickness have NOT been agreed. Propose sensible provisional values, clearly
classified, before implementation; do not silently invent hard dimensions.
Keep exterior/body-height/pose protected and preserve editable source/operands.

Plan the mouth rim, inner wall and floor as a coherent cavity. The original body
and profile share data; shared-user effects must be checked before changing them.
Do not assume a Solidify modifier alone closes an open-bottom surface correctly:
it can create an annular bottom rim, leaving the central hole open. Verify an
actual floor and intended mouth opening, wall clearance, no unintended openings,
finite/nondegenerate geometry and unchanged outer silhouette. Spout bore, attachment
union, detailed holes and export should not be inferred from shell authorization.

Save before each substantive operation, separate evidence from construction, and
report completed/blocked/unverified plus actual saved/live state. Passing checks
does not grant user acceptance.

## 12. Key scripts (inspect before using)

- `build_wateringcan_profile.py`: historical body construction; do NOT rerun on A.
- `build_wateringcan_assembly.py`: first attachment builder and capture helpers;
  `build()`/`baseline()` refuse existing output; old root checks are too strict.
- `correct_wateringcan_assembly.py`: first interrupted correction; superseded;
  do NOT execute it merely because it exists.
- `correct_wateringcan_assembly_v2.py`: staged correction-1 builder/verification;
  do NOT rerun stage1 or stage2 wholesale on latest geometry. Stage2 assumes old
  station/radius tables and old output filenames.
- `assembly_01/parent_verify_assembly.py`: saved-baseline preservation comparison.
- `assembly_01/parent_capture_02.py`: parent review captures; its radial sampling
  is approximate, not a validated cap-ring detector.

All source files and assets stay local/uncommitted. No active worker is running
at this handoff. The requested next action is transferring context, not launching
another implementation worker.
