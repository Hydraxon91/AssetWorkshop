# Curved products — verified in one product pass

**Status: verified in one reference-led product pass (2026-10-26); still candidate
guidance, not a universal generator.** Follow the main skill; use for moulded
shells, curved housings and swept/revolved parts. Also read the category module when
the product is furniture, a vehicle or architecture.

## Verification record — 2026-10-26

Applied end-to-end to the standalone Frutiger Aero soap bottle: superellipse section
loft for the body, revolved collar/stem, a user-edited flattened pump head fused with
a swept spout, a conforming label film, full per-object UVs, and a material/render
handoff. The user accepted the body, the pump correction and the materials. Evidence:
`.dev-shots/frutiger-aero-bottle-01/soap-01/brief.md`; UV checkpoint
`appearance/appearance_uv.blend`; final appearance checkpoint
`appearance/appearance_final.blend`.

What the pass supports: independent shoulder/base/label-panel control from the sparse
loft; revolve/sweep for the pump; exact-union plus a BVH-selected local seam fillet
for a user-edited sub-part; a thin conforming label film; and the scale/health checks.

Limits: one asset, one operator pass, no motion or deformation, no independent second
asset and no game integration. The pump seam is a Tier 3 close-up detail accepted at
the target scale. This record verifies the guidance was usable for this product; it
does not make the module a generator or certify every future form.


## Construction order — products and household housings

1. Establish the complete envelope, dominant profiles, axes and defining openings.
2. Resolve primary section progression and curvature before panel seams or controls.
3. Test one coupled cap/side, handle/host or opening/rim transition. Inspect the host
   as well as the attachment; do not repair an unidentified host defect with trim.
4. Resolve required cavities/thickness and separate assembled pieces without losing
   the approved outer form. Add buttons, feet and other secondary masses in a pass.
5. Add fine grooves/legends only after form approval; optimize only in its own scope.

For electronics, inspect front controls AND side/back depth before finishing one
face. Review the whole envelope, then one close-up/section of the difficult junction
under neutral shading and a broad reflection. A shiny view is not thickness proof.
Order is a project synthesis, not a mandatory modifier stack. General form-first
support: [CG Cookie modelling principles](https://blog.cgcookie.com/posts/6-principles-of-great-3d-modeling/)
(article read). [Topology guide](https://blog.cgcookie.com/posts/the-art-of-good-topology-blender/)
is an additional lead, not evaluated here; topology advice is not shape acceptance.

## Game-first application (only for an agreed game destination)

For game assets, read the shared [game-asset contract](game-asset-contract.md). Use only enough section
and bevel resolution to preserve approved curves at the nearest intended view. Fine
grooves, legends and grain can use existing material/normal detail when they do not
need physical depth. Strip-reflection diagnostics reveal defects; they do not demand
film-smooth geometry invisible in-game. Keep the editable cage/high source separate from
delivery and recheck rim thickness, opening boundaries and normal/UV splits after reduction.

## 1. Recognise the geometric drivers

Identify section changes, curvature direction, symmetry, openings, rim thickness,
mating parts and operating poses. Distinguish a continuous moulded shell from assembled
panels. Establish whether the closest view requires physical thickness and interior faces.
Do not treat a paint boundary or reflected stripe as a structural edge.

## 2. Choose a starting method

| If… | First candidate | Main alternative / risk |
| --- | --- | --- |
| Sections change independently along the body | Sparse section-driven subdivision cage | A rounded box may couple cap and side curvature |
| The object is rotationally symmetric | Revolved profile with editable radius/height | Sphere scaling provides less direct profile control |
| A stable section follows a path | Curve sweep with controlled orientation | Freehand mesh deformation may introduce twist |
| Surfaces are mostly planar with local machined cuts | Panels/solid plus editable booleans and bevels | Subdivision may unnecessarily couple flat faces and openings |

Choose by the actual part. A mixed product may need more than one construction method.
Do not default every housing to a bevelled cube or every opening to a Boolean.

## 3. Prove the tightest transition

For reference-led products, first establish a stable exterior silhouette with an
editable profile/cage and verified camera/reference registration. Do not make a
full inner shell a prerequisite to deciding the outer form. Once exterior shape
is settled, prove the tightest opening/shell transition below. Standard modifiers
are available; explicit mesh generation is not mandatory. Repeated script runs
should edit known controls and derive the surface, not invent a new profile each
time. Shared framing and local Python/MCP workflow: repository
`docs/authoring-operations.md`.

1. Build only the main sections and symmetry at the agreed physical scale.
2. Keep sections sparse enough to edit independently. Add support where curvature needs
   it, not a uniform high subdivision level that hides the cage.
3. Test one cap-to-side transition plus the tightest rim/opening and shell thickness.
   Keep source profiles, cutters and modifiers editable.
4. Inspect neutral solid and broad strip-reflection views. Move the view: a static
   highlight can conceal a dent or a flat spot. Keep diagnostic materials temporary.
5. Evaluate shell thickness and mating surfaces, including cap/subdivision shrinkage.
   For moving parts test closed and operating poses before replication or trim.

**Editable controls:** section positions, section shape, support-loop spacing, symmetry,
wall thickness, opening boundary and sweep/revolution axis. A material split must not
duplicate a shell. Use graphics and fine grain as textures after the surface is approved.

Procedural revolutions, lofts and sweeps are legitimate construction methods, not an
exception to editability. Retain their profiles/paths and source operands separately
from evaluated or Boolean-combined results. Update the scoped controls rather than
reconstructing unrelated parts; regenerating the derived mesh must preserve accepted
features and placement. Test the actual bend, cross-section and shell interface before
combining the assembly. If a Boolean fails, establish operand health and isolate the
failing intersection before changing the host or trying another operation order.

## 4. Diagnose failures

| If you see… | Inspect… | Test next |
| --- | --- | --- |
| Pinching by an opening | Cage topology, support spacing and nearby curvature | A local boundary/support revision before increasing subdivision |
| Highlight waviness | Section progression and pole placement | Simplify/reposition controls; compare the same reflection view |
| Flat-face shading smears | Actual planarity and evaluated normals | Correct the geometric cause before stacking normal modifiers |
| Rim or cap shrinks away from a neighbour | Evaluated surface versus cage | Revise cap/support construction, not filler trim |
| Sweep twists or intersects itself | Path curvature, frame orientation, section size | Test one bend with the actual cross-section |
| Bevel vanishes near a cut | Thin features, nearby edges and overlap clamping | Diagnose the limiting feature; do not globally disable safeguards |
| Boolean-union seam is a crease or pinch | The true intersection loop, not a bounding box | Select dual-surface seam edges; fillet only those, or accept the crease at the target scale |
| Voxel remesh ripples a thin rim | Voxel size versus rim thickness | Keep the exact union; do not remesh a defining rim |
| A flattened or shortened sub-part changes overall height | Whole-assembly bounds after the edit | Re-run the envelope/scale check, not just the edited part |

## 5. Change-of-method gate and checks

If section edits cannot control the tightest transition without changing protected
surfaces, compare a small alternate construction under identical lighting and framing.
Propose a method change only when the comparison demonstrates the control difference.

Acceptance evidence must show silhouette, opening, thickness, reflection continuity
and evaluated mating fit separately. A shiny hero view does not prove the hidden wall
or the complete interface. Use [openings/glazing](openings-and-glazing.md) where applicable
and the shared assembly checks. No detail, bake or export while required form is missing.

## 6. User-edited sub-parts and local fusion (observed, candidate)

When the user supplies an edited `.blend`, that edit is authority. Do not regenerate
the part from older parameters or silently replace it with the builder's previous
shape. Preserve the source, record its hash, and integrate it as a new-name checkpoint.

For a sub-part that must become one visible prop:

1. Keep the edited head and the mating part as sources; duplicate the head before
   destructive work.
2. Apply an exact Boolean union, clean tiny slivers (~1e-5), and confirm one closed
   island.
3. Fillet only the true intersection loop, selected by dual-surface proximity (BVH),
   not a bounding box. A box also catches the spout tip and head rim and pinches.
4. Keep source operands hidden and unselectable; they are recovery inputs, not visible
   parts.
5. Re-measure the whole assembly. Flattening or shortening one part changes total
   height and the envelope check.

A global bevel on the union can generate hundreds of degenerate faces; a voxel remesh
fuses the seam but ripples a thin rim. Use remesh only when the rim is not a defining
feature. If the remaining seam is a continuous crease, judge it at the target scale
rather than reopening the geometry.

**"One seamless prop"** means one visible object with no gap or overlap. A perfectly
continuous smooth surface is a stronger requirement; state it explicitly in the brief.
A small crease at a moulded junction can be acceptable at the target scale.

## 7. Detail importance at the target scale

Before repairing a seam, end cap or tiny fillet, measure its share of the intended
screen height. A 0.8 mm crease on a 12.7 mm pump head of a 160 mm bottle is roughly
1–2 px at one-third screen height; it is close-up-only. The general tier rule is in
[stage review](stage-review.md). A gap, hole, non-manifold result, unsafe operation or
user-named feature is never downgraded.

A printed capacity is nominal, not the visible fill. Report capacity and fill fraction
separately; do not gate the liquid volume to the label number.

A single oblique handheld photo cannot calibrate orthographic scale. Use a declared
envelope plus a labelled 10 mm grid proxy, not a stretched image plane.

## Related reading, not validation

[Blender Expert hard-surface guidance](https://github.com/edemaistre/blender-expert-skills/tree/main/blender-hard-surface)
discusses planar Boolean/bevel versus curved subdivision approaches. This guide is
project-authored synthesis, not its toolkit or a transfer of its claimed test results.
