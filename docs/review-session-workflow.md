# Resumable review evidence

Execution-mode choice is in [`docs/execution-modes.md`](execution-modes.md). This
runner is the `scripted-disposable` path; it does not drive live Blender and its plans
must declare `execution_mode: scripted-disposable`.

## Bounded-task lessons — seat closeout 2026-10-26

- Announce a new outcome/scope before expanding a repair into tool development;
  agree a finite implementation/test batch and stop boundary. Failed tests call
  for a diagnosis, not weakening assertions or unbounded Blender retries.
- File-tool denial is not evidence that a user received a permission prompt.
  Return the exact denied scope. Do not bypass worker source-edit restrictions.
- Respect an explicit user handoff to direct parent ownership; a stopped worker
  does not retain ownership. No parallel Blender drivers.
- Claims must match tests: UV bounds equality is not mapping preservation;
  per-object overlaps are not global atlas checks; attractive renders do not
  prove bake transfer or mip safety. Record selected and superseded evidence.


## Current worker path

Use **`scripts/review_worker.py`** for a reviewed disposable stage plan. Do not make
each worker author save/check/capture wrappers or invoke Blender through shell strings.
The original `review_session.py` remains the low-level ledger/legacy inspection CLI.

Small executable preset, used for the fresh workflow trial:

```powershell
python tools/asset-pipeline/scripts/review_worker.py init --fixture-panel --manifest .dev-shots/NEW_TRIAL/session.json --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python tools/asset-pipeline/scripts/review_worker.py run --manifest .dev-shots/NEW_TRIAL/session.json --stage before_build
python tools/asset-pipeline/scripts/review_worker.py status --manifest .dev-shots/NEW_TRIAL/session.json
```

Run each returned `next` stage individually: `before_build`, `before_save`,
`before_check`, `before_capture`, `after_build`, `after_save`, `after_check`,
`after_capture`, `sheet`. At midpoint, a separate status invocation must resume at
`after_build`, not repeat the baseline. The fixed stages call shared health and
capture helpers, hash the main scripts and inputs/outputs, and register their own
checkpoint/check/capture events. A failing check never becomes a passing ledger entry.

The panel is a **synthetic fixture**, not a general modelling recipe. Generic plans
can be supplied with `init --plan PLAN.json --manifest NEW.json`; they must declare
`execution_mode: scripted-disposable` and name reviewed scripts, dependencies and outputs
before execution. The runner is **not a sandbox**: scripts can access the OS. Permissions
and an approved task remain required.
The main script and plan/executable hashes are checked; imported helper dependencies
are not an exhaustive captured software environment.

Capture bookkeeping: a capture-only plan still needs a recorded checkpoint for its
role; run a save stage or a continuation plan first. The capture metadata `view` must
match the plan evidence label exactly, otherwise the runner rejects the evidence.

### One budget, one unit

The current continuation in `budgets` is authoritative. Budgets count **runner
operations**, automatically, not model turns or worker-estimated steps. The preset
uses construction-stop 5 / deadline 12 for nine operations: construction at 1 and 5,
then final save/check/capture/sheet. `status` accepts no `--step` for these manifests.
The runner refuses construction in the reserve and any operation past its deadline.
Failed attempts count; a changed budget requires an explicit parent-approved
`review_session.py budget` command with continuation ID and reason. Budget history
and prior events remain intact. Low-level event recording cannot supply a step
different from the current operation count.

**Model-turn ceilings are separate.** The runner does not count or enforce model
turns, tool reads, deliberation or elapsed authoring time. Report those as unknown
unless actually measured. Never use a small operation count to claim an agent obeyed
its turn limit. Legacy manifests without budgets retain caller-reported step semantics
and are labelled accordingly; their inconsistent old trial numbers are not rewritten.

### Fixed execution and failure behavior

The host runner builds argv lists and uses `Popen` without a shell, starts only
background Blender, disables autoexec, and keeps construction, final checkpoint save,
checks and capture in separate stages. Working `.blend` snapshots cross disposable
process boundaries; there is no redundant baseline discovery or generic GUI session.
The runner owns and times each process (maximum 120 seconds), logs its PID/argv/exit,
and terminates only its own process tree on timeout/interruption. A failed/running
operation blocks continuation; inspect the partial state rather than rerun automatically.
No automatic rollback, delete, overwrite, alternate interpreter or shell fallback.
Manifest updates use same-directory atomic replacement after an observed earlier
service interruption; this still requires one writer.

Only the existing fixed Python CLI permissions (`review_worker.py`,
`primitive_recipe.py`, `blender-safe/run.py`) are needed for worker execution. The
trial01 `.blend/.json/.png/.html` shell-resource workarounds have been removed from the
modeller agent; its unmatched-shell rule remains DENY. Existing user-saved approvals
and unrelated permissions were not removed. Runtime verification is the fresh trial,
not a promise based solely on configuration text.

## Pass size — the fix for step-ceiling stops

Eight seat-junction passes stopped at the agent ceiling; later passes stopped after
inspection/numeric design without geometry. Oversized briefs and repeated setup were
observed problems; this does not isolate model efficiency or prove the ceiling was
the only cause. Parent supplies a ready operation and an early execution milestone,
or explicitly scopes development rather than consuming a modelling pass on setup.

Use **one bounded outcome per pass**, with required checks/save/evidence. Split
substantial design/development from execution when needed, not every command into
another planning session. Existing approved plans may cover a complete small result:

| Pass | Returns | Must not |
| --- | --- | --- |
| Design/decision | parameters, measurements, or a rejected candidate | commit geometry |
| Build (disposable) | saved pilot + scoped checks/evidence for supplied parameters | re-choose the approach or develop wrappers |
| Render/inspect | matched images of a saved candidate | change geometry |
| Apply (live) | saved new-name checkpoint + checks | explore alternatives |

**Apply adopts, it does not rebuild.** When a pilot is already a saved scene, applying it means
open the pilot, save under a new checkpoint name, verify, capture. Do not re-run the field
script against live state — the pilot *is* the artifact under review. Re-running invites a
different result from the one that was inspected.

**Worked example.** The seat junction pilot pass inherited the measurements and the rejected
variant, built one pilot, validated it and stopped inside its allowance. The apply pass then
only adopted that file. Keep briefs at this size: numbered steps, inherited facts stated as
facts, one artifact, explicit STOP condition.

Rules that make this work:
- Parent owns the decision; the worker executes it. A worker spending its budget
  choosing between variants is a mis-briefed pass.
- Inherited measurements, rejected variants and closed decisions are **facts**. Re-deriving
  them is waste and is now called out in the modeller prompt.
- If a pass cannot produce its one artifact within its allowance, that is a brief-size
  or setup signal: reduce scope or return the concrete blocker early. Do not simply
  raise the ceiling or create another preparation pass without resolving the cause.
- Record the artifact (parameters, pilot path, SHA) so the next pass resumes from it
  instead of repeating discovery.

This is a procedural convention with observed support (repeated ceiling stops on an
oversized brief). It is not evidence that small passes succeed; that needs the trial.

## Cleanup pass verification — fresh trial 02

`.dev-shots/review-workflow-trial-02/` completed on the fixed path: **9 of 12
operations, first attempts, no permission denials/timeouts/retries/parent rescue**.
Construction operations 1 and 5; final save/check/capture/sheet at 6–9. Separate
midpoint status returned `next: [after_build]` at used4; no baseline rerun.

Parent independently inspected both PNGs, verified all returned artifact hashes and
matched camera/shading/visibility metadata, and confirmed unchanged authored
signature/matrix/bounds with one unapplied bevel. Both health reports pass. See
`parent_verification.json` and `comparison.html` there. No owned trial PID remained
when parent enumerated processes; unrelated interactive Blender PID31032 was left
alone. No live Blender or seat access occurred.

This is one successful **synthetic fixed-plan trial**, not a complex-modelling success
rate. Model turns were not independently measured, and operation accounting is not
advertised as model-turn enforcement. Previous rescued trial01 stays historical.

Portable tests cover the runner's reserve/deadline rejection, explicit continuation
budgets, false step rejection, no overwrite/repeated stages, dependencies, changed
scripts/artifacts, failed processes, and owned-child timeout termination. Existing
authored preservation, retention, exposure and pipeline pure regressions also pass.

## Historical low-level interface and first trial

Implemented for the approved execution-loop improvement. This tool tracks work;
it does not construct geometry, launch processes, run checks or capture Blender.
Existing authoring, health and capture tools remain separate commands.

## Contract

`tools/asset-pipeline/scripts/review_session.py` is a stdlib-only CLI:

```powershell
python tools/asset-pipeline/scripts/review_session.py init --manifest .dev-shots/review-trial/session.json --goal "One visible junction correction" --construction-stop 12 --deadline 20 --views left right whole
python tools/asset-pipeline/scripts/review_session.py record --manifest .dev-shots/review-trial/session.json --kind checkpoint --role before --file PATH_TO_SAVED_BLEND --step 1
python tools/asset-pipeline/scripts/review_session.py record --manifest .dev-shots/review-trial/session.json --kind check --role before --file PATH_TO_CHECK_REPORT --step 2 --outcome pass
python tools/asset-pipeline/scripts/review_session.py record --manifest .dev-shots/review-trial/session.json --kind capture --role before --file PATH_TO_PNG --metadata PATH_TO_METADATA_JSON --view left --step 3
python tools/asset-pipeline/scripts/review_session.py status --manifest .dev-shots/review-trial/session.json --step 12
python tools/asset-pipeline/scripts/review_session.py sheet --manifest .dev-shots/review-trial/session.json --out .dev-shots/review-trial/comparison.html
```

Record each required view and both roles. The manifest is an explicitly mutable,
single-writer event ledger: keep it under ignored artifacts, never use an existing
unfamiliar file as the manifest. Initialization and sheet creation refuse overwrite.
Exit 0 means the requested bookkeeping operation succeeded, not shape acceptance;
exit 2 means invalid input or I/O. `status` prints remaining work.

Checkpoint, report, PNG and metadata bytes are SHA-256 linked. A replacement checkpoint
invalidates prior checks/captures for that role without erasing history. A failed latest
check blocks the sheet. Resume with `status`, not a fresh discovery pass. Do not rerun
construction merely because capture is missing.

Check outcome is explicitly supplied by the caller: the ledger does not parse or
independently validate arbitrary check-report contents. The capture producer must
declare correspondence to the saved checkpoint; hashes do not prove a render depicts it.

## Fixed capture metadata

Each capture supplies JSON with exactly these fields:

```json
{
  "checkpoint_sha256": "FULL_SAVED_BLEND_SHA256",
  "view": "left",
  "camera": {
    "matrix_world": [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],
    "type": "ORTHO", "lens": 50, "ortho_scale": 2
  },
  "resolution": [900,700],
  "shading": {"engine": "BLENDER_WORKBENCH", "settings": "RECORD_ACTUAL_SETTINGS"},
  "visibility": ["RECORD_ACTUAL_RENDERED_OBJECTS_AND_RELEVANT_FLAGS"]
}
```

This is a schema example, NOT calibrated camera data. Record actual evaluated camera
matrix, projection settings (including shifts/sensor/clip if relevant), render resolution,
shading/world/color-management settings and visibility from the capture run. The producer
must restore temporary scene state. Before and after metadata must match exactly except
checkpoint SHA. Legacy evidence with missing metadata is unverified: do not invent it.

The output is a local HTML comparison sheet, with view labels and before/after checkpoint
hashes, using original image files (no Pillow/browser dependency). It is not a portable
archive: keep linked artifacts at their paths and regenerate after any change. Visual
inspection still decides whether the correct feature is framed. A camera name is not proof.

## Evidence reserve and handoff

Agree construction-stop and final deadline within the worker's actual ceiling before work.
Example 12/20 is illustrative, not a new universal cap. At construction-stop, stop geometry
and finish checks, save, capture and handoff; do not spend the reserve on a new repair.
At deadline, return STOPPED with the manifest's pending work and explicit blockers.
The CLI reports phase from a caller-reported step count; it cannot enforce agent budgets,
stop Blender, cancel a timed-out tool or authorize a retry. Existing safety gates remain.

Resume handoff: manifest path + live owner/stopped state + checkpoint/live differences +
one next pending command + any permission/timeout blocker. Permission denial is not a
resume instruction to try another tool or interpreter.

## Verification and trial limits

`python tools/asset-pipeline/fixtures/test_review_session.py`: pure synthetic fixtures test
resume, reserve phases, replacement/stale artifacts, failed checks, metadata mismatch,
missing files, no-overwrite and cross-process CLI continuation/sheet generation.
Synthetic artifacts are explicitly not Blender health or capture evidence.

Implementation verification: **13 tests passed**, including a resumed CLI subprocess
that sees only pending after-evidence, generates the matched sheet, and refuses to
overwrite it. Existing retention (20), authored preservation (12), and exposure (17)
pure regressions also passed. No dependencies were installed and Blender was not driven.

This validates bookkeeping and sheet generation, not improved modeller completion rate.
A fresh bounded modelling trial remains the behavioral test: report whether checked images
and a stopped handoff arrived within budget, whether parent rescue was needed, and whether
the inspected visible outcome improved. No seat edits or new modelling trial were performed
by this tooling implementation. Existing exposure/retention checks remain opt-in.

## First real authoring trial — completed with rescue, budget result failed

Subsequent synthetic-panel trial: `.dev-shots/review-workflow-trial-01/`.
Parent inspected both final PNGs: fixed framing shows the intended hard-edge to
rounded-edge change. Saved before/after checkpoints, passing health/preservation
reports, six manifest events and a matched HTML sheet exist. Parent re-ran `status`
at reported step 26: `pending: []`, `evidence_complete: true`, **phase: stopped**.

This demonstrates end-to-end artifact tracking and resumable evidence, NOT a
rescue-free workflow or successful budget control. Several permission stops required
parent interventions. The Windows shell scanner appears to request the output file
argument as another command resource: the successful temporary ASK diagnostic created
a saved shell pattern for the output `.blend` path. Trial-only artifact resource
allowances allowed completion with default DENY restored. Full scanner cause is not
proven; see `.dev-shots/opencode-permission-diagnostic-01/note.md`.

Worker reported construction at approximately step 11–12 against parent stop-10,
and completion around step26 against parent deadline28. Manifest still contains the
original stop12/deadline24, with event steps3/8 that do not reflect actual model-turn
counts. Thus **reserve/deadline accounting is inconsistent and unvalidated**; it must
not be cited as proof the worker obeyed the reserve. Completion took multiple
continuations and a post-save summary NameError also required reconciliation.

Next tooling correction should address this specific mismatch: one recorded budget
revision/continuation identity and an unambiguous step-count convention. Do not add
new shape gates or claim improved completion rate from this single rescued fixture.
