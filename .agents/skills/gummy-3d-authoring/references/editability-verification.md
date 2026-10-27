# Editability verification

Use for selection, origins, assembly controls or editing-performance work. This
supplements [stage review](stage-review.md), not authorization to reshape an asset.
No new reference calibration is needed unless the task changes or judges form.

## 1. Define what the user can edit

- Distinguish the visible derived result, its editable sources and technical cutters.
  State which object/control moves each part or assembly; clicking a Boolean result
  does not select its source. Keep meaningful parts accessible, not only named.
- Protect reference planes, archives and incidental helpers from normal clicks.
  Provide an explicit source-editing route (selection, Outliner collection or mode)
  without duplicate solid surfaces. Disclose wire-source editing when used.
- Choose useful pivots: centred origins for free parts, hinge/axle origins where
  appropriate. A wheel's tyre/rim/hardware moves together, independently of others.
  Inspect snapping, pivot mode, locks, constraints and shared object-data users;
  a fake user is not a second object instance. Do not reset user transforms.

## 2. Test dependencies, not just parenting

- Whole-model and part/assembly controls must carry intended members and active modifier
  operands while unrelated parts stay static. A whole-truck root test alone does
  not prove body-only or individual source editing. Check the actual dependency
  links, not a name-prefix guess; complete lower/upper assembly membership matters.
- Choose representative translate/rotate probes and, for coupled sources, the
  reported failing direction plus a small bounded set of contrasting poses.
  State tested offsets, not arbitrary-motion guarantees. Restore in `finally` and
  compare against the captured baseline, including unrelated parts and selection.
- Verify the visible evaluated result survives the edit. Healthy source meshes,
  matching matrices and nonempty output can all coexist with most of a body missing.
  Inspect retained features/extent and affected health, allowing intended detachments.
  Risky evaluation belongs in an owned timed disposable process under AGENTS.md,
  not an interactive Boolean sweep in the user's live scene.

## 3. Compare the right representation

- For hierarchy-only edits, compare mesh data, world poses, modifier links and
  materials. For origin edits, local coordinates legitimately change: prove world
  geometry/topology and dependent modifier inputs are preserved. Preserve children
  and inspect coordinate-dependent modifiers; do not claim raw-hash identity.
- A solver change can alter topology without a consequential visible change.
  Separate raw-source identity, evaluated topology and surface preservation; use
  matching-pose surface/visual comparisons when correspondence is lost. Report
  local maxima and sampling limits, not exact identity from sparse distances.
- If geometry disappears, localize the first failing modifier using comparable
  prefix results, including loss of body extent rather than only empty meshes.
  Validate a single configuration correction on a copy before live integration.
  Do not hide the failure behind a proxy or adopt one solver as a universal fix.

## 4. Responsiveness and handoff

- Distinguish snapping, input/selection trouble and expensive evaluation. Compare
  a simple part with the affected derived assembly. Record any update timings as
  that measurement only; a scripted matrix move does not certify smooth dragging.
- If a proxy/cache is proposed, agree the switch/refresh workflow and preservation
  first. It must not mask missing geometry or replace recoverable construction.
- Report selection/pivot usability, dependency motion, evaluated preservation and
  responsiveness separately as passed/failed/unverified. Give exact control names
  and editing exceptions in the asset guide; keep the handoff short.
- A user interaction check can accept usability without accepting whole-model
  likeness or resolving untested performance. Move on when the agreed gate is met;
  do not grow every origin correction into another full-asset audit.
