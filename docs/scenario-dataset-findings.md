# Scenario dataset evaluation — findings ledger

## Scope and current state

Dataset: `scenario-labs/3d-collection`, revision
`55b4c002b4c1529fc48da3dff98516c3069bfa3f`. License: CC BY 4.0, credit Scenario.
Evaluation is inspection-only; recommendations do not authorize repairs, tool
implementation, instruction changes, material generation or destination integration.
User approved a 5,000,000,000-byte aggregate download cap and broadened research
to editing, efficiency, Frutiger Aero, vehicles/RC relevance, houses and household
objects. ComfyUI is unavailable on the user's powered-off other PC: do not contact it.

Parent owns this ledger. Record new actionable findings during each bounded
review, not only in the final report. Workers provide candidate findings in their
owned artifacts; parent verifies and incorporates them here. Preserve uncertainty
and distinguish observed defects from untested improvement proposals.

Original ten outputs acquired; three-helmet normalized pilot independently reviewed.
Remaining seven technical counts and payload hashes independently checked; broader
visual/reference verification is incomplete. Validated payload subtotal before
expanded acquisition: **213,942,842 bytes**. Expanded acquisition added
**585,188,769 payload bytes** (43 files), independently verified against pinned
hashes/sizes. The conservative cumulative transfer ledger including recorded
metadata is **799,174,257 bytes**. Native/edit technical inspection and the bounded
visual pass are complete, with unresolved criteria recorded below;
this is not a live transfer counter or final sample total.

## Findings

### F01 — Compare raw source, imported baseline and round trip separately

- **Evidence:** Tripo helmet has 499,519 source indexed triangles, including 23
  repeated-index triangles; Blender imports 499,496. Subsequent round trip has
  zero triangle delta relative to the imported baseline, not the source.
- **Independent review:** parent decoded source indices and reproduced source and
  imported counts. This explains degenerate primitive loss, not lost visible area.
- **Proposed helper change:** report all three baselines, repeated-index and
  near-zero-area primitives, and unexplained deltas separately. Add regression fixture.
- **Status:** confirmed finding; proposed tool change not implemented.
- **Artifacts:** `.dev-shots/scenario-eval/helmet-pilot-01/parent_verification_01.json`,
  `diagnostics_01.json`, `parent_review_01.md` in that directory.

### F02 — Validate embedded image signatures, not just loader success

- **Evidence:** Direct3D S2 helmet image data URI declares PNG but contains JPEG
  bytes. Parent independently decoded the payload and checked its signature.
- **Proposed helper change:** check bufferView and data-URI images for declared
  versus detected type; report external dependencies without silently fixing them.
- **Limits:** Blender loads it; behavior in other loaders has not been tested.
- **Status:** confirmed source inconsistency; validator addition not implemented.

### F03 — Dense wire overlays are unsuitable for likeness review

- **Evidence:** 40k-triangle helmet wire overlays obscure the reference. Final
  flat translucent silhouettes expose exterior mismatches much more readably;
  separate clay views show form and the visor region.
- **Proposed helper change:** provide reference-only, clay-only, flat-mask overlay
  and optional sparse-landmark modes with the same camera/pixel mapping. Keep
  wireframe as topology evidence, not the default likeness comparison.
- **Independent review:** parent inspected all three final overlays and a clay view,
  reopened checkpoints, checked mesh preservation and reference-plane projection.
- **Limits:** approximate orthographic pose is not recovered source perspective;
  these comparisons do not establish a numerical likeness ranking.
- **Status:** useful method demonstrated in scratch scripts; shared helper not changed.
- **Artifacts:** `.dev-shots/scenario-eval/helmet-pilot-01/normalized-review-02/`,
  `parent_saved_review_02.json` in the pilot root.

### F04 — Prove orientation and segmentation assumptions

- **Evidence:** Tripo's original `threequarter_ref` view faced image-right while
  the supplied reference faces image-left. A filename did not establish a match.
  An RGB threshold selected almost the entire colored reference rather than the
  helmet. Later inspection found transparency; the parent's initial assumption of
  an opaque background was also incorrect.
- **Proposed helper change:** record observed front/up/features, projected image
  directions and source alpha statistics; expose the segmentation mask/occupancy
  before accepting a computed subject box. Support explicitly provisional manual
  landmarks when automatic segmentation is unsuitable.
- **Status:** confirmed evaluation failures; general helper behavior not implemented.

### F05 — Separate seam connectivity from geometry defects

- **Evidence:** many raw boundary edges disappear after diagnostic positional
  welding. S2 has 172 welded components and no welded boundaries; this does not
  establish whether the shells are intentional or free of intersections.
- **Proposed helper change:** show raw and diagnostic-welded counts, tolerance and
  component sizes separately. Make clear that nonmanifold totals include boundaries.
  Never recommend destructive welding merely because UV/normal seams split vertices.
- **Independent review:** parent used object-identity graph traversal to reproduce
  pilot component counts, avoiding reliance on potentially stale BMesh indices.
- **Status:** confirmed reporting need; no source mesh altered or repair approved.

### F06 — Report geometry cost versus visible function, not just total triangles

- **Evidence:** biplanes have 95,156 and 484,050 source triangles; birds have
  10,582 and 90,066; barrel has 87,596. Parent independently verified raw counts.
  Appearance/pose differences prevent treating these as equal-quality benchmarks.
- **Proposed helper change:** per-part density report plus a human-reviewed detail
  allocation sheet: geometry for silhouette/openings/moving interfaces; normal/bump
  for shallow relief; basecolor/roughness/decal for paint, grain, wear and labels.
  Record viewing distance and motion requirements before setting reduction targets.
- **Limits:** savings and quality must be tested in separately approved edits.
  Normal maps, decals, cards and instancing have their own costs; displacement may
  increase evaluated geometry. Instancing does not inherently reduce drawn triangles.
- **Status:** efficiency concern substantiated; optimization recipes unvalidated.
- **Artifacts:** `.dev-shots/scenario-eval/original-seven-01/metrics.json`,
  `parent_verification_01.json`, `report_run_01.md`.

### F07 — Material/texture overhead needs its own budget

- **Evidence:** one native/GLB diving-helmet inspection reports 15 materials and
  39 images; the other has repeated high-cost viewport/hardware groups.
- **Proposed helper change:** inventory unique image bytes/dimensions/channels,
  reused images, material assignments and per-part evaluated geometry. Flag reuse,
  atlas or lower-detail hardware candidates without declaring them automatic wins.
- **Independent review:** parent checked payload hashes and raw triangle counts;
  detailed shader wiring, unique texture-memory cost and part costs remain worker
  findings pending independent verification.
- **Status:** candidate improvement supported by worker inventory; savings unverified.

### F08 — Add scoped preservation comparisons using real edit pairs

- **Evidence:** dataset includes explicit source/output associations for retexture,
  UV-only edits, canopy reduction, tracks, lid animation/interior and pot cutaway.
  Same source can have different requested edits, so hash grouping alone is not
  a matched generator trial.
- **Proposed helper change:** task-specific geometry/UV/transform/material/animation
  fingerprints and protected-part comparisons; reference the exact prompt and source.
- **Limits:** edit packages acquired and payload hashes independently verified.
  Requested behavior is not
  proof that the edited output succeeded; correspondences may require manual review.
- **Independent follow-up:** parent independently loaded source and edited native
  files using separate packed-array fingerprints: teapot retexture exact geometry,
  UVs and matrices; roof all 17 matched mesh objects exact geometry/matrices with
  only `Thatched roof` UVs changed; canopy 720→360 triangles with exact trunk;
  rover 22 old mesh objects exact geometry/UV, only studio-ground matrix changed.
  These establish technical preservation, not material quality, roof mapping quality,
  all-side canopy shading, track clearance or interior validity.
- **Status:** preservation fixture feasibility demonstrated for four tasks; shared
  regression helper implementation and visual/structural acceptance still pending.
- **Artifacts:** `.dev-shots/scenario-eval/parent-edit-task-records.json` distinguishes
  prior row observations from independently pinned file metadata.

### F09 — Treat generated material workflows as a separate, existing capability

- **Evidence:** `docs/comfyui-materials.md` documents existing StableMaterials/Qwen
  runners, API-format workflow requirements, map outputs, color drift, UV-normal
  requirements and historical results. User reports successful testing in the
  source project; live generation is not validated here and the PC is offline.
- **Proposed use:** evaluate these existing routes for reusable surface detail,
  rather than inventing a duplicate generator. Keep object-specific high-to-low
  baking distinct from tileable PBR generation; inspect map quality and color.
- **Status:** documentation located; no service contacted and no generation performed.

### F10 — Dataset outputs are fixtures, not a helper-code collection

- **Evidence:** pinned repository inventory has 3,699 files and no standalone
  `.py`, `.js`, `.ts`, `.sh` or `.ipynb` files. The two original diving-helmet
  native inspections report zero embedded text blocks and no mesh modifiers.
- **Limits:** embedded text/controls in every other native file remain uninspected.
  Output structure does not establish construction history or procedural editability.
- **Proposed helper change:** distinguish delivered geometry, editable objects,
  modifiers/node controls and embedded scripts in native-file inventories; never
  execute embedded scripts merely to inspect them.
- **Status:** repository-level absence checked; native-file conclusion limited to two.

  Follow-up worker inventory inspected 16 additional native files, reporting zero
  text blocks, mesh modifiers and drivers. This broader negative result is worker
  evidence, not a claim about every `.blend` in the dataset. Some outputs retain
  separate objects and material graphs, and the teapot lid has animation.

### F11 — Distinguish unique-mesh storage from instanced geometry totals

- **Evidence:** rover source GLB has 232,821 triangles across unique meshes and
  461,781 across mesh-bearing nodes; edited GLB has 298,997 versus 527,957.
  Parent independently reproduced these counts from source accessors and nodes.
- **Proposed helper change:** report both unique-mesh and instantiated totals,
  identify shared mesh users, and separately count active-scene reachable nodes
  before making rendering-cost claims. A raw all-nodes sum is not draw-call/GPU cost.
- **Status:** confirmed discrepancy between two useful metrics; production helper
  not changed. Full active-scene and visibility filtering remains unverified.
- **Artifacts:** `.dev-shots/scenario-eval/expanded-acquisition-01/parent_verification_01.json`,
  `raw-inventory_run02.json` and `manifest_run02.json`.

### F12 — Dispatch payload inspection by validated file type

- **Evidence:** expanded inspection mistakenly sent three reference PNGs to the
  GLB importer. These failures are explicitly recorded, not converted into passes.
- **Proposed helper change:** validate suffix/header before routing; separate model,
  image and metadata queues. An image-import error must not imply a missing model
  or invalidate completed checks of unrelated payloads.
- **Status:** confirmed diagnostic-script defect from worker report; production
  routing not changed. Images still require visual inspection in a later pass.
- **Artifacts:** `.dev-shots/scenario-eval/expanded-inspection-01/file_40.json`
  through `file_42.json`, `report.md`.

### F13 — Measure the requested part, not the entire asset

- **Evidence:** independent source/native checks show canopy 720→360 triangles
  (50%), trunk 197→197. Total tree 917→557 is a different denominator and must
  not be used to mark the requested canopy reduction failed.
- **Proposed helper change:** allow named region/object metric scopes and exact
  protected-part signatures alongside totals. Warn when semantic part identity is
  unresolved; don't infer it from arbitrary names alone.
- **Status:** independently reproduced; shape/shading retention remains unverified.
- **Artifacts:** `.dev-shots/scenario-eval/expanded-inspection-01/parent_task_verification_01.json`.

### F14 — Separate native preservation from export representation equality

- **Evidence:** native roof edit preserves geometry but changes roof UVs. Worker
  reports the GLB roof topology fingerprint differs with the same triangle count.
  UV seams and export reindexing can change representation; count equality alone
  also does not establish shape equality.
- **Proposed helper change:** preserve exact native fingerprints; for exported
  assets add correspondence-aware surface/attribute checks before diagnosing
  geometry damage from nonidentical arrays.
- **Status:** native result independently reproduced; GLB correspondence unresolved.

### F15 — Do not turn a reduction target into an appearance pass

- **Evidence:** parent inspected two opposed source/output canopy views. The 50%
  canopy reduction retains the broad crown arrangement but has larger facets and
  visibly different lobe contours. This is not identical silhouette/shading.
- **Proposed helper change:** separate count-target, protected-part, silhouette,
  shading and attachment statuses in optimization reports; retain matched views.
- **Status:** numerical success and visible differences independently observed;
  acceptable viewing-distance/quality thresholds remain a user decision.

### F16 — Functional edits need a cost delta and structural evidence together

- **Evidence:** parent inspected the raised lid/visible rim cavity, wheel-wrapping
  track bands and cactus cutaway with displaced section. These are stronger than
  object names alone. Lid edit grows from 120,116 to 780,494 triangles (~6.5×),
  while the cutaway grows from 34,572 to 146,748 (~4.2×).
- **Proposed helper change:** attach per-feature cost deltas to structural edits;
  report keyframe gap separately from full trajectory clearance and visible cavity
  separately from measured watertight interior/wall thickness. Added functionality
  must not silently waive efficiency or protected-exterior checks.
- **Limits:** no motion sweep, exact cut angle, wall continuity or geometric
  correspondence of the rebuilt lid-body/pot exterior was established.
- **Status:** visible cues independently observed; density costs verified in
  inventories; no optimization or full structural certification performed.

### F17 — Style/material labels need observed evidence

- **Evidence:** parent inspected both candidate grids. Rounded teal/yellow robots
  visibly support glossy consumer-design studies. The bottle is visibly opaque
  and its GLB lacks transmission/alpha-blend declarations. Car samples are generic
  vehicles, not demonstrated RC constructions. The bed's labelled plant is not
  visible in the inspected view; absence versus occlusion is unresolved.
- **Proposed helper change:** distinguish metadata intent, observed material cues,
  structural functionality and aesthetic acceptance in fixture tags; don't label
  an asset a glass or RC validation fixture from a keyword alone.
- **Status:** relevant visual cues independently reviewed, no full Frutiger Aero
  style acceptance or rig/mechanical-fit claim.
- **Artifacts for F15–F17:** `.dev-shots/scenario-eval/visual-evidence-01/report.md`,
  `image-index.json`, `views.json`, six task sheets and two candidate grids. Parent
  inspected all eight saved sheets; no further render batches were authorized.

## Completion and acceptance

### Subsequent approved implementation stage

The first helper stage is now implemented separately from the completed research:
see `docs/preservation-helper-stage.md` and the asset-pipeline README. Granular
authored snapshots, explicit per-part preservation policies and scoped cost reports
address subsets of F06–F08, F11 and F13. Independent source/edit trials and negative
probes pass, with 48 selected pure regressions plus a synthetic Blender fixture.
Material face assignments remain topology-dependent; runtime session IDs must be
excluded from authored shader hashes (caught and regression-tested in review).
Existing approval fingerprints/gates are unchanged. Raw GLB/MIME preflight,
surface-correspondence comparison and optimization are not implemented in this stage.

Parallel Verdant static research is recorded separately in
`docs/verdant-research-findings.md`. Its instancing/dilation/isolation lessons are
not dataset findings and are not evidence of defects in AssetWorkshop tools.
No add-on was installed or executed; licensing and runtime validation remain separate.

No shared pipeline tool implementation, optimization, material generation or
destination integration has been performed as part of this evaluation. Scratch
diagnostic scripts are not production helpers. Download validity, geometry health,
likeness, editability, efficiency and user acceptance remain separate conclusions.
Expand this ledger as new evidence arrives; final synthesis must state failed,
blocked and unverified criteria as well as successes.
