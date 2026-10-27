# Vehicles — unvalidated

**Status: unvalidated.** Candidate procedures, not a validated car builder. Follow the
main skill's calibration, protected-geometry and approval rules. For smooth curved bodywork also
read [curved products](construction-curved-products.md). Vehicle type determines which
wheel, suspension, articulation or hull checks apply; state exclusions explicitly.

For car/truck construction ordering and orchestrated shape reviews, also read
[car modelling workflow](car-modelling-workflow.md). It is a working procedure,
not a validated builder or authorization to change the active stage.

## Intended use and budget

Establish intended use before budgeting body panels, wheels, glass and moving parts;
do not assume a game destination. For game/runtime assets only, read the shared
[game-asset contract](game-asset-contract.md) and establish background, interactive
or hero use. For other purposes, agree the relevant visual or physical requirements.
Spend loops on identifying body/arch curves and required operating clearance; do not
model engine internals, hidden cabin detail or every fastener by default. Keep parts
separate where movement requires it, not merely because a CAD assembly would. Budget
transparent glazing, shadows and material primitives as well as triangles where
relevant to the intended output. Test any
approved delivery reduction in the required poses and at intended camera scale.

## 1. Establish the vehicle, not just its bounding box

Record authoritative views, overall dimensions, wheelbase/track when applicable, axle
centres, tyre size, ground plane, body landmarks and visible openings. For non-wheeled
vehicles identify their support/propulsion and characteristic sections instead. Decide
static prop versus operating steering, wheels, doors or suspension before construction.

Never stretch a reference sheet to reconcile conflicting dimensions. Locate physical
silhouettes, not livery or shadows. Missing interior/reference data stays unverified.

## 2. Choose construction per system

| If the system is… | Start with… | Avoid… |
| --- | --- | --- |
| Smooth continuous bodywork | Longitudinal/transverse sections at approved scale (calibrated for measured matching), Mirror and controlled subdivision | A single scaled primitive with details hiding its profile |
| Fabricated body panels or frame | Dimensioned panels/members, thickness and scoped bevels | Treating painted boundaries as separate structural panels |
| Wheels or other rotational parts | Revolved profiles with explicit centres and axes | Guessing tyre profile from total diameter alone |
| Glazing or apertures | Real opening boundary and mating pane/seal geometry | A dark decal substituting for an opening visible in silhouette |

Use distinct editable systems where the real assembly or articulation requires them.
For boats/aircraft, prove the characteristic hull/wing section and junction rather
than applying a car-body recipe. No physical or aerodynamic performance is implied.

## 3. Build the difficult interface before repeating it

1. Place dimension/axis datums and one representative wheel or support section.
2. Build the primary body sections without grilles, lights, handles or livery.
3. For a wheeled vehicle test one arch/fender adjoining the body, including thickness,
   inner opening, wheel clearance and curvature under subdivision. For other vehicles
   test the defining section junction identified in the brief.
4. Review neutral multi-angle shape views; for measured matching capture aligned
   orthographic reference-only, edge overlay and solid views. Compare
   upper and lower contours, overhangs, openings and axle landmarks, not just roof height.
5. Inspect curved interfaces under broad reflection strips. Test required steering,
   suspension or panel poses using evaluated geometry before mirroring/replication.

Keep wheel proxies through primary body and body-detail work. Build the final
wheels/tyres/rims after the body character and the representative
arch/fender/suspension interfaces are accepted; finished wheels obscure those
interfaces and can make a weak body look finished. Do not detail springs, drivetrain
or rims while the primary body silhouette is unresolved (2026-10-26 RC-car pass).

**Editable controls:** section locations/shapes, symmetry plane, axle/hinge axes, wheel
profile, panel boundaries, arch clearance, thickness and support spacing. Keep wheel
placement independent of body shape. Do not move a protected wheel to disguise a bad arch.

## 4. Failure-specific responses

| Failure | First diagnostic | Scoped test |
| --- | --- | --- |
| Correct bounds, wrong vehicle character | Beltline, greenhouse, overhangs and section widths | Revise the controlling sections without adding details |
| Arch pinches under subdivision | Local cage, poles, support loops | Test one arch boundary; more subdivision is not a repair |
| Flare gaps or buries itself | Evaluated host/attachment over the full interface | Fit the attachment, not an approved host surface |
| Window looks opaque/filled | Opening geometry, occluders and pane placement | Isolate the actual aperture before shader changes |
| Tyre clips during movement | Axes, evaluated sweep and operating poses | Test the required movement, not just parked clearance |

## 5. Decision and checks

Change construction only if a representative section/interface cannot be independently
controlled within the approved tolerances, and an alternate test demonstrates why it can.
Do not rebuild the complete vehicle after a local shading failure.

Before detail, show required apertures, underside silhouette, ground contact and body
sections in named captures. Check both sides and front/rear; symmetry does not establish
reference fidelity. State static versus motion evidence separately. Use the shared
evaluated-contact and mesh-health procedures; counts and parked bounds are not fit tests.
No fixed triangle, bevel or penetration allowance applies to all vehicles.

## 6. Livery, materials and export (unvalidated field notes)

These are observations from the 2026-10-26 Spike RC-car pass, not a validated vehicle
pipeline. Apply the normal stage gates and the project-wide Qwen/UV precondition.

- **Livery follows the body gate.** Do not use paint to hide a weak silhouette, missing
  opening or unfitted detail. Agree whether livery is painted directly on the body/canopy
  UVs or on separate decal films. Direct body UVs avoid film z-fighting and extra
  geometry but replace the body material with the atlas; separate films preserve the
  base material but need seating, thickness and occlusion checks. Record the choice and
  its trade-off.
- **Plan the UV sheet before generation.** Use the Qwen prerequisite in
  `uv-island-export.md` and `AGENTS.md`. Directional planar charts work for decals:
  classify by dominant world normal and use a basis with right x up = normal so the
  texture is not mirrored. Name flanks, top, nose, tail, wing and canopy separately;
  verify the names on the model, not only in the atlas, including nose-up orientation
  for top charts.
- **Do not trust one multi-island Qwen pass to place every island.** In this pass a
  64-island livery canvas painted only one flank's mouth and wordmark, put the mouth at
  the tail, and assigned endplate/panel colours to the wrong islands despite explicit
  per-island instructions. Raw output is artwork, not placement. Prefer one focused
  canvas per side or part for direction-dependent art; otherwise repair deterministically
  (mirror the accepted flank, re-paste the wordmark, fill non-key islands black) and
  inspect the result on the model. Keep a scripted wordmark fallback for legibility.
- **Do not put a livery-critical feature on a provisional plate.** A separate front
  accent panel that is not accepted may be deleted or sit proud of the body. Paint the
  feature on the accepted host surface, or confirm the plate is part of the accepted
  silhouette and seated correctly. A render can show a plate that the user does not
  consider part of the model.
- **StableMaterials colour drift is normal.** Generated black plastic/tyre came out
  blue-grey and red came out neon. Grade the base colour with a script to the authored
  look, keep the generated normal/roughness/metallic, and do not regenerate solely for
  colour. Judge gloss and clearcoat under neutral, non-blown lighting; a broad front-view
  highlight is a lighting response, not proof of a texture seam.
- **Export is a separate gate.** Keep one object per wheel with the required names and
  axle origins; apply export modifiers; exclude reference planes; state axis and units.
  Interchange formats do not support Blender object-coordinate texture mapping: rewire
  image textures to the UV layer (or bake) for the export copy and keep the look-dev
  wiring in the source. In Blender 5.2.3 FBX, `path_mode='COPY'` plus
  `embed_textures=True` embedded PNGs; `AUTO`/`STRIP` left absolute source paths and no
  embedded content in this pass. Verify both formats by re-importing: object/mesh count,
  wheel names, materials, bounds and rendered appearance. Export does not authorize
  destination integration.
