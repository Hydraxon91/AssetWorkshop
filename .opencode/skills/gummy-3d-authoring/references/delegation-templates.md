# Compact authoring handoffs

Use when delegating a bounded modelling/review stage. Fill placeholders; omit
irrelevant fields rather than pasting every project rule. Repository/agent safety
instructions remain in force. These templates are working orchestration aids,
not evidence that a particular construction method is validated.

## Default: short outgoing brief, longer parent checklist

The longer templates below are the parent's PREPARATION CHECKLIST, not text to
paste wholesale into every worker prompt. Use the short brief for routine work;
add only facts whose omission could change the outcome or violate protection.
Do not repeat inherited repository/agent instructions as a miniature production
contract. Missing consequential authorization still blocks work.

Reference-read rule: scope it by task, not blanket. A brief that changes visible
form or judges likeness (shape, proportion, detail, surface) must name the
reference and require the worker to report what it read from it before building:
proportions, landmark positions, angles, relative heights. Naming a file is not a
read; a handoff that cannot state what the reference shows has not done it and the
parent returns the brief. Verification-only, preservation/restore, diagnostic and
index briefs do NOT need the reference - they name the checkpoint, the measured
question and the pass/fail criteria instead. Ask which governing view or crop
actually decides the task and supply that, not the whole sheet by reflex. Images
supplied in conversation are not files: the parent must save them into the asset's
`references/` folder before briefing, or say explicitly that the worker cannot see
them. Prefer the in-scene locked reference planes for shape judgement.

Execution gate: unproven native geometry must first pass reviewed-script and
disposable-process testing (`tools/blender-safe/README.md`, repository-relative).
Keep exact script/input hashes and timeout result. Native construction, checks,
save and capture are separate commands. A timeout is unknown/in-flight, never
permission to retry. A passing process is not passing shape/health/preservation.
Use one representative transition before a whole system. Do not spend the check
reserve on screenshots or omit health checks at a call ceiling; shrink the task.

### Routine modeller brief (default outgoing prompt)

Bounded-pass rule: one pass, one artifact. Design, build, render and apply are separate
passes. Put already-established measurements, rejected variants and parent decisions in
the brief as facts the worker must not re-derive. If the single artifact cannot fit the
allowance, the brief is too big — split it rather than extending the step ceiling.

```text
Mode: [GEOMETRY | VERIFICATION | EDITABILITY | MATERIALS; exact allowed changes].
Goal/level: [PRIMARY FORM or LOCAL REFINEMENT; one visible outcome; good-enough scale/criteria].
Baseline/ownership: [approved checkpoint, exact editable targets, new output path].
Recovery baseline: [last non-rejected checkpoint; retain all rejected candidates].
Protected/authority: [hard requirements/anchors versus scoped provisional controls; axes].
Evidence inputs: [reference/current images ONLY when the task changes visible form
or judges likeness; verification/preservation briefs name the checkpoint instead].
Reference read FIRST: [form/likeness tasks only: state, in the handoff, what the
governing view shows - proportions, landmark positions, angles, relative heights -
before building; a path alone does not count as having read it].
Approach: [SCRIPTED or INCREMENTAL MCP; one bounded batch, not guessed coordinates].
Completion: [new saved candidate + targeted checks + inspected comparison/provenance; actual result].
Deadline: [save by step N; stop construction by step M; reserve evidence/handoff].
Stop/handoff: [regression/blocker rule, candidate/images/results, STOPPED/live state].
```

Choose deadlines within the configured ceiling; all numeric defaults are local
heuristics. Record parent-approved adjustments; workers cannot self-extend or waive gates.
Once the evidence reserve begins, no new shape work: finish evidence and return
completed or explicitly partial. Saving geometry alone is not completion.

For reviewed disposable stage plans, use repository
`tools/asset-pipeline/scripts/review_worker.py` (contract in
`docs/review-session-workflow.md`), not new per-worker shell wrappers. It records and
enforces a runner-operation budget; the agent's model-turn ceiling remains separate.
Record construction-stop and deadline once per named continuation; on resume use
the manifest's pending stages, never repeat completed discovery or construction.
At the reserve boundary switch to evidence only; at deadline hand back the manifest
and blockers. Legacy `review_session.py` step indicators remain caller-reported.
Matched sheets require checkpoint-linked capture metadata; never invent missing legacy
camera data to make a sheet pass. This workflow is not validated as an agent-success
improvement until a fresh bounded trial completes without parent rescue.

### Routine reviewer brief (default outgoing prompt)

```text
Question/level: [one outcome; PRIMARY FORM or LOCAL REFINEMENT; agreed scale/criteria].
Candidate identity: [saved checkpoint or explicitly labelled disposable variant; baseline if relevant].
Closed evidence: [reference/crop for likeness; matched baseline/current for preservation].
Scope/authority: [required cues/exclusions; final-saved correspondence, metadata/registration limits].
History/protection: [stable findings/counts, essential protected constraints].
Inspect images FIRST; then assess these attributed claims: [short worker handoff].
Return: verdict, up to 3 supported findings, progression or ONE next action, gate, STOPPED.
If insufficient: request one missing view/fact; no artifact hunting.
```

Keep the parent's visual diagnosis out of the initial reviewer prompt when possible.
If a prior disputed finding must be supplied, label it as disputed, not ground truth.
Role separation is not statistical independence; agreement alone validates nothing.

## Trial validation — not yet proven

After each completed round, record briefly in the existing asset record:
- Did the worker finish candidate, checks, evidence and handoff within its allowance?
- Did inspected evidence/review support visible improvement at the agreed level/scale?
- Did the reviewer finish and distinguish observation from unsupported cause claims?
- What parent rescue was needed (missing render, protection check, path correction)?
- What time/cost was observed, if available (otherwise unknown, not estimated as fact)?

Use those observations to revise the brief, evidence set or construction strategy.
Do not declare the templates validated from one success, agent agreement or fewer
tokens alone. Repeated unfinished evidence means the orchestration still needs work.

## Additional parent preparation — not another prompt template

The two short templates above are sufficient. Check consequential fields before
sending: inherited finding/counts, actual live/dirty state, recovery candidate,
permission limits and temporary diagnostic changes/restoration. For editability,
select the relevant [checks](editability-verification.md) and name separately what
proves UI usability, dependency motion, result preservation or responsiveness.
For preservation, choose world geometry versus local-data identity deliberately.
Do not demand a full delivery audit or an external reference for origin maintenance.

## Parent adjudication between rounds

- Verify what was saved and inspect the selected evidence independently.
- Separate visual outcome from technical checks and attributed worker claims.
- Adjudicate causes/numeric remedies as hypotheses; do not blindly adopt reviewer
  coordinates. Verify the agreed threshold, not newly invented artistic gates.
- Accept improvement for progression, retain an imperfect candidate for a bounded
  refinement, or reject regression; none of these means user shape acceptance.
- Diagnose repeated failure and change the controlling construction when supported.
  A first failure is not proof that scripting or MCP is unsuitable.
- Reassess whole-object likeness periodically; do not spend every round on one tip.
- Reopen scoped provisional geometry when the whole-model evidence warrants it,
  within user authorization; local acceptance does not freeze a wrong silhouette.
- Preserve history. Do not silently pick the newest rejected file as the next baseline.

## Scripted and interactive specialists

For now use one modeller with an explicit execution approach. Scripts suit repeatable
construction, replication and measurements; incremental MCP suits visual control
adjustment. Both can use Blender Python: the distinction is feedback cadence, not
the programming language. Measurements alone do not establish either method's quality.

If separate agents are introduced, transfer ownership SEQUENTIALLY:
previous worker STOPPED → inspect saved/live state → record checkpoint and protected
state → brief next worker. Never concurrent live/headless asset editing. Independent
read-only review can use completed saved evidence without driving Blender.
Do not add a second specialist merely to work around an unresolved permission or
ownership blocker. Compare completed outcomes before declaring a method preferred.

### Limited truck-pilot evidence: incremental MCP is a promising option

The front-left flare's section-frame loft/mounting-pad method change, executed in
live MCP with intermediate visual checks, received conditional independent visual
approval for front-right replication. Earlier tip/sill-coordinate batches were
rejected for a hooked end and folded panel/diagonal sill artifacts. This supports
trying incremental visual feedback for difficult coupled curves; it does NOT prove
that MCP itself outperforms scripts (construction method changed too).

Use scripts for repetition/measurement and consider incremental MCP for local
section/junction shaping: state the expected contour change, edit scoped controls,
look immediately, then decide. Do not batch speculative deformations until a final
render. A first imperfect result warrants bounded diagnosis/refinement, not immediate
method abandonment. Regression still pauses that edit chain, not permission for
unlimited retries or automatic rollback.

Limits: one local result, not a finished car; front comparison is qualitative
against perspective reference. Worker hit its step cap and left temporary sheet
clutter live after saving the candidate. Method guide remains unvalidated: improve
evidence/cleanup budgeting and do not treat a clean flag as proof of scene parity.
Evidence: truck `gate1-ultrafast-01/evidence/compare_before_after_sheet.png` and
`interactive_flare_front_check_01.png`; candidate `truck_flare_FL_interactive_02.blend`
under `.dev-shots/car_img2-01/`. Conditional review is not user shape acceptance.
