# Workflow cleanup audit — instructions, records, scripts

Date: 2026-10-25. Scope: documentation/record consolidation and one shared-capture
extraction. **No modelling, UV, bake, export or destination integration.** No live
scene was edited, reloaded or saved. Original files replaced by this pass are preserved
byte-identically in `.dev-shots/workflow-cleanup-03/source-before/`.

## 1. Instruction overlap — what was authoritative and what changed

| Question | Single authority | Consolidated/retired here |
| --- | --- | --- |
| Permissions, preservation, ownership, one-Blender rule | `AGENTS.md` | Unchanged. |
| Current asset/live identity | `BLENDER_OWNER.md` | Rewritten to the actual saved intake, current repair state and observation time; old card archived. |
| Session orientation / "what next" | `HANDOFF.md` | Was truck-only and contradicted the active seat work; now routes to the seat and states cleanup is the active task. |
| Asset scope, features, gates, history | `.dev-shots/seat-01/brief.md` | Current-state preamble replaced; old stage2b_02 card retained verbatim under an explicitly historical heading. `rounds.json` stale protocol note moved to a labelled historical field. |
| Review levels, progression, evidence reserve | skill `references/stage-review.md` | Unchanged; other documents defer to it. |
| Execution/evidence mechanics | `docs/review-session-workflow.md` | Extended with the current fixed worker path; old low-level CLI section kept historical. |
| Reusable construction starting points | skill `references/asset-workflows.md` | Second "shape gate"/approval ceremony and duplicate MCP add-on version claims removed; examples now point at current commands rather than `/Applications/...` and duplicated gate instructions. |

Deliberate non-actions: no safety rule was relaxed, no user approval was inferred, no
historical failure was deleted, and no agent permission was widened. The trial-scoped
`.blend/.json/.png/.html` shell-resource allowances added during permission diagnosis are
absent from `.opencode/agents/modeller.md`; its unmatched-shell rule is still `deny`.

Remaining overlap, kept on purpose: `AGENTS.md` and `stage-review.md` both restate
budgets/repairs — `AGENTS.md` owns safety, `stage-review.md` owns progression, so the short
restatement was left rather than duplicated in a third place. `authoring-handbook.md`
remains a large on-demand index; it was **not** rewritten, and its sections are still the
route targets listed in `SKILL.md`.

Also corrected: `docs/exposure-check-stage.md` had claimed the cam_05 blocker map showed
the seat junction "reads closed". The helper samples target surfaces and never aims
through the seam, so that claim was withdrawn in place and the seam question marked open.

Second pass (same session) covered the surfaces the first pass deliberately skipped:

- `authoring-handbook.md`: removed the stale "add-on 1.8 / protocol-14" MCP claim (now
  version-neutral: inspect the installed schema) and replaced the duplicated four-view
  "shape gate + approval revalidation" paragraph with a pointer to `stage-review.md`,
  keeping the substantive requirements (feature presence, views that contain the question,
  overlays only where calibrated).
- `docs/migration.md` and `docs/pipeline-migration-inventory.md`: prominent archival
  banners; the watering-can row is no longer labelled "current"; "GummyBearTest is the
  confirmed destination" is now scoped to the migration phase that created this workspace.
- `docs/legacy/*`: one-line archival banner on each of the four files so a search cannot
  mistake an old ownership card, agent procedure, handoff or game template for current
  instruction. Content otherwise unchanged.

## 2. Records reconciliation

- `BLENDER_OWNER.md` pointed at `stage2b_02.blend` (`246f8270…`) as live. The actual saved
  file at cleanup was `seat_01_junction_intake_01.blend` (`a2512545…`). Corrected, with
  the earlier measured geometry-equality finding retained.
- The owner card's "seven ceiling stops, most recently with nothing saved" is true
  historically but misleading as current state. Now recorded as carried repair history,
  with the rejected pilot and the unspent live deformation batch stated explicitly.
- The card's route decision ("user chose unified shell", "being re-checked") was ambiguous
  about what is authorized now. Replaced by: the latest bounded squab correction was the
  actual scope; unified shell is not implied.
- `HANDOFF.md` described a truck material preview as "next approved asset work". True for
  the truck phase, false for the seat. Truck material/UV/export guidance remains in
  `docs/authoring-operations.md` and the parked owner-card section, not as the active next
  action.
- The seat brief declared repair #3 in progress and did not mention the later repair #4
  pilot rejection. Corrected without deleting the earlier text.
- `rounds.json` `working_mode` claimed a protocol 14/15 handshake failure. MCP summaries
  worked in later passes; the note is now labelled historical rather than current.

Unresolved by design: no independent proof exists that the *user's* viewport framing change
from the intake session was reproduced; only that no camera object or mesh transform
differed. That limitation stays in the intake note.

## 3. Script consolidation

New shared entry point: **`capture_fixed(...)` in
`tools/asset-pipeline/scripts/capture_review.py`**. It captures from an already-loaded
saved checkpoint using either an untouched existing camera or an explicit world-matrix /
projection specification, optional recorded Workbench and colour-management values, two
new output paths, and a caller-supplied renderer. It restores scene state in `finally`,
removes its temporary camera and data, refuses overwrite/path collision, verifies the
checkpoint bytes did not change, and writes the matched-sheet metadata contract.

Consumer updated: `review_blender.py` now delegates its capture stage to `capture_fixed`
instead of keeping its own camera/metadata/restore copy.

Retained as historical, not deleted or rewritten in substance:

- `.dev-shots/seat-01/scripts/` (22 files): per-stage builders and renderers with
  hard-coded paths and superseded framing. A disposition table was added at
  `scripts/README.md`; `build_stage2b_03.py` remains marked DO-NOT-RUN.
- `.dev-shots/review-workflow-trial-01/scripts/`: rescued-trial wrappers. A replacement map
  was added; the trial's inconsistent step accounting is not rewritten.

Not consolidated, and why: the seat render scripts each encode different view sets,
resolutions and one-off framing. Folding them into one configurable script during a
cleanup pass would create an unvalidated generalisation and risk making historical
captures look reproducible when they are not. Only framing-independent mechanics were
shared.

## 4. Verification performed

- Pure runner/ledger tests: **29 passed** (`test_review_session.py`,
  `test_review_runner.py`).
- Blender regression on a saved disposable fixture (`fixtures/check_fixed_capture.py`, run
  against `review-workflow-trial-02/before.blend`): passed explicit-camera restore,
  existing-camera-unchanged, custom shading restore, injected-failure restore,
  no-overwrite, temporary data cleanup and source-bytes unchanged. Output:
  `.dev-shots/workflow-cleanup-03/fixed-capture-test-02/`.
- Existing suites re-run unchanged: `tests/phase7/test_capture_review.py` **pass**,
  `tests/phase7/test_asset_capture.py` **pass**.
- Refactored consumer re-run directly on the saved fixture
  (`.dev-shots/workflow-cleanup-03/review-blender-refactor/`): `review_blender.py check`
  passed and its `capture` stage rendered through `capture_fixed` with the expected
  ORTHO framing (ortho_scale 1.5, 900×800) and contract-shaped metadata.
- Live seat re-inspected read-only: same filepath, `is_dirty: false`, 18 objects,
  `EDIT_MESH` with empty selection; no scene edit or save.
- Source/archive hashes compared for every file copied to `source-before/`.

## 5. Known limits

- This is a documentation/tooling audit by the same assistant that wrote much of the
  material; it is not independent review.
- "Overlap retired" means the duplicate instruction was removed from the active path; the
  archived copies still contain the old wording.
- The shared capture helper was tested on one synthetic saved panel plus restored-state
  assertions, not on the seat's real camera rig. No new seat captures were produced, so the
  historical junction images remain the only seat evidence and carry their stated limits.
- Links were checked mechanically; the HTML sheet layout was not re-reviewed in a browser.
- Second-pass surfaces (`authoring-handbook.md`, `migration.md`,
  `pipeline-migration-inventory.md`, `docs/legacy/*`) were treated as wording/routing
  hazards only: every link there was rechecked (**70 links, 0 missing**) and the four
  legacy files plus both migration documents now carry an archival banner. Their technical
  claims were not re-validated against Blender or the game repository.
- Integration check: a scratch legacy ledger
  (`.dev-shots/workflow-cleanup-03/ledger-integration/`) accepted the `capture_fixed`
  metadata as a capture event (checkpoint → passing check → capture), confirming the
  shared helper's metadata still satisfies the matched-sheet contract. That ledger is a
  verification artifact, not asset evidence.
