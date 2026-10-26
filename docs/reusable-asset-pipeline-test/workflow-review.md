# Initial workflow review — 2026-10-26

## Question and scope

Does preparation/tool friction consume the allowance before a small tested result?
Review existing evidence and simplify the handoff/execution path, not safety rules.
This is an initial read-only diagnosis plus plan documentation, not a completed
performance study. No instructions, runners, permissions or agent caps changed.

## Evidence inspected

- `docs/review-session-workflow.md`, especially current worker path, pass-size
  findings and synthetic trial02.
- `tools/blender-safe/README.md`, including its narrow direct-mesh runner contract.
- Controller `preparation_01/`, `preparation_02/`, `brief.md`, and
  `registration_01/run_registration.py` / `metadata.md`.
- `docs/deepseek-authoring-pilots.md` for prior bounded results and limitations.

## Findings

1. **The controller assignment selected the wrong experiment.** The intended
   question was reusable operations with cheaper-model parameter selection.
   Instead, two preparation passes designed new asset-specific geometry scripts.
   This was parent scope/method drift; it does not establish model incapability.

2. **Preparation produced no model-geometry test.** Both preparations stopped
   before Blender execution. Parent review found concrete construction and
   registration errors. Rejecting those scripts was justified; repeatedly asking
   a worker to design the pipeline was not testing reusable modelling capability.
   Exact total model turns and elapsed preparation time are unmeasured here. The
   supplied '30-turn' example is not verified by these controller artifacts.

3. **A shared staged path already exists.** `review_worker.py` is documented to
   separate build/save/check/capture and avoid worker-authored wrappers. Its
   synthetic trial02 reportedly completed 9/12 runner operations without rescue.
   That is useful execution-path evidence, not a curved-modelling template or a
   general success rate. Its plan/dependency/version suitability needs checking
   during the tooling audit before reuse for this benchmark.

4. **The controller handoff did not take that path.** Parent briefs emphasized
   the lower-level `blender-safe/run.py`. Workers then wrote stage, save, reopen
   and capture code. Registration used a fixture cube to carry non-mesh parameters
   through the mesh-preflight interface. The worker disclosed it, but that cube
   did not validate the reference scene. This is a concrete interface mismatch,
   not evidence that another new runner is needed.

5. **Reference registration succeeded, modelling remains untested.** The saved
   two-plane reference checkpoint and inspected orientation captures are useful
   retained work, but no editable controller body exists. The registration script
   calls build/check/save/capture functions in one command, rather than the
   separately resumable staged path. Do not elevate this bespoke script to the
   benchmark's frozen reusable toolchain without explicit review/development.

6. **Provider failures are a separate failure class.** Two Abliterated continuation
   requests failed during generation, before new files appeared. The requested
   switch to OpenCode Free produced the registration artifact. That does not
   isolate a model-quality effect: provider and task scope changed, and no matched
   modelling benchmark was run.

## Changes to the planned experiment

- Parent finishes the narrow audit and chooses a supported operation before
  briefing a modelling worker. Supply exact inputs, runner path and next command.
- Keep reusable tool development separate from benchmark operation. No wrapper
  authoring or method selection inside a frozen-tool modelling pass.
- Front-load the first actual disposable test. Agree an early milestone for the
  chosen ready operation, not another universal step rule. Missing setup returns
  a named blocker while there is still decision budget.
- Budget one complete small result with mandatory checks/save and minimal useful
  captures. Do not attach full-asset development to a representative pilot.
- Track preparation, first execution, validation and manual rescue separately.
  Report measured model turns/operations/time independently, unknown when absent.
- Retain ownership, baseline preservation, reviewed disposable execution and honest
  verification. No new governance layer, automatic cap increase or instruction edits.

## Next decision

Complete Step 1's capability inventory, including whether the existing staged
runner can invoke the selected tools without asset-specific wrapper code. Recommend
the smallest supported end-to-end test and disclose any development required.
Do not resume the controller cage as a substitute for that decision.
