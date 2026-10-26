# Live Blender ownership

> **Historical ownership cards, not current authorization.** Content preserved from
> `BLENDER_OWNER.md` on 2026-10-26 when that file was reduced to its current card. The
> "Current state" heading below describes a past state. Read the repository
> `BLENDER_OWNER.md` for the present owner. Asset evidence/history remains in the linked
> briefs and `.dev-shots/`.

Project: `C:/Users/Hydra/Documents/GitHub/AssetWorkshop`.
Coordination record, not a technical lock or permission to drive Blender.

## Current state — stool A/repeat-A/B benchmark (2026-10-26)

- COMPLETED / parent STOPPED. Four-legged stool benchmark passed end-to-end: A, repeat-A in a
  fresh directory, and variant B (550 mm) via recipe parameters only. 48 runner operations,
  0 failed; all owned Blender processes exited, no timeout/live signals.
- Editable master A: `.dev-shots/reusable-pipeline-test-01/benchmark-stool-a-01/geometry/master.blend`,
  SHA256 `0add93c0d87da4cc5836000e0e8c8dd67f79490830644119727c181dd630563e`. Baked A:
  `benchmark-stool-a-01/atlas/baked.blend`, `22c074d6149d0121d996608407d2ac10b9a573fdc58391cd97af92eaa27184c7`.
  B master: `benchmark-stool-b-01/geometry/master.blend`, `447738c0608fb5dc`.
- Result: `docs/reusable-asset-pipeline-test/results.md`. Brief: `benchmark-brief.md`.
  A and repeat-A are equivalent within declared tolerances (identical parts, identical packed
  AtlasUV, 6e-8 max delta on the legacy UVMap layer, all five baked maps pixel-identical);
  .blend bytes are not reproducible. B differs only in leg height, leg z-origin and seat z-origin.
- Model honesty: `refuseless/deepseek-v4.1-flash-abliterated` was NOT invoked. The parent
  executed all operations directly. This run proves tool reuse and parameter-only variation;
  it proves nothing about that model's ability to operate the pipeline. Model turns 0.
- No implementation-code change under `tools/asset-pipeline/` (hashes recorded in results.md).
  Only new files: two recipes, and benchmark measurement scripts under `.dev-shots/`
  (read-only editability probe, cross-run comparator) that do not build, unwrap, bake or modify
  the asset. No export, controller work, destination integration, install or live MCP.
- Unverified: live mouse/UI responsiveness, quantified shader error, lower-mip safety, embedded
  texture packaging, production furniture quality, byte-reproducible .blend. Interactive
  filepath/dirty state unknown and untouched.

## Historical state — reusable primitive adapter development (2026-10-26)

- COMPLETED / parent and all workers STOPPED. User-approved parent-direct adapter
  implementation produced two-box source/prepared/UV/baked checkpoints and a passing
  reopened exact-source/corner/map fixture. No owned process remains; all completed
  normally or exited1 on recorded development assertions, no timeout/live signals.
- Latest baked: `.dev-shots/reusable-pipeline-test-01/adapter-atlas-01/baked.blend`,
  SHA256 `6b2820e8a6bdbd2ca9e7d543e1483dcd269d2583390d0634c6a45771c0121ba0`.
  Editable master: `adapter-fixture-02/master.blend` under same asset folder, SHA256
  `b425d7f41fa820a3252abc13d8bf98d208f535709a46a15d6a1ec1a33eeb8f48`.
- Primary authoritative result/history/evidence: `docs/reusable-asset-pipeline-test/adapter-result.md`.
  Initial transform-roundtrip and material-user-count assertion failures retained;
  fixes diagnosed/tested, not an autonomous no-rescue success. Pure tests38 pass.
- DeepSeek initial source review completed; final fixes/presets parent-only review
  initially after provider Free usage limit blocked execution request before it began.
  Subsequent user-requested Abliterated final READ-ONLY review succeeded, STOPPED,
  no fixed-revision fixture blocker; limits in `final-code-review.md`. No
  provider substitution/permission changes. UI editability, repeated variants,
  quantified shader transfer/mips and user acceptance unverified.
- No live MCP or controller/barrel edits, source checkpoint overwrites, installs,
  new runner or export. Interactive filepath/dirty state unknown and untouched.
  Next gate: benchmark scope/model availability; no further action underway.

## Historical state — reusable pipeline panel smoke (2026-10-26)

- COMPLETED / parent and modeller STOPPED. Unchanged fixed-panel smoke passed
  nine operations of twelve; all eight owned Blender processes exited0. No live MCP,
  tool/source changes, controller/barrel work, UV/bake/export or active writer.
- Saved `.dev-shots/reusable-pipeline-test-01/panel-smoke-01/after.blend`, SHA256
  `3383f08994bc6179e6e2552d0a4cde9792a60970cfa131512b4187fcac42f28f`.
  Parent inspected both matched PNGs/checks and verified all11 operation output
  hashes. Result: `docs/reusable-asset-pipeline-test/panel-smoke-result.md`.
- Parent reviewed existing preset/builder/save/check/capture source in the tooling
  audit. Explicit Blender executable exists at
  `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`; target run directory
  did not exist at preflight. All previous barrel workers/processes recorded stopped
  below. Interactive filepath/dirty state unknown and intentionally untouched.
- One outcome: saved before/after panel, passing health/preservation checks and
  matched neutral evidence. This is execution plumbing, not general modelling or
  parameter-selection validation. See `docs/reusable-asset-pipeline-test/README.md`.
- Next gate: user approval for bounded adapter-development/benchmark scope.

## Historical state — barrel junction pilot (2026-10-26)

- LATEST / photo request COMPLETED, parent STOPPED. Inspected matched sheet
  barrel-efficiency-01/texture_comparison_01/barrel_texture_comparison_02.png.
  Temporary projected-UV textured preview visibly has seam/stretch artifacts;
  not a bake. Source/candidate geometry,sourceUV,slots and saved SHA preserved.
  All owned processes exited. No live MCP or baseline saves. User cancelled
  workflow discussion/changes in this session; no such work remains authorized.

- ACTIVE photo request: temporary texture/clay comparison of full saved retopo and
  source in owned disposable process, no live MCP or baseline saves. Modeller authors
  only texture_comparison_01/preview.py; parent reviews/executes. No shape edits/bake.

- CURRENT / parent STOPPED: full barrel geometry saved at
  barrel-efficiency-01/full_retopo_02/candidate_retopo_01.blend, SHA256
  bcd4ae0e9a427a0f9e116d6839920f1fc279b3bfd43ee6409e91e5ee3b1ad575.
  9600tri/4802v, saved-reload health PASS closed1island. All four whole-model
  candidate/source captures inspected, matching cameras/shading, softer source
  relief disclosed. User review gate; no appearance/export authorization.
  Source/oldcandidate hashes unchanged; no interactive Blender driven. All owned
  processes exited; no worker remains active. Current criteria/result in asset brief.

### Historical continuations — superseded by saved full candidate above

- ACTIVE fixed-layout full build: parent supplied full_retopo_02/layout.json,
  anticipated9600 triangles. Modeller owns other NEW full_retopo_02/ files and
  owned disposable processes only, no live MCP. Existing raw samples reusable;
  discovery labels rejected. One whole-model saved candidate/review, no config edits.

- LATEST: full-retopo worker STOPPED at ceiling, source sampling only. No full
  geometry/checkpoint. Parent rejected handoff's63-stave claim: actual sample JSON
  says20; landmark inference also omits verified upper hoop. Raw grid preserved,
  but proposed assembly not approved. No active worker/process/live MCP ownership.

- ACTIVE: user requested FULL barrel retopology progression. Modeller owns NEW
  barrel-efficiency-01/full_retopo_01/ and owned disposable Blender processes only.
  Geometry whole-model stage, approximate <=10k triangles; all defining contours
  required. Prior source/candidate/pilot immutable. No live MCP, UV/bake/export.
  Parent whole-model review after saved candidate; see asset brief current card.

- LATEST / parent STOPPED: one structured junction saved at
  barrel-efficiency-01/structured_build_01/junction_pilot_01.blend, SHA256
  0f7405d6c04c63795a6ec25080ec2e019160c99224bad47b5a363bd5df66535e.
  234v/204q/408tri, source retained hidden, baseline source/candidate hashes unchanged.
  Corrected health pass + inspected matched region captures (capture_01/) demonstrate
  improved local hoop shading. Original health failure retained: hidden source
  transform needed dependency evaluation; no geometry repair was made.
  All owned processes exited, no live MCP/interactive scene changes. User review
  gate before replication; full barrel, UV/bake/export remain unauthorized here.

- Active: user approved sparse junction build. Modeller prepares exact new
  structured_build_01/ scripts only, cap16 turns, no process/native execution
  before parent review. Earlier source/candidate diagnostic complete. No live MCP.

- Latest: corrected-region verification COMPLETED, parent STOPPED. Two recovery
  diagnostic processes exited0, no baseline saves/live MCP/geometry edits. Matched
  inspected region pairs in barrel-efficiency-01/corrected_region_01/recovery_01/.
  Source/candidate hashes unchanged. Source groove is theta=-90; upper hoop and
  shoulders contained in normalized z=.17-.39. No worker/process remains active.
  Next scoped action: sparse junction build/preflight, not whole-barrel replication.

- Active approved continuation: VERIFICATION ONLY, corrected-region source/candidate
  captures and radial sampling. Modeller owns NEW corrected_region_01/ files and
  owned disposable runner processes only. No live MCP or baseline saves. Previous
  workers stopped; all prior artifacts read-only. See asset brief active continuation.

- Active asset: `.dev-shots/barrel-efficiency-01/`; approved representative structured
  hoop/stave topology pilot only. Current criteria/limits are in its `brief.md`.
- Modeller assigned only new `structured_pilot_01/` files and owned disposable
  Blender processes. No worker may drive interactive Blender/MCP in this pass.
- Protected source and previous candidate retained. Live filepath/dirty state is
  unknown and deliberately untouched. Prior workers recorded STOPPED.
- Go worker explicitly STOPPED: two completed read-only disposable probes, no
  in-flight processes, no geometry/checkpoint. Partial artifacts in `structured_pilot_01/`.
- User requested provider switch. Replacement modeller assigned only NEW
  `structured_pilot_02/`, model `refuseless/deepseek-v4.1-flash-abliterated`.
  Replacement explicitly STOPPED, no changes/processes. Prior artifacts read-only.
- Current continuation is preparation-only: modeller writes proposed script/plan
  under `structured_pilot_02/`, no shell/Blender/runner execution. Parent reviews
  before any construction; no interactive ownership granted.
- Preparation worker now STOPPED, no processes or built checkpoint. Proposed
  structured_pilot_02 scripts retained but execution BLOCKED by parent review
  (sampling bracket bug, density/landmark and comparison design issues). No worker
  currently owns Blender. Next authorized scope remains representative junction only.
- User approved preparation corrections. Modeller assigned NEW structured_pilot_03/
  only, prior artifacts read-only, no Blender/shell execution. Return revised design
  and scripts for parent review, not an automatic build. Same Refuseless model.
- Correction worker STOPPED; parent stdlib tests 9/12 pass, design still blocked.
  No Blender process/checkpoint or active worker. Automatic preparation rewrite
  loop stopped; measurement/strategy decision pending (see asset brief).
- Parent completed narrow read-only existing-probe measurements, STOPPED. Results
  in barrel-efficiency-01/landmark_diagnostic_01/measurements.json. Old dense grid
  truncates likely upper hoop at z=.22; target diagnostic region proposed .17-.39.
  No Blender accessed, no owned process or checkpoint; next boundary is targeted
  source/old candidate visual sampling before geometry construction.

## Historical state — seat closeout

### Latest appearance checkpoint (2026-10-26)
- Quick mitigation afterward: `texture/verification_01/restricted_mips_01/` under
  seat-01 contains only 2048/1024 maps plus explicit LOD 0–1 consumer policy.
  Ten PNGs decoded/hash-recorded. Not a configured runtime sampler; no lower-mip
  safety claim. Parent STOPPED, no Blender operations in this packaging pass.
- Actual seat verification subsequently completed in owned disposable processes:
  `.dev-shots/seat-01/texture/verification_01/VERDICT.md`. New candidate saved/reopened
  with exact indexed geometry/UV preservation and global layout PASS. Shader-channel
  p95 diagnostics pass at one whole-seat view; normal max 21.17 degrees remains.
  Conservative mip-footprint test finds foreign-chart risk from 512 downward;
  unrestricted mip-chain safety FAILED. No candidate promoted, old checkpoints untouched.
  Parent STOPPED; no live Blender access or real background operation remains.
- Subsequent tooling-only follow-up STOPPED: explicit UV packing/preserved-layout
  bake modes implemented and fixture-tested, including reopened saved output.
  Evidence: `.dev-shots/seat-01/tooling-tests/atlas_modes_04/`. Only owned disposable
  Blender processes ran/exited; live state unknown. Seat checkpoint unchanged.
- Tooling/documentation closeout completed after appearance work; no further Blender
  execution or asset changes. Current brief and HANDOFF reconciled; failed/superseded
  artifacts retained and labelled in `.dev-shots/seat-01/closeout-2026-10-26.md`.
- Parent direct ownership; STOPPED after procedural texture/bake review. No interactive Blender access in this pass.
- `.dev-shots/seat-01/checkpoints/seat_01_uv_08_baked_review.blend`: six visible baked parts, original meshes preserved but hidden in viewport/render, joined bake helper hidden. Previous uv_07 had originals and baked meshes simultaneously render-visible; its previews are superseded (z-fighting).
- Procedural source: `seat_01_uv_06.blend`; frozen UV source uv_05 unchanged. Textures: `.dev-shots/seat-01/texture/bake_01/textures/` (2048 basecolor, roughness, metallic, tangent normal and ORM).
- Inspected corrected whole/surface previews: `.dev-shots/seat-01/texture/bake_01/isolated_review_01/uv08_whole.png`, `uv08_surface.png`; capture metadata alongside. Basic dark fabric/noise grain, vinyl piping, steel rails. No texture-generation model/service used.
- Verification limit: bake report's `uv_layer_preserved` checks bounds only, NOT exact corner mapping; no quantitative texture transfer or mip-bleed certification. Bake margin 12 px exceeds half the 9 px gap, so dilation collision risk remains unverified. No export/integration or final acceptance claimed.

## Historical UV checkpoint summary — superseded as current state

- **Owner:** none; parent took direct ownership at user request and is now STOPPED (2026-10-26). No further delegation.
- **Authoritative UV checkpoint:** `.dev-shots/seat-01/checkpoints/seat_01_uv_05.blend`, SHA256 `ade85271f0498db366c47ef0271b6d0a12ef3cc3fc28bb9adb831ddebe756bba`.
- **Scope/result:** approved repack-only utilisation pass; 46.681% coverage, 188 islands, global bounding-box gap 9 px at 2048, zero global triangle overlaps, smallest island 6.120 px². Saved file reopened and checked. Geometry/material-slot/transform fingerprints unchanged from uv_04. No unwrap or mesh edits.
- **Baseline preserved:** uv_04 SHA256 `d7ca03ded5275c1bb31395a57875abe06a4e242cd0b482b3c2f81ffacbf4f09b`.
- **Live Blender:** not queried or driven in this pass; actual interactive filepath/dirty state unknown. All work used completed disposable background processes.
- **Evidence:** `.dev-shots/seat-01/uv_repack/owned_01/verify_report.json` and `seat_01_uv_05_layout.png` (inspected). Ten packing tests pass. No baking/export/integration or user acceptance claimed. Next boundary: user review.

## Historical state — superseded 2026-10-26

- **Owner:** none; all assigned workers STOPPED. Parent performed read-only inspection
  for this cleanup on 2026-10-25 at approximately 21:26 local time.
- **Live/checkpoint:** `.dev-shots/seat-01/checkpoints/seat_01_junction_candidate_03.blend`,
  clean, 18 objects (6 meshes, 12 cameras), 0 modifiers, OBJECT mode; SHA256
  `4ac614fe39b7aa450ebdbaa9a4852631c06c2e219925684cb33a9c05621b896b`.
  Contains the reviewed junction fix (candidate_02) plus the reviewed shorter/wider base
  (base_01 pilot adopted unchanged). Not saved over by the parent. Reinspect before use.
- **Preserved earlier checkpoints:** intake `seat_01_junction_intake_01.blend`
  (`a2512545…bd93f`, original user state), `seat_01_junction_candidate_02.blend`
  (`dcaac190…df87`, junction only). Both bytes unchanged.
- **Active asset:** standalone `seat-01`, Stage 2b; R1 withdrawn at the squab/backrest
  interface, repair #4 OPEN. Current agreement/history/evidence: [seat brief](../../.dev-shots/seat-01/brief.md).
- **Latest shape decision:** disposable shoulder-lift `pilot_03` was NOT integrated:
  corner steps improved but a new outer-shoulder ridge regressed the visible form.
  [Parent review](../../.dev-shots/seat-01/evidence/junction_candidate_01_pilot_03_after/parent_review.md).
  Preserve that failed candidate and the prior repair/ceiling-stop history.
- **Cameras:** saved `cam_05`/`cam_06` do not frame the junction. Use the recorded
  temporary-view metadata, not camera names, when planning a matched comparison.
  A surface-directed ray map did not prove the seam closed.
- **Constraints:** text-only stylised seat authority, separate squab, full required
  features; occupant 1.7–1.8 m and rail pitch 400 mm are scale anchors. Overall
  dimensions remain provisional. Parent working cap 21k triangles / squab pair 8,600;
  user's approximate 25k budget unchanged. No geometry progression is implied here.
- **Tooling:** fresh synthetic workflow trial02 finished with 9/12 runner operations
  and no rescue. This is not seat acceptance. [Current worker path](../review-session-workflow.md).
  Agent model-turn ceiling and runner-operation budget are different units.
- **Environment:** Windows Blender 5.2.3 LTS, explicitly supplied executable
  `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`; MCP summary calls worked
  at inspection. Do not reinstall/reconfigure the addon from historical protocol notes.
- **Next boundary:** current request is instruction/record/script cleanup only.
  Seat repair remains stopped; UV/detail/export/integration are not advanced by it.

## Truck (parked, not current authorization)

- **Last delivery:** `round68/out_01/truck_livery_baked_01.glb` (SHA
  `12f1205b…c82fbaf`, 9.75 MB), re-import verified in Blender. Godot import deferred
  by the user; no engine-side evidence exists.
- **Editable master:** `.dev-shots/car_img2-01/gate1-ultrafast-01/truck_materials_windows_02.blend`
  (SHA `ea191e71…f043f6`), unchanged.
- **Provenance flag:** the UV candidate
  `round66/pilot_body09/truck_uv_candidate_body09.blend` was **re-saved by the user at
  13:42** (5,719,891 → 5,683,395 bytes; SHA now `d69d0367…a277ae`). The round66 UV
  measurements, the guide `uv_sha256`, and the round68 bake were produced from the
  earlier byte state. Treat their correspondence to the current file as **unverified**
  until re-checked. No recorded hash for the candidate itself was contradicted.
- Truck livery limits remain as documented: stripe breaks at island borders, roof
  unstriped, 2048 PNG textures, no LOD/collision/performance data, no user acceptance.

## Historical record — not current authorization

- Full pre-cleanup ownership card: `.dev-shots/workflow-cleanup-03/source-before/BLENDER_OWNER.md`
  (byte-preserved local archive). It contains the obsolete stage2b_02 filepath/hash,
  old camera claims and the seven historical modeller ceiling stops; not a live card.

- Earlier ownership cards and the watering-can handoff are archived under
  `docs/legacy/`. They include superseded assets, approvals and restrictions; do not
  resume those tasks from the archive.

Replace this card at each handoff; keep asset evidence/history in the brief's linked
records, not a growing stack of ownership cards. One live owner globally, including
parent inspection; follow AGENTS.md for handoff and timeout reconciliation.
