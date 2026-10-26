# Migration status — historical copy record (2026-10-23/25)

> **Archival, not current state.** This records how the authoring tools/skill were copied
> out of GummyBearTest and the portability checks of that phase. Current live ownership is
> the current card in `BLENDER_OWNER.md`; current execution policy is
> `docs/execution-modes.md`; evidence mechanics are in
> `docs/review-session-workflow.md`. The seat work and watering-can paths below describe
> that migration moment, not current authorization.

Source: GummyBearTest HEAD `39cb88a7e91ef2c7c28d8a6d3cf07e5b9fcabbbc`,
with unrelated local game/doc changes preserved. Copy-only migration; no commit,
deletion, LFS or dependency installation approved/executed.

Copied authoring skill, pipeline tools, three historical 3D topic docs, and ignored
`wateringcan_body_trial` / `deepseep_wateringcan` checkpoints/references. Python
caches and Finder metadata excluded. Original files remain authoritative recovery
sources. Historical jobs/scripts/checkpoints may contain absolute old paths.

Live Blender inspected clean on `wateringcan_body_modeller_trial_01b.blend`; scene
contains Body_Modeller01 and preserved wallDefect attempts. This means the
interrupted worker made changes; it does not establish successful completion or
acceptance. No scene edits or file opens were performed during migration.

## Remaining gates

- Confirm interrupted worker stopped before handoff; validate checkpoint dependencies
  and relocate references without reading/writing game sources during the cold run.
- Run standalone tools/tests and cold-start modeller stage; inspect saved evidence.
- Define/test versioned Gummy delivery manifest and game-side intake. Existing
  check_interface.py is a geometry-contact diagnostic, not an intake validator.
- Freeze legacy routes only after standalone verification. They are migration-only
  copies meanwhile, not independently maintained authoring branches.
- LFS/storage policy and migration of other asset histories remain deferred.

No standalone success or body approval is claimed by this inventory/copy step.

## Executed checks

- `python3 tools/asset-pipeline/fixtures/test_pipeline.py`: 12 tests passed
  from AssetWorkshop, without dependency installation.
- Checksum dry-run (`rsync -rcn`) over both copied watering-can work folders:
  no source/destination content differences reported (Finder metadata excluded).
- `git init`: independent repository initialized; no files staged or committed.

## UV extractor dependency migration

Copied `tools/uv-layout-extractor/` from the source workspace, preserving LICENSE,
UPSTREAM.md, documentation, examples, scripts and tests. Excluded CI configuration,
Python caches and Finder metadata. Existing local skill routes
`references/uv-layout-extractor.md`, `uv-template-delivery.md` and
`uv-island-export.md` already provide the relevant guidance; no duplicate skill added.
No dependency installation, geometry changes or live Blender operations performed.

Executed in AssetWorkshop:
- `python3 tools/uv-layout-extractor/tests/test_atlas_checks.py`: 5 tests passed.
- Disposable factory-startup Blender import of `audit_asset.load_helpers()`:
  all six helper modules loaded, including uv_core and uv_atlas_checks.
- Existing `tests/blender/run.sh` with explicit Blender executable and approved
  temporary directory: UV_LAYOUT_FIXTURE_PASS. Color/line output, name rebinding,
  clean gate and expected rejection cases passed automated checks. Temporary
  outputs were cleaned by the runner; visual output quality was not reviewed.

Preview/browser dependencies and active external image paths remain separate
unresolved gates. This migration does not establish overall standalone readiness.

## Standalone verification run (2026-10-23)

User confirmed the interrupted modeller stopped and approved dependency-only
checkpoint preparation plus one verification-only body pass. Fresh inspection
found Blender already on the local copied source, saved and clean. No old game
repository was read. Created `modeller_trial_01/standalone_verify_01/` under the
copied watering-can work folder; original source remains untouched.

`wateringcan_standalone_relinked_01.blend` relinks six existing local images with
relative paths. Its dependency inventory records source SHA-256 and unchanged
mesh-coordinate/topology/transform hashes. No libraries were present in this
actual local source. Render Result and Viewer Node are non-file image entries,
not missing external dependencies. Earlier live-scene findings do not describe
this newer inspected local state.

Fresh executed checks: pipeline fixtures (12), UV atlas checks (5), reference
sheet tests (15), construction gate, Blender mesh diagnostics, capture-review
(including evidence rejection controls), and all six audit helper imports passed.
`test_asset_capture.py` first failed because its scratch parent did not exist;
the fixture now creates that directory, and its rerun passed, including failure
restoration/orientation controls. These checks do not approve body likeness.

Browser preview still imports absent `scripts/browser-harness.mjs`; the historical
`launch.py` example is unavailable. Preview/export delivery and intake gates are
not verified. No installations, project-asset exports, commits or pushes occurred.
Delegated body verification and independent saved-evidence review subsequently
completed; see results below. Neither grants user acceptance.

Additional fresh checks passed: pure document unittest discovery (14), both audit
Blender fixture phases (1a/1b), and reference-sheet Blender fixtures (4). The audit
fixtures intentionally include missing-image and bad-geometry negative controls;
their printed findings are expected assertions, not asset findings. Parent viewed
the new synthetic capture fixture's front, side and wire PNGs: asymmetric objects
are visible with different front/side projections; wire is faint but visible.
All 77 scanned local Markdown link targets exist. Prose paths/imports are outside
that link check. `git diff --check` has no tracked diff to check in this still-
untracked workspace; it is not substantive whitespace evidence for these files.

Static JS-import inspection additionally found absent `scripts/glb-inventory.mjs`
in the verification coordinator, Phase 2 tests and historical manifest helpers.
The coordinator imports preview statically, so `--skip-preview` does not make it
available. This is reported separately from the functioning body-verification
path; no JS delivery success is claimed. Python syntax parsing passed for all
125 pipeline/extractor Python files without importing them or writing caches.

## Final bounded review

Modeller stopped explicitly after 12 live calls. Parent then independently opened
the original local source, relinked baseline and `wateringcan_standalone_verified_01.blend`
in disposable Blender, without saving any of them. Parent's `parent_review.py` and
`parent_saved_review.json` are retained beside the checkpoints. Original inventory
hash serialization matches all 12 meshes in all three files, resolving the worker's
reported hash-comparison blocker. Independent expanded coordinate/edge/face/UV/
transform hashes also agree. All ten saved capture hashes match the manifest and
parent inspected all ten images. Source SHA-256 remains
`1c1fc0607496f269c6128b6f6b4504f04feda0da8344d5e1f9fd72de21e79221`.
Verified checkpoint SHA-256:
`6b8c044046365b28845de5bdfba3c91ac59e6d56b83b51ddc6773bd98f0364f6`.

Parent confirms 180.000 mm maximum OD, 298.000 mm height, 80.000 mm throat
diameter (84 mm outer lip diameter); the 42-segment section is faceted, not an exact
circle. Worker measured normal shell offsets 1.932–2.000 mm; this is sampled
nominal-wall evidence, not exhaustive minimum-thickness/self-intersection proof.
Worker health diagnostics report one closed island and no listed manifold,
degenerate, winding or loose-vertex defects. Profile and historical defect attempts
are retained, but body modifiers are absent: profile edits do not regenerate body.
Embedded construction scripts retain historical output paths; no claim of a
portable parametric rebuild is made.

Saved checkpoint has three file-backed reference images, all relative and existing
locally, plus two non-file viewer images and no libraries. Three zero-user crop
images from live inventory are not persisted in the save (Blender orphan handling).
Worker also disclosed reloading the clean baseline to discard capture churn,
including three zero-user live-only temporary materials; no saved source material
or geometry deletion was found. This cleanup is disclosed, not treated as an
authorization for future deletions.

Reference-plane calibration failed: planes have inconsistent orientation and
non-uniform scale. Worker made uniformly scaled 2D comparisons instead, documented
as approximate perspective/likeness guides, not measurement certification. Parent
observes mismatched shoulder/base outlines and opening registration; the 3/4 body
is visibly narrower than the drawing through much of its contour. Exact shape
failure versus perspective/registration cannot be settled from these comparisons.
No geometry repair or reference-plane repositioning was performed.

Status: standalone instructions/tool execution/delegation PASS for this bounded
body pass; current checkpoint dependency portability PASS, portable procedural
rebuild UNVERIFIED; numeric geometry checks PASS with faceting/sampling limits,
live editable construction FAIL; likeness UNVERIFIED; evidence file integrity PASS,
calibrated likeness evidence FAIL. Browser/GLB verification routes remain unavailable
as documented, and delivery-contract/intake validation remains deferred.

Live Blender is clean on the relinked baseline, not the verified copy. No worker
remains authorized. No further repair, export or integration is authorized by this
result. Legacy workflow removal is not established safe for every historical route.

## Whole-pipeline file migration completion

User requested completion of pipeline migration, deferring functional checks.
See `docs/pipeline-migration-inventory.md` for route mapping and exclusions.
Added the omitted ComfyUI operating doc, local browser harness and GLB inventory,
and a game-independent localhost preview launcher. Preserved legacy technical and
species documentation under `docs/legacy/`, not as startup instructions. Copied
missing tool/skill files only; existing AssetWorkshop repairs were not overwritten.

Read-only file coverage check: all 320 source tool/skill files present locally
(excluding caches, Finder metadata and CI). Relative JS import scan across local
tools/scripts reports no missing files. These are migration coverage checks, not
runtime, rendering, ComfyUI or export validation. No live Blender access, model
changes, dependency installs, CI changes, source deletions or commits performed.
Other asset histories remain preserved at source, not claimed migrated. Destination
contract versioning/intake and final game-side workflow cleanup remain separate.

## Expanded migration review (offline)

Reviewed actual local inventory and added copies without reading GummyBearTest or
touching Blender. Earlier missing browser harness, GLB inventory and standalone
launcher blockers are resolved. Fresh execution:

- StableMaterials runner: 7 offline tests passed; real deskfan-v4 job dry-run
  produced three material graph candidates, zero failures under
  `.dev-shots/migration-review-materials-01/`. No server contacted.
- Qwen runner: 11 offline tests passed; both the reusable and historical laptop
  API workflow graphs loaded and patched successfully with placeholder inputs.
- All seven material job template paths resolve locally. Historical laptop image
  inputs remain asset-specific examples, not newly migrated asset histories.
- Pipeline fixtures: 12 passed. JS Phase 2: 8 passed, 1 explicitly skipped because
  the pinned glTF validator is not provisioned. No package downloaded/installed.
- Browser harness, GLB inventory and verification coordinator imported successfully;
  existing Brave executable resolved. No browser was launched.
- Standalone preview HTTP smoke test returned 200 with HTML; owned server stopped.
  Initial test using `--port 0` failed because launcher prints 0 instead of the
  allocated port; retry with an explicit free port passed. Port-0 URL reporting
  remains a minor known launcher issue, not a missing migration dependency.
- Scanned 77 local Markdown links and relative imports in 18 JS files: no missing
  targets; 175 Python files parsed successfully. These are static checks, not full
  runtime proof. Handbook line 725 retains a stale prose path to
  `docs/agent-procedures.md`; archival content is at `docs/legacy/agent-procedures.md`.
  Current AGENTS.md remains active repair policy; no skill instructions changed.

Migration verdict: PASS for relocation of the authoring tool/instruction routes
listed in `pipeline-migration-inventory.md`, supported by that inventory's recorded
320-file coverage check and fresh local dependency/execution checks. This review
does not independently recount source files in the old repository. Model likeness
and live parametric editing are not migration acceptance gates. Green flag applies
to removal of those migrated legacy authoring routes in a separately approved
source-repository cleanup, NOT deletion of uncopied asset histories, game runtime,
destination contracts/intake validators or shared global MCP/config/credentials.
No legacy deletions performed here. Keep recovery copies/backups for source history.

Live ComfyUI generation (explicitly skipped by user), material quality/bake visual
acceptance, browser WebGL rendering, pinned-validator execution and destination
delivery/intake validation remain UNVERIFIED. These functional acceptance gates
are distinct from relocation completeness and do not imply missing tool files.

## Pinned validator prerequisite resolved

User approved provisioning the exact migrated pin with the documented local
installation method. Executed `node tools/asset-pipeline/scripts/provision_validator.mjs`:
`gltf-validator@2.0.0-dev.3.10` was downloaded with `npm pack`, the pinned tarball
SHA-1 `9b09225db864fe3f0a584259f65d087e2213a93a` verified, and the package extracted
to `.dev-shots/asset-pipeline/validator/gltf-validator-2.0.0-dev.3.10/`.
The adapter independently loaded it as ready and reported version
`2.0.0-dev.3.10`. `node --test tools/asset-pipeline/tests/phase2.test.mjs` passed
all 9 tests, with zero failures and zero skips (including the validator smoke test).
No dependency upgrades or global configuration changes were made.

This supersedes earlier statements that the validator is unprovisioned or its
smoke execution unverified. The provisioning prerequisite is closed; no further
validator setup is needed. Full GLB asset delivery, destination contract/intake
and browser rendering remain separate unfinished checks. Live ComfyUI testing
remains deferred; no ComfyUI service was contacted.

## Historical-job disposition and delivery contract status

User confirmed GummyBearTest as destination and approved auditing jobs/local
delivery preparation. No game-repository reads are authorized or made.
The former requirement to secure a requirements handoff before manifest work was
withdrawn on 2026-10-23: the destination contract is deferred until working assets
exist and is not a project blocker. Requirements must still come from the
destination when that work starts; they are not to be invented.

- Added read-only `tools/asset-pipeline/scripts/audit_historical_jobs.py` and four
  synthetic tests. The audit prints original SHA-256s and path dispositions without
  writing jobs, opening Blender or probing external files. Initial fixture failures
  exposed relative/macOS symlink path normalization; normalizing the job path fixed
  them. Final four tests pass; existing 12 pipeline fixtures also pass.
- Audited all 33 top-level pipeline jobs: 31 archival-blocked by absent declared
  source files, two archival-requires-explicit-scene (source omitted). Their exact
  names/disposition rule and missing deskfan map inputs are documented in
  `tools/asset-pipeline/jobs/README.md`. No corresponding source was available at
  the declared local paths; no substitute asset or fabricated runnable copy made.
  Original jobs are unchanged. Nested scratch outputs are not job specifications
  and were not used as substitutes for missing original sources.
- Seven material examples retain existing local templates; the historical laptop
  Qwen example lacks both declared reference images. No material generation run.
- Prepared `contracts/gummy/README.md` with the requirements checklist (schema/
  example, package boundary, runtime conventions/budgets, acceptance policy, intake
  procedure). No versioned manifest schema or destination package validator is
  implemented; that work is now deferred until working assets exist. Existing
  reusable local validator tests rerun: 9 passed, zero skips.
- Live ComfyUI testing explicitly **DEFERRED** in operating notes and inventory.
  Local validation does not establish destination compatibility; actual intake must
  be tested separately in GummyBearTest when delivery work is approved.

Completed: job audit/dispositions, local audit tooling/tests and requirements
checklist. Open item limited to corrected job copies for absent asset sources.
Deferred by user decision: destination contract/intake (until working assets),
live ComfyUI and game-side intake. No model edits, integration, dependencies,
deletions, commits or pushes.
