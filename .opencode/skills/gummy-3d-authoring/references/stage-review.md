# Stage, approval and evidence policy

This is the single Blender progression/capture policy. `AGENTS.md` owns common
safety. Execution-mode choice (scripted disposable vs live MCP) is in repository
`docs/execution-modes.md`; this policy constrains a delegated stage but does not choose
the mode. Technical references supplement this policy; they do not add per-edit
approval gates. This policy does not grant permission to edit, export or integrate.
Shape-first and inspect/revise are supported workflow principles, not proof that
this agent setup is optimal. Exact budgets, retries and evidence layouts are local
heuristics; ownership, preservation and user gates are safety/authority policies.

## Agreement and progression

Use stages **shape → assembly → appearance → delivery → runtime integration**.
Skip inapplicable stages explicitly; local repairs may revisit a stage, invalidating
dependent evidence. Neither a review nor prior local acceptance authorizes rebuilding
neighbouring parts. Parent may reopen provisional geometry within approved scope;
workers cannot release protected targets or change hard constraints/scale anchors.

Agree review boundaries once in the approved scope. Ordinary edits, diagnostic
captures and scoped repairs within the active stage do not each require approval.
At an agreed user review, stop for approval. An approved whole-asset chunk may
authorise crossing listed stages after verification without routine check-ins;
explicit shape-approval gates still require the recorded user approval they name.
A later “body only” instruction blocks other parts despite earlier broad scope.
“Broadly match it” changes fidelity, not part scope or visible-result approval.
Checkpoint renames and new methods never convert rejected shapes into accepted ones.
Export and runtime integration must each be explicitly included in scope.

Name one review level for the pass; these are not additional production stages:
- **Primary form:** whole-model proportions, governing silhouettes, major masses,
  defining openings and visible support/contact. Use normal-scale neutral views.
- **Local refinement:** junctions, shading and small surface defects, once primary
  form is good enough. A consequential primary-form regression takes priority again.

### Visual importance at the agreed scale

Judge a defect at the view where the asset is used, not only in a close-up.

- **Tier 1:** silhouette, major masses, defining openings, support/contact.
- **Tier 2:** features that read at the agreed view (label graphics, collar ribs,
  a pump seam if it reads).
- **Tier 3:** close-up-only seams, end caps, tiny fillets, fasteners.

A Tier 3 issue does not block a Tier 1/2 gate when it is continuous and does not change
the read; a gap/hole, non-manifold or unsafe result, a user-named feature or a Tier 1/2
change is never downgraded. Record the acceptance and the target view. A close-up
capture is diagnostic, not an automatic defect. Example: a 0.8 mm crease on a 12.7 mm
pump head of a 160 mm bottle is roughly 1–2 px at one-third screen height.

### Render budget

Renders are evidence for a decision, not iteration fuel. Use the smallest set of views
that answers the question (normally one full view plus one close-up; add a functional
view only when it answers something new). Do not run a render suite or repeat beauty
renders after every parameter tweak; re-render only when the change invalidates the
evidence. Stop at the agreed gate.

Before editing, record one visible outcome, governing views, intended scale/fidelity,
required features/exclusions and the threshold for progression. A qualitative
criterion is valid (for example, a continuous major outline in named views); do not
invent pixel tolerances without measurement authority. Review against that agreement,
not retrospective perfection. New safety issues/regressions still stop work; a newly
discovered artistic concern is for parent adjudication, not a silently stricter gate.

User selection ends candidate exploration. Record the selected object and current
approved pose in the asset-local record, then develop that candidate; do not revive
old rankings or switch to a prior favourite without a specific approved reason.
Treat user-corrected transforms as authoritative, not older generated parameters.

## Current work record

### Bounded worker brief checklist

When preparing a modeller/reviewer handoff, use the compact
[delegation templates](delegation-templates.md). Load for delegation, not every
geometry operation; fill only the active-stage fields and keep briefs bounded.

Name the review level/agreed outcome, protection, new-name checkpoint, minimum
evidence and stop condition. Routine local edits use affected health/protection
checks and an inspected comparison, not overlapping audits. Choose enough views
for the question; broader review coverage and user acceptance remain separate.

Allocate a construction/save deadline, evidence reserve and handoff within the
configured ceiling for a complete small result, not just script preparation. For a
ready-operation pass, agree an early first disposable-test/execution milestone;
after essential ownership/input checks the worker invokes the supplied operation.
If setup blocks it, return the specific blocker while decision budget remains.
Explicit design-only work is not an execution result. Separate commands need not
mean separate planning sessions. Numbers are task-specific, not quality guarantees;
parent may adjust within authorization, never waive safety/gates. Workers cannot
self-extend. At deadline preserve safe partial work and report unmet criteria,
not another iteration. Record runner operations, model turns and elapsed time
separately when measured; never infer one from another.

Return STOPPED once saved, checked and visually assessed; report failed criteria
honestly, without extra audits, invented assertions or easier substitute tests.
Judge overall completion against the requested result/operator, not the easiest
passing subsystem. Toolchain execution, named-model operation, visible asset quality
and user acceptance are separate outcomes; parent-run fixtures do not validate an
uninvoked model. Do not repeat completed work merely to inflate a supporting metric.

Maintain one compact asset-local current record, preferably updating the existing
brief rather than creating a parallel system. Update at consequential decisions,
review boundaries and handoffs, not every edit. Link historical evidence without
rewriting it. Include:

- Active part/stage, review level/agreed criteria and blocked downstream stages.
- Approved constraints, required features, protected state, budget and decision sources.
- Reference/view authority, observations, assumptions and unresolved discrepancies.
- Authoritative saved checkpoint; actual live filepath/dirty state and known live
  differences. Inspect contents: filenames and dirty flags alone prove neither.
- Last verified result, evidence provenance below and pending user decisions.
- Next authorised action and unresolved criterion's failed-repair count.

If inherited state cannot be established, mark it unknown and inspect before editing.
An agent inference is not a user decision. Keep report detail proportional to risk.

### Evidence provenance

Use unique, non-overwriting names tied to checkpoint identity, not modification time.
In the existing record or a small metadata sidecar, link each selected capture to:
- Exact source checkpoint and before/after role; whether it depicts final saved
  geometry, an intermediate candidate or live-only changes.
- Camera transform/direction and image axes, projection plus lens/orthographic scale,
  framing/resolution, shading or render settings and relevant visibility state.
- Reference crop, uniform scale/registration and known projection/scale uncertainty.

Temporary capture settings must be restored and live/saved differences disclosed.
Geometry changes invalidate dependent captures/checks; refresh them before claiming
they prove the final source. Unknown or stale legacy correspondence is unverified,
not silently promoted to current evidence. Reuse established metadata when unchanged.

Distinguish "saved source loaded" from "source saved during capture"; a false value
for the latter does not imply unsaved geometry. Label pilot comparisons as pilots,
not final-saved evidence; they can support a configuration decision before saving.

## Verification matrix

Execution modes constrain a delegated stage; they do not replace this matrix.
Verification inspects without asset edits; geometry changes named systems only;
editability changes named hierarchy/origins/selection while preserving world shape;
materials preserves mesh data, transforms and unrelated materials. Check shared users.
Briefs explicitly allow any temporary diagnostic state, require restoration and
name preservation checks. Blender Python is not technically restricted by mode.
UV/bake/rig/export scope must be separately specified. Reuse the existing current
record and approvals; do not add a new approval ceremony for routine scoped edits.

| Decision | Evidence required |
| --- | --- |
| Routine construction edit | Targeted neutral comparison at the agreed level/scale, affected evaluated health and protected-state checks; inspect returned images |
| Editability | Task-scoped [editability checks](editability-verification.md); distinguish UI state, dependency motion, evaluated preservation and responsiveness |
| Shape-stage review | Whole-model neutral governing views, normally front/side/top/three-quarter, showing required forms/openings/contact; reference-led work also needs aligned reference-only/edges-over-reference/solid comparisons with calibration limits disclosed |
| Assembly acceptance | Assembled and isolated affected interfaces, endpoints, neighbouring clearances and protected surfaces; relevant operating poses; inspect front/back/both sides/three-quarter coverage of changed assembly |
| Appearance acceptance | Matched material/rendered views of affected channels and corners; geometry-preservation checks for material/UV-only work |
| Delivery | Fresh final-source feature checklist, evaluated/export/re-import inventories, topology/UV/material/transfer checks and clean self-contained import; inspected final multi-angle appearance |
| Runtime integration | Separately approved game loading, functional assertions, captures and performance/lifecycle checks under the chosen destination's verification plan |

Select extra close-ups, underside views or motion frames when needed to demonstrate
a criterion. A view name does not prove orientation, isolation or visibility. Do not
recapture unrelated views after local edits; refresh evidence whose claims depend
on those edits. Construction uses cheap views; rendered batches are for settled
acceptance decisions or targeted render-only diagnosis. Standalone Blender work
does not require game screenshots or `window.__gummy`.

## Decision and stop conditions

Report specific observations: what contour improved, what remains mismatched and
what is unverified. Never substitute bounds, mesh health or an isolated beauty
render for the requested comparison. Separate structural health, reference fidelity,
feature presence, fit, preservation, motion and user acceptance. Missing active-stage
required features block progression; uninspected regions are not passes.

Reviewer causes/numeric prescriptions remain hypotheses unless measured/verified;
parent adjudicates them against scene facts and the agreed threshold. Recommend
progression when met, otherwise one consequential correction or decision-relevant
diagnostic. Optional polish alone does not force another round. Separate reviewer
roles do not imply statistical independence; agreement is not a correctness test.

Contradictory diagnostics stop geometry repairs while the diagnostic is validated.
Keep hypothesis/control/evidence and cumulative counts per unresolved criterion;
use AGENTS.md's retry defaults unless a parent-approved brief records an adjustment.
Continuation beyond a review/batch boundary needs recorded authorization covered
by user scope, otherwise ask the user. Successful construction is not a failed repair.
No new hypothesis means stop; renamed files/sessions/methods never reset history.
New regressions stop the chain for scoped recovery, not speculative patching.

Helpers may check documentation completeness or freshness; they cannot judge visual
suitability or approve on the user's behalf. Their restrictions apply to their own
entry points, not arbitrary MCP operations. Do not describe procedural rules as
technically enforced restrictions. Known tool mismatches must remain disclosed.
