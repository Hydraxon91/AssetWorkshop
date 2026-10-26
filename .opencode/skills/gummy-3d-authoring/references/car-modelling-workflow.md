# Car modelling workflow — working procedure

**Status: unvalidated.** A dependency-based workflow informed by external guidance
and the truck pilot, not a proven autonomous car builder. Use for cars/trucks after
the vehicle route. This supplements stage-review/reference-review; it does not
authorize new geometry, mechanical detail, optimization, materials or integration.
Use the approved asset brief for actual scope, dimensions and budgets.

## Principle: whole form → connected regions → details

Do not finish a roof, side, front and back as independent pieces. Establish the
whole vehicle at low detail, then develop coupled surfaces together. Recheck the
full silhouette after each regional change. The order below is a dependency order,
not a rule that all openings or thickness must wait until a late step.

## Construction order

| Stage | Establish | Evidence before progression |
| --- | --- | --- |
| 1. Reference setup | Vehicle axes, view authority, hard dimensions/scale anchors, uniformly registered locked planes, uncertainty | Correct front/left/up projection and relevant landmarks; resolve consequential conflicts |
| 2. Whole-vehicle blockout | Wheel proxies, wheelbase/track/ride height, body/cab/bed or trunk masses | Front, side, top and useful three-quarter; recognize vehicle character without details |
| 3. Primary body form | Central body/tub, nose/rear deck, canopy, side pods and fender volumes; no spoiler, springs or finished wheels | Coherent body character in front/side/top/three-quarter with proxies only; upper/lower contours and side-pod/character lines |
| 4. Body details | Fenders/arch lips, spoiler/wing, bumpers, panel lines, vents, windows and livery-registration surfaces; test one representative arch/fender/body interface | Local interface plus surrounding full contour; openings/thickness; no floating ends or exposed unintended returns; review before replication |
| 5. Running gear | Suspension arms, springs/shocks, drivetrain and underside; use the fixed wheel datums | Wheels visibly supported; shock/arm endpoints seated; coherent stance/contact; no body/arm intersections hidden by filler |
| 6. Final wheels and tyres | Finished wheel assemblies last; replace proxies; check ground contact, clearance and rotation | Whole vehicle with final wheels; both sides/front/rear/underside; no proxy remains |
| 7. Shape approval | Whole vehicle with all required geometry present | Neutral multi-view/reference comparison and explicit user gate where required |
| 8. Optimization, then later appearance/delivery | Separately scoped high-to-low, retopology, baking or LOD work as needed | Preserve approved silhouette and interfaces; delivery/runtime require their own approval |

**Why final wheels last (2026-10-26):** wheel proxies establish stance early, but finished
tyres and rims obscure the arch, arm and shock interfaces and invite detail work before the
body character is resolved. The RC-car pass built springs and running gear while the body
still read as a generic smooth egg; the result was detailed but unconvincing. Treat the
body silhouette and side-pod/character lines as the primary gate, then body details, then
running gear, then final wheels. This is a working heuristic, not a universal law: a
wheel-led design or an approved fit problem may justify bringing final wheels forward, but
record why and keep the body gate.

Rough windows, arch gaps and provisional thickness may be necessary during the
blockout to judge the form. Do not postpone a defining opening until after accepting
the body. Conversely, detailed seals, panel gaps, grille cells, tread and hardware
must not distract from unresolved primary shape. Suspension detail is only built
when authorized; visible plausibility is not engineering or simulation accuracy.

Wheel proxies establish stance early, but are not a finished wheel assembly.
Keep required named wheels separate and preserve protected axle/track datums.
Do not move wheels to hide body mistakes. Triangle counts follow the approved
stage: when shape-first work suspends a target, report counts only if useful;
do not simplify away necessary curvature or run optimization prematurely.

## Assign connected shape systems, not isolated symptoms

Prefer "front-left arch/flare/body junction" to "move this flare tip." Inspect
the adjoining surfaces and actual cause before selecting editable targets. The
brief must still explicitly authorize every changed system: discovering a bad body
return during a flare-only task does not grant permission to edit the body.

- Pilot one difficult interface before copying/mirroring it.
- Preserve editable sections/cages/operands and new-name checkpoints.
- For a visible tab/sliver, establish its object/face source through a bounded
  isolation/ray diagnostic; do not assume it belongs to the last edited object.
- If an attachment fix repeatedly exposes a host defect, return the scope conflict
  for a combined-interface decision instead of stacking cosmetic tip adjustments.
- A new regression stops that edit chain. Preserve the candidate, carry finding
  and repair counts forward, and choose a supported recovery/method change.

## Orchestrator → modeller → reviewer → orchestrator

1. Parent selects one region and measurable visual outcome, exact editable targets,
   protected state, baseline, save deadline and minimum evidence.
2. Modeller makes one bounded batch, saves, checks affected health/protected state,
   inspects the saved matched evidence and stops. Budget evidence time explicitly.
3. Reviewer receives a CLOSED evidence set: original reference/crop, authoritative
   current sheet and one matched previous sheet only if judging improvement (or a
   labelled before/after sheet). Include axes/registration facts and short handoff.
   No historical capture browsing. Ask for one missing view/fact if insufficient.
4. Parent independently adjudicates. Mirror only after representative geometry is
   supported by evidence. A rejected local edit is not silently adopted because it
   is the newest file. Continue only within the user's authorized stage/scope.

Review full form periodically so local cleanups do not consume the entire project.
Health, preservation, likeness, fit and user acceptance are distinct results. Agent
agreement alone is not a shape gate. Do not claim source registration from matched
before/after cameras: those establish edit comparison, not source calibration.

## Sources and evidence limits

- [SunStrike: 3D Car Models for Games](https://sunstrikestudios.com/en/blog/car_modeling_for_games/)
  — article read. Supports broad masses/temporary wheels first, continuous surfaces
  before panel separation, then detail/optimization. Commercial studio guidance,
  not independent validation. Its destination/material recommendations do not
  become requirements for this standalone workspace.
- [3D Car Modeling — Blocking in Your Models](https://www.youtube.com/watch?v=4L9pqU5WLDY)
  — discovered resource; video content not reviewed here.
- [3D Cars: Inside and Out in Blender](https://superhivemarket.com/products/3d-cars-inside-and-out-in-blender)
  — paid course option; lessons not evaluated here.

External beginner/industry guides consistently describe blockout → detailed modeling →
texturing, but they do not settle final-wheel timing. The body-first/final-wheels-last
order above is a local heuristic from the 2026-10-26 RC-car pass, where running-gear
detail outpaced the unresolved body character.

Local evidence limit: the RC-car pass then tried smooth lofts (v3–v10) and a manual
16-station cage with Subdivision/creases, glazing and a red front assembly (v11–v12).
The order was followed, but the body still did not reach reference fidelity; it remained
a smooth pod with crude fitted details. The body-first order is still sensible, but it is
not sufficient by itself. A detailed product buggy needs skilled manual cage/sculpt work
or a different modelling tool/operator; the vehicles module remains unvalidated.

Local motivation: the truck pilot's isolated flare edits exposed a pre-existing
body return, and a later tip-only re-seat introduced a hook without removing the
body tab. Reviewer evidence supported rejection, not successful repair. These
observations justify interface-first diagnosis; they do not validate this complete
construction order or guarantee autonomous reference fidelity.
