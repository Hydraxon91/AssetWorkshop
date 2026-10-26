# Live Blender ownership

Project: `C:/Users/Hydra/Documents/GitHub/AssetWorkshop`.
Coordination record, not a technical lock or permission to drive Blender.

## Current state

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
  interface, repair #4 OPEN. Current agreement/history/evidence: [seat brief](.dev-shots/seat-01/brief.md).
- **Latest shape decision:** disposable shoulder-lift `pilot_03` was NOT integrated:
  corner steps improved but a new outer-shoulder ridge regressed the visible form.
  [Parent review](.dev-shots/seat-01/evidence/junction_candidate_01_pilot_03_after/parent_review.md).
  Preserve that failed candidate and the prior repair/ceiling-stop history.
- **Cameras:** saved `cam_05`/`cam_06` do not frame the junction. Use the recorded
  temporary-view metadata, not camera names, when planning a matched comparison.
  A surface-directed ray map did not prove the seam closed.
- **Constraints:** text-only stylised seat authority, separate squab, full required
  features; occupant 1.7–1.8 m and rail pitch 400 mm are scale anchors. Overall
  dimensions remain provisional. Parent working cap 21k triangles / squab pair 8,600;
  user's approximate 25k budget unchanged. No geometry progression is implied here.
- **Tooling:** fresh synthetic workflow trial02 finished with 9/12 runner operations
  and no rescue. This is not seat acceptance. [Current worker path](docs/review-session-workflow.md).
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
