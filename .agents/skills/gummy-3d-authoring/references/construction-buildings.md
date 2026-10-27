# Houses and buildings — unvalidated

**Status: unvalidated.** Project-authored construction guidance, not architectural,
engineering or building-code certification. Follow the main skill and approved scope.

## Construction order

1. Establish complete footprint, storey/roof masses, scale and viewing coverage.
2. Block the main wall/floor/roof system together, including defining large openings.
3. Prove one corner + reveal + eave/floor junction before repeating bays/modules.
4. Test a small assembled layout with the actual pivots/grid and required interior
   coverage. Close unintended seams before producing the rest of the kit.
5. Refine openings/frames/overhangs, then scoped secondary trim; furnishing and fine
   surface detail must not hide unresolved structural silhouette or junctions.

Review the whole massing and one representative assembled corner from exterior/top
and, when required, interior. Choose modules for actual repeated needs, not a universal
grid size. [Beyond Extent: modularity and uniqueness](https://www.beyondextent.com/articles/balancing-modularity-and-uniqueness-in-environment-art)
(article read) supports reference decomposition, early blockout assembly tests and
main pieces before smaller ones. Its material/engine advice is destination-specific,
not authority to integrate or merge this project's assets.

## Game-first application (only for an agreed game destination)

For game assets, read the shared [game-asset contract](game-asset-contract.md). Budget visible modules
and their repeated use, not only one facade. Prove a module before repetition; reuse
materials/UV scale where suitable and preserve project batching/instancing ownership.
Do not build inaccessible interiors, hidden joinery or physical bricks unless required
by views or gameplay. Required reveals, overhangs and cutaway thickness still need form.
Keep collision/navigation requirements distinct from render detail. Check module seams,
material primitives and shadow cost at representative repetition before runtime claims.

## 1. Identify the viewing and construction contract

Record plans/elevations, units, footprint, storeys, floor/roof levels, wall thickness,
opening dimensions and roof pitch where known. Mark estimates. Decide exterior-only,
visible interior, cutaway or walkthrough. Identify moving doors, modular repetition,
collision requirements and intended camera distance without assuming game integration.

For exterior-only stylized houses, layered applied window bays are acceptable when the
frame has real depth and a dark recess. Record whether each opening is cut or applied.
Applied bays do not prove wall thickness, interior coverage, real reveals or weather
closure.

## 2. Choose a method by structure

| If… | Start with… | Watch for… |
| --- | --- | --- |
| A unique house follows a measured plan | Extruded wall/floor/roof components with explicit junctions | Corner overlaps, missing returns and uneven thickness |
| Bays, windows or floors repeat | One proven module, then Array/instances | A repeated defective junction or shared-data edit |
| Walls contain many rigid openings | Closed wall solids and scoped editable cutters | Thin reveals, coincident cuts and wrong cutter collection |
| Walls are deliberate open panels | Surface plus controlled thickness | Treating open source panels as closed solids in diagnostics |
| A roof or facade has continuous complex curvature | Profile/section method from curved products | Primitive stacking that misses the silhouette |

Use [curved products](construction-curved-products.md) for the last case. A facade
texture cannot replace an opening, reveal or roof overhang visible at the intended view.

## 3. Prove a junction, then expand

1. Establish footprint and floor/roof datums before furnishing or landscaping.
2. Build one exterior corner, one window/door reveal and the adjoining roof/eave or
   floor junction. Model the surfaces visible from the agreed interior/exterior cameras.
3. Check wall thickness and opening clear dimensions on evaluated geometry. Add the
   representative pane/frame only after the opening is correct.
4. Inspect top, outside corner, inside corner and elevation views. For cutaways also
   inspect the exposed exterior wall corner and complete floor perimeter.
5. Test the module's repeated seam and material/UV behaviour before replication.
   Test moving doors with hinges and clearance if movement is required.

**Glazed openings:** build each pane from one simple closed boundary and keep the arch
winding consistent with the springing. Check for profile self-intersection before adding
frames. Inset glass ~10–20 mm from the frame/reveal; never give a pane and its opening
the same outer boundary. Keep backing/recess planes separate. Inspect a close-up in the
viewport and in the final render engine.

**Editable controls:** plan dimensions, levels, wall thickness, opening bounds, roof
profiles, overhang, module spacing and pivots. Keep furnishing independent of the shell.
Use trim for actual trim, not to conceal failed wall/roof connections.

## 4. Diagnose before patching

| Observation | Inspect first | Next test |
| --- | --- | --- |
| Interior works but outside corner is open | Wall returns and junction coverage | Isolated top/exterior view of that corner |
| Flicker at repeated seams | Coincident faces and ownership | Correct one module boundary; do not just offset the whole facade |
| Window is a dark rectangle with no depth | Opening, reveals and pane placement | Oblique interior/exterior close-up |
| Diagonal shimmer or flicker inside a glass pane | Profile winding/self-intersection; coincident pane, reveal, frame or backing faces | Rebuild one simple profile; inset the pane; re-render a close-up |
| Z-fighting in the viewport but clean in the final render | Coplanar/overlapping surfaces and viewport depth precision | Fix the geometry, not the engine or shading |
| Open underside when the building is lifted | Floor/base closure | Add a floor slab/plinth, or explicitly record an exterior-only open boundary |
| Roof floats or penetrates walls | Evaluated eave/wall geometry | Fit the roof junction without distorting approved elevations |
| Unexplained changes across copies | Shared mesh/material users | Diagnose sharing before changing the source module |

## 5. Change-of-method trigger and checks

If the chosen module cannot express the required corner, roof change or opening without
changing protected bays, test a distinct junction/module rather than forcing identical
repetition. Obtain approval for restructuring; a single failing corner does not authorize
replacing the building.

Check footprint/elevations, wall/floor/roof continuity, required interior coverage and
opening thickness separately. A front facade render does not prove a complete building.
Report deliberate cutaway/open boundaries distinctly from unexpected mesh defects.
Game collision, navigation, lighting performance and integration are separate tasks.

## Field record — one stylized exterior (2026-10-27), not a verification

Applied to a reference-led Frutiger Aero villa: reference-plane blockout, curved white
massing, a central roof drum, arched glazing, a sculpted entrance canopy, ring
balconies, chrome bands, a recessed rear curtain wall and an exterior-only landscape
look. The pass exercised the guide's massing, opening, frame, trim and whole-view
inspection guidance. It also exposed a failure: six arched glass panes had a
self-intersecting profile and shared boundaries with their openings, producing
z-fighting after first delivery. Rebuilding the profiles and insetting the panes fixed
it.

What the pass supports: using the guide for a stylized exterior massing and glazing
study; treating a perspective/AI reference as a qualitative guide; and checking a
glazed close-up separately from the whole-building view.

Limits: one asset, one operator pass, no independent second building; no interior,
cutaway or walkthrough; no measured plan, wall-thickness or opening-clearance proof;
no repeated-module, moving-door, roof/eave or game-runtime test; no junction-first
proof before expansion. The initial z-fighting was found only after delivery, and the
user subsequently made cosmetic and z-fighting edits. Evidence:
`.dev-shots/frutiger-aero-house-02/brief.md` and
`artifacts/frutiger-aero-villa-house-only-v1/`.

This is a field record, not a verification. The module remains unvalidated.
