# AssetWorkshop

Standalone Blender authoring workspace. This project owns authoring; destination
projects own integration. Do not read another repository to obtain instructions.

## Scope and safety

- **Proportionate safeguards:** Before adding workflow complexity for a speculative
  or very unlikely failure, explain the concrete failure mode, evidence of likelihood,
  potential impact, and added cost. Get user approval before expanding scope. Prefer
  the simplest safeguard that addresses a credible risk. This does not waive existing
  safety rules, preservation requirements, or review gates.
- Plan → user approval → implement → verify → report and stop. Agree active stage,
  target objects/paths, dimensions, fidelity, budgets and review gates once. Each
  pass names its review level, one visible outcome and “good enough” criteria at
  the intended viewing scale. A body-only gate blocks attachments. Checks never
  grant user acceptance; reviewers do not add stricter artistic gates afterward.
- Preserve the requested outcome and operator. Do not replace asset delivery with
  an expanding research programme. If the user requires a named model/agent to
  perform the work, parent execution, static review or another model is not an
  equivalent substitute. Return an unavailable operator as a blocker; a change
  needs explicit approval and cannot establish the original model's capability.
- Classify dimensions as hard constraints, scale anchors or provisional values.
  In approved reference-led work, provisional values may change to improve the
  inspected shape; record old/new values, reason and evidence for parent review.
  Hard constraints and scale anchors need approval to change. Do not silently
  reclassify existing commitments or infer hidden dimensions from perspective.
- Inspect source, references and actual live state before editing. Separate user
  decisions, evidence, assumptions and conflicts. Return consequential conflicts
  instead of silently changing constraints. Preserve unfamiliar work.
- Use a reference plane for any supplied reference view, even a single side view:
  build a locked, uniformly scaled in-scene plane before shaping, and judge the
  form against it. Do not eyeball proportions or work from a detached image viewer.
  If scale or orientation cannot be established, say so and agree the substitute
  authority before building; never non-uniformly stretch a reference to fit.
- Prove model/view orientation as well as pixel registration: record object
  datums, camera direction and image axes before comparing asymmetric features.
  A filename or a camera-axis label alone does not establish front/side/back.
  A reference plane aids comparison; it does not make a source orthographic or
  physically calibrated. State projection/scale uncertainty and measurement authority.
- Preserve editable profiles/cages/operands and new-name checkpoints. Never open
  over unsaved unrelated work. Never delete, overwrite baselines, commit, push,
  add dependencies or use paid generation without explicit approval.
- Use file-edit tools for scripts/docs; Blender Python edits approved scenes and
  saves/exports approved assets. Export does not authorize destination integration.
- Load `gummy-3d-authoring` as the routing index for asset work. Select only the
  relevant construction category and current-stage references. Follow additional
  links only when their stated condition applies, not merely because they are
  linked. Do not preload the handbook, unrelated categories, historical records
  or destination contracts. The retained skill name is compatibility, not a
  requirement to load Gummy game context. Select a delivery contract only when
  the destination requires one; no destination is assumed.

## Delegation and Blender ownership

- Execution mode is chosen from `docs/execution-modes.md`; the default is
  `scripted-disposable`. Live MCP is parent-owned read-only inspection; subagents do
  not receive MCP tools in the current harness. A scoped live edit is a parent-owned,
  explicitly authorized exception. A brief that does not name a mode is incomplete.
  Actual tool names are in `docs/mcp-tools.md`; the approved operator is in
  `docs/operators.md`.
- Unproven scripted native geometry runs first in an owned disposable process,
  not interactive Blender. Review/retain exact scripts and input hashes; use
  `tools/blender-safe/` for direct-mesh pilot preflight and timed process tests.
  It is not a sandbox or geometry/shape approval. Prove a representative junction
  before expansion. Shape, health and preservation must pass before integration.
- Separate native construction, validation, save and capture commands. A tool
  timeout means unknown/in-flight execution, not cancellation. No new MCP queries
  or retries until process state is reconciled. After a freeze, inspect exact
  failed code and disposable reproduction before live retry. Only owned test
  processes may be terminated automatically; interactive Blender needs approval.
- Keep ONE current-state card per brief/ownership record, with superseded state
  under an explicitly historical heading. Record exact scripts, timestamps,
  timeouts and checks when observed. Budgets must fit a complete small result;
  mandatory health checks come before screenshot work, not after the step cap.

- Parent uses short outgoing briefs; long templates are preparation checklists,
  not prompts to paste wholesale. Supply consequential approval/ownership,
  baseline/recovery, relevant references/protection, the exact reviewed entry point
  and next operation, one outcome and minimum evidence/deadline. Check required
  worker command/write scopes before assigning execution or source development;
  do not assume an approval brief changes permissions. Workers verify consequential
  facts, not the entire toolchain/history. Do not commission redundant readiness
  probes or repeated discovery when current evidence already establishes them.
- Reuse suitable reviewed operations. Keep infrastructure development separate from
  asset operation: name the concrete missing capability, obtain bounded development
  approval and test it before reuse. A frozen-tool/parameter-only pass changes data,
  not implementation code or wrappers; return a required repair as tool development.
  Scripts alone are not a completed modelling pass. Do not silently turn a blocked
  asset task into another tool project or extend preparation by increasing the cap.
- Review the WHOLE MODEL periodically, not just the last edited region: after a
  connected system is completed, before replication/stage progression, and when
  successive local edits yield little overall improvement. Use the latest selected
  full-model captures to rank remaining high-impact mismatches; do not expand every
  small correction into a fresh full-asset audit or render suite.
- Reviews must lead to decisions, not automatic diagnostic loops. Separate observed
  defects, unverified features and proposed causes. Reviewer causes and unmeasured
  numeric fixes are hypotheses, not instructions or new dimensional authority.
  Ask for diagnostics only when they change the next decision. Parent reconciles
  conflicts and completed work; repeated failure calls for a construction/scope
  decision. Separate roles reduce self-review but do not establish statistical
  independence; agent agreement never substitutes for evidence or user acceptance.
- Protection distinguishes user requirements/scale anchors from temporary ownership
  boundaries on provisional geometry. Prior local acceptance does not prove the
  whole-model shape correct. Parent may revise scoped protection within existing
  user authorization; workers may not release it themselves. Return consequential
  conflicts rather than build around a known bad host or change hard constraints.

- For visual reviewers, parent supplies a closed evidence set: relevant original
  views/crops, labelled authoritative current captures, and matched previous captures
  only when judging improvement (a labelled before/after sheet may combine them).
  Select by checkpoint identity, not modification time; use enough views for the
  question, not a fixed image quota. Include the review level/agreed criteria,
  short handoff, registration facts and constraints; do not point reviewers at
  artifact directories or optional historical captures. Reviewer requests one
  specific missing view/fact and stops if evidence is insufficient;
  parent selects any expanded evidence set before another review.

- Parent plans and independently reviews; `modeller` implements approved bounded
  stages. Briefs name approval, exact ownership, saved/live baseline, protected
  state, criteria, evidence, limits and recovery. Missing authorization blocks edits.
  Name verification, geometry, editability or materials mode; other tasks need explicit scope.
  Default to two unsuccessful diagnostic approaches per blocker, then return it;
  this does not reset geometry-repair counts. Require explicit stopped handoff.
  Workers return scope/permission blockers to the parent once, without trying
  alternate tools or interpreters. No service/browser startup, downloads or
  environment/credential inspection unless explicitly included in approved scope.
  Final replies state completed, blocked or stopped; claim ongoing work only when
  a real background operation exists. Keep full logs in artifacts, not handoffs.
- One live Blender owner across all projects that share this machine, not just
  this Git tree. Consult `BLENDER_OWNER.md`; it records this workspace's current
  owner and is not a machine-global lock. Record the handoff wherever the other
  project keeps its ownership card. Global MCP access does not grant ownership.
  Explicit handoff requires previous worker stopped, filepath/dirty state inspected
  and checkpoint recorded. Do not drive Blender concurrently, including during
  parent review.
- Keep one writer per assigned files. Record scoped Git state and ignored source
  checkpoints; Git cannot recover unsaved scenes. After interruption inspect actual
  partial state before retrying. No automatic rollback or replacement worker.
- Correction briefs use stable findings, expected/actual evidence, allowed targets
  and regression checks. Carry repair counts across sessions/filenames: diagnose
  after two unchanged failures, review at six, and require recorded approved batches
  after seven by default. Every repair names a hypothesis and testable change; a
  new geometry regression stops the edit chain. Workers cannot self-extend; absent an
  explicit adjustment, tighter limits win.
- Budget, reserve, deadline and handoff mechanics have one owner:
  `references/stage-review.md`. AGENTS.md keeps only the safety line above — repair
  history, regression stops, one writer and no self-extension.

## Evidence and delivery

- **Design connections; do not camouflage them.** Do not conceal gaps or
  disconnected parts with arbitrary blocks, shims, collars, tubes or other filler.
  Identify the actual host and intended load/assembly path, then correct the
  interface or replace the faulty mounting assembly. Brackets/gussets are valid
  only when deliberately shaped and plausibly seated on both hosts, not added
  merely to make a proximity/contact check pass. Remove superseded visible patch
  pieces while preserving recoverable originals. Inspect joints close-up AND in
  assembled context: zero distance, overlap or coincident vertices alone do not
  prove coherent construction or acceptable appearance. Return scope conflicts
  instead of stacking filler around protected bad geometry.

- **User-editable delivery:** meaningful parts must remain independently
  selectable and transformable in Object Mode, with useful origins, named assembly
  controls and recoverable sources. Protect technical helpers from accidental
  selection without making required user parts inaccessible. Locks, destructive
  merges or shared-data behavior that obstruct ordinary edits need approval/disclosure.
  Follow the skill's `references/editability-verification.md` for UI state,
  dependency motion, evaluated-result and responsiveness checks. Names and matrix
  tests alone do not prove an editable, responsive asset.

- **Silhouette first, details later.** Establish whole-model proportions and major
  contours in all governing views before local surface polish or secondary detail.
  Use primary-form reviews before prolonged local-refinement reviews; stage-review
  defines both levels. Judge "good enough" at the agreed scale/fidelity, not perfection.
  Do not let close-up seams, end caps, faceting or tiny interface flaws monopolize
  iteration while a primary outline is wrong. Defining openings, support/contact
  and silhouette-changing
  parts belong to primary form; this rule never excuses missing required features,
  unsafe operations or geometry regressions. Use simple neutral shading and make the
  next edit address the largest remaining visible mismatch, not the easiest detail.

- Compare full contours before/after edits; inspect saved captures. Visual likeness,
  geometry health, fit and user acceptance are separate results. Use stage-appropriate
  checks, not a complete delivery suite after every edit.
- Give evidence unique, non-overwriting filenames linked to checkpoint identity,
  view/camera/render metadata and whether it depicts final saved geometry. Refresh
  affected evidence after geometry changes; unverifiable legacy provenance remains
  unverified. A filename, timestamp or clean flag alone is not proof of correspondence.
- State measurement authority and units explicitly. Normalized authoring units are
  not metres/millimetres merely because Blender has a unit setting. Technical contact
  or endpoint checks do not prove visible plausibility; an isolated assembly can fit
  while reading poorly or remaining hidden in the intended assembled views. Neither
  occlusion alone nor absent evidence proves a geometry defect.
- Scratch/reference/checkpoint copies under `.dev-shots/` are ignored. No automatic
  LFS setup or binary commits. Source copies retain historical paths; inspect and
  relocate dependencies before claiming portability.
- Report completed, failed, blocked and unverified criteria, changed paths, current
  checkpoint/live state and next authorized action. Separate toolchain execution,
  requested-model operation, visual asset quality and user acceptance; supporting
  checks cannot make an unmet central requirement an overall pass. Identify the
  actual operator and any parent rescue. Propose skill changes with evidence;
  workers do not edit their own instructions.
- Destination contracts live under `contracts/`. Versioned copy + hashes is the
  delivery boundary; destination intake and integration remain separately approved.
