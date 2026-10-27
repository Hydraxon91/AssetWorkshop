---
name: gummy-3d-authoring-handbook
description: Create, edit, calibrate, inspect and export Blender assets (3D models, meshes, props, vehicles, houses, furniture, soft goods, humanoids, animals, GLB files) for Gummy Bears using Blender MCP, with reference-image matching, PBR materials, UVs, texture baking, Geometry Nodes, editable source preservation and multi-angle verification. Use whenever the task involves Blender, MCP for Blender, a 3D model or mesh, materials, textures, baking, geometry nodes, blueprint/reference images, mesh cleanup, or GLB export, even if the user does not name this skill. Asset work does not authorize game integration.
---

# Authoring handbook — specialist procedures and tool index

Read only sections routed by `SKILL.md`. This is not a second mandatory entry
point. Paths retain their original repository/skill bases. Stage progression and
capture policy belong to [stage review](references/stage-review.md); reference
authority belongs to [reference review](references/reference-review.md). These
take precedence over summaries here. Existing validation labels remain unchanged.

Follow the repository's `AGENTS.md` and its task routes. Detailed technical preservation
rules are in `docs/authoring-operations.md`. Execution-mode choice, live ownership and
current MCP tool names are in `docs/execution-modes.md`, `docs/mcp-tools.md` and
`BLENDER_OWNER.md`; this handbook is technical reference, not a second policy.
Historical section 15 is preserved in
`docs/legacy/agent-procedures.md` for technical lookup, not as active project policy.
No game integration unless separately in scope. Repository paths below are relative to
the project root, not this skill directory.

This procedure applies to any Blender asset in the project, not only bears. Character and
species-variant rig/export notes are in "Character and variant authoring" and
"Deformation and export".

Last reviewed: 2026-10-26. Update this line when the commands, scripts or delivery
contract below materially change; `AGENTS.md` remains the policy source.


## Inspect before editing

1. Inspect the current filepath, dirty state, target objects, transforms, materials
   and modifiers using the configured read-only summaries in `docs/mcp-tools.md`
   (`get_objects_summary`, `get_object_detail_summary`,
   `get_blendfile_summary_path_info`). Do not assume the active file is the asset
   mentioned in chat; do not open another file over unsaved work without approval.
2. Capture the target with the configured screenshot or viewport-render tool,
   explicitly passing target names where the tool supports it. Establish a
   recoverable checkpoint before destructive edits: save under a new incrementally
   named file (`name_001.blend`, `name_002.blend`, ...) in the approved destination
   and never overwrite an existing one. Do not rely on a saved `.blend` containing
   unsaved changes.
3. Identify reference landmarks: head/body ratio, shoulder width, arm slope,
   base shape and depth. Distinguish visible measurements from estimates; a single
   front reference does not establish side geometry.
4. State units and axis conventions in the plan (e.g. metres, +Y front, +Z up) and keep
   them for the whole session. Put parts in collections per system and name objects
   clearly (`Wheel_FL`, `Tire_FL`).
5. Inventory shared mesh/material/image users, parents, constraints and modifier dependencies
   before changing data. Print `obj.data.users` and the sharing objects
   (`[o.name for o in bpy.data.objects if o.data is target.data]`) plus each material's users:
   spares and duplicates commonly share a road-wheel or prop mesh, so a transform edit is safe
   while a geometry edit silently reshapes both. Preserve linked users outside the scope; create an
   approved independent copy when needed rather than silently altering another part or its
   placement.


## Locating geometry before you touch it

When the user points at something ("this tube clips the body", "the hood is gone"), identify
it from the capture, not from bounding boxes or proximity.

1. Pick the visible target or cast a ray using the actual capture camera/pixel correspondence.
   Record the object, face/component and world position, then confirm it in an isolation
   capture. The first hit can be an occluder. If the camera cannot be recovered, reproduce
   the view or ask for a marked target; do not invent coordinates or edit a guessed object.
2. Print that object's island inventory before assuming what it is: island count, vertices
   per island, and each island's bounds. One object routinely holds both a detail and a
   structural panel.
3. Only then decide whether to move, trim, hide or rebuild, and record which control the
   next attempt will change.

Print that inventory before deciding what a component is; the case that motivated this rule
is recorded in `docs/3d-authoring-notes.md`.

Vertex sampling can detect some defects and measure vertex displacement, but cannot establish
complete surface clearance. Long tube faces can cross a host while both endpoint rings clear
it. Inspect evaluated triangles with BVH/ray or surface tests and captures; interpret intended
joints and containment separately rather than treating an overlap count as the verdict.


## Reference calibration (before modeling)

Required for reference-faithful/reconstruction work and requested dimensional matching.
Stylized/gameplay-read work without measured matching instead follows its declared
dimensions and visual-guide review; it must not claim calibrated likeness. Existing
reference planes must still be preserved and may not be warped to hide discrepancies.

1. Record real target dimensions (e.g. wheelbase, overall width/length, tyre diameter,
   ride height). Ask the user for any that are unknown and mark estimates as estimates.
2. Measure what each reference sheet actually encodes, and check that the sheets agree
   with each other. Report disagreements as numbers (e.g. "same tyre diameter, wheelbase
   differs by 21%").
3. Pick one sheet as the dimensional authority; the others stay faithful proportional
   guides. Never non-uniformly scale a reference to force agreement: it distorts the
   drawing (circles become ellipses). Conflicting sheets are the user's decision: present
   the numbers and options and wait.
4. Scale and place the planes uniformly so all views share one origin and scale, keep them
   in a `Reference` collection, and lock them after calibration. Recalibration requires
   reporting the discrepancy, obtaining approval, and rechecking dependent measurements.
5. Measure geometry from physical silhouettes and named structural landmarks, never from
   livery, paint colours or decal boundaries. Visually confirm each landmark on the
   reference before measuring; report obscured or ambiguous landmarks as uncertain rather
   than substituting a colour boundary. Record landmark names/endpoints, reference view,
   pixel coordinates, pixel-to-unit scale and uncertainty. State whether a measurement is
   projected or established by explicit dimensions; perspective images do not imply a
   uniform pixel-to-unit scale across different depths.
6. State the noise of any measurement taken from images (silhouette masks, edge scans) and do
   not tune below it. Validate a measuring script on a known case before trusting its
   numbers; a wrong sampling position or a mask that catches unrelated parts gives
   confident but false results.


## Direct comparison with reference planes

Use this measured-comparison gate in the calibrated-reference modes above. A stylized
visual guide does not require per-edit overlays; inspect neutral multi-angle form changes
and capture the approved shape gate. If an overlay is used as measured evidence, all
calibration, framing and source-freshness requirements still apply.

- During construction, inspect each silhouette change with a targeted viewport/solid
  view; use a targeted overlay when reference alignment is in question. At a silhouette
  review or acceptance gate, capture reference-only, reference plus model edges, and
  solid-model views with identical aligned orthographic framing against the calibrated
  planes. Preserve the baseline and refresh affected evidence after subsequent edits;
  do not rerun unrelated acceptance views or delivery checks after every small edit.
- Hide unrelated reference planes to avoid overlapping drawings. Use see-through or
  wireframe overlays, and inspect the captures to confirm the reference stays textured
  and readable beneath the model edges. Material Preview may ignore X-ray; full wireframe
  may hide the reference texture. A toggle is not evidence that the overlay works.
- Compare both upper and lower contours, openings, and fixed structural landmarks. For
  vehicles, explicitly check cab/window openings, wheel arches, door depth, rocker height
  against axle centres, and body-to-chassis relationships. Do not move unrelated parts to
  conceal a mismatch.
- Distinguish physical edges from paint boundaries, shadows, cage tubing, spare tyres and
  other overlapping components. Confirm feature identity visually before measuring.
- Report measured offsets and uncertainty. Agreement at sparse landmarks or sampled top
  heights does not establish whole-profile fidelity. Preserving image aspect proves only
  that the plane adds no aspect distortion, not that the source image or calibration is
  correct.
- Preserve reference calibration and restore temporary object visibility and viewport
  settings after captures. Report any intentionally retained comparison setup.


## Fitting attachments to host surfaces

- Fit trim and flares to the approved host surface; do not reshape that surface merely to
  accommodate a convenient primitive without explicit approval.
- Size structural joints against the bevel radius and reach the host member's centre or
  deeper; a nominal overlap smaller than the combined bevel opens a visible gap. Align a
  continuous stile with its leg, and use a Boolean-cut solid where joined objects would
  leave visible intersecting faces. Hidden overlap is acceptable; visible flicker is not.
- Measure the actual interface on evaluated geometry. A torus's full axial bounds do not
  describe its cross-section everywhere. Compare attachment and host surfaces locally,
  not just global X ranges or object bounds. Validate image/UV axes and local-to-world
  transforms against visually identifiable landmarks before trusting measurements.
- Test both floating gaps and host material breaking through the attachment. Include the
  full visible arc, ends and transitions. Missing samples remain unverified; do not narrow
  the sampling region merely to obtain a pass. Document any geometrically justified
  exclusions and report sampling limits alongside visual close-ups.
- Preserve symmetry: build mirrored fittings from one source unless reference evidence
  requires asymmetry. Do not introduce different left/right radii through independent
  fits without justification.


## Mesh health gate (after every step)

- Report non-manifold edges, loose vertices and flipped faces on the evaluated target.
  Intended closed solids must have 0 of all three before continuing. For intentional open
  panels, reference planes and construction geometry, report expected boundary edges
  separately; unexpected non-manifold edges, loose vertices and flipped faces must be 0.
  A single object may contain disconnected shells, and Boolean success does not prove a
  single watertight volume. A closed shell can still contain openings: window rims are
  interior loops between outer skin, inner skin and cut wall, so `boundary_edges: 0` is not
  evidence that the body has no windows.
- Verify consistent face winding numerically and inspect each closed component's intended
  orientation with Face Orientation captures. Blue marks front faces and red back faces;
  interpret them relative to the intended material volume, including cavity walls.
  Signed volume is supporting evidence only: a positive total does not prove every face
  points correctly. Do not use per-face ray tests as proof of orientation on open or
  concave meshes. For open panels, state the intended front side; reference planes looking
  red from behind are not defective. Report any orientation that could not be verified.
- Never run Recalculate Normals on an open panel without comparing Face Orientation before
  and after. It can pick the wrong side for a whole island.
- When a Smooth or other modifier is in play, compare evaluated geometry with that modifier
  enabled and disabled in world units. Report maximum vertex displacement only when vertex
  correspondence is established; otherwise report sampled surface distances with the
  sampling method and its limits. Report movement at fixed landmarks (roof, arches, lower
  edge) in mm, and stay within the tolerance the user set. Unapplied modifiers stay toggleable.
- Report evaluated, not only source, counts. Optimise after the shape is acceptable: smooth
  shading does not add polygons, flat shading is not synonymous with low-poly, and the
  silhouette must be re-inspected after reduction. Budget triangles, material primitives and
  exported vertices, not Blender polygon count alone. Do not invent a universal triangle
  budget; ask the user for one if none is given.


## Geometry transfer verification

Apply before accepting a join, split, bake preparation, topology conversion or export,
and before attributing a candidate failure to the source asset.

1. **Compare equivalent representations.** Label raw source mesh, evaluated source,
   bake candidate and re-imported export separately. Record source filepath, exact
   object and mesh datablock names, coordinate space, frame/pose, modifier configuration
   and whether each count is raw or evaluated. Compare matching evaluated states;
   bevels/subdivision and export UV/normal splits can legitimately increase counts.
   Raw-versus-evaluated count growth is not evidence of duplicated geometry.
2. **Resolve contradictions before repairs.** If a summary says all counts match but
   a named part disagrees, invalidate that diagnostic and stop edits, rebuilds and
   architectural changes. Produce the summary and per-part evidence from the same
   captured snapshot and exact identities, not separate queries with ambiguous name
   matching. Check stale datablocks, aliases, grouping and evaluation state before
   proposing a fix. Correct the report and withdraw unsupported earlier claims.
3. **Prove ownership through each operation.** Do not assume face or vertex ranges
   survive join, triangulation or modifier evaluation. Verify source-to-candidate
   ownership before and after every topology-changing step. Detect missing faces,
   foreign faces, duplicated parts and loss of material boundaries. Record any supported
   one-to-many mapping explicitly; index ranges require demonstrated order stability.
4. **Use independent preservation checks.** Equal counts plus zero nearest distance
   do not prove identical meshes: coincident duplicates can satisfy both. Verify vertex
   multiplicity or explicit correspondence, face connectivity, face/material ownership,
   UV correspondence, transforms and parents. Report point-distance bounds separately
   from topology and identity claims. Explain legitimate representation differences
   rather than inventing a vertex/face-count multiplier or offset as an acceptance guard
   (for example, `source_faces * 1.5 + 8` has no geometric justification).
5. **Exercise realistic fixtures.** Test bevel and subdivision modifiers, multiple
   materials, named UV layers, overlapping coordinates and animated parents, including
   their interaction in one fixture. Use known-good fixtures and deliberately duplicated,
   misassigned or missing outputs that must fail. Two separated unmodified cubes cannot
   establish arbitrary-assembly support. Validate diagnostic units and tolerances on
   those controls before treating a reported failure as an asset defect.
6. **Establish source responsibility.** Reproduce the suspected defect independently
   on the evaluated source at the same pose before requesting or performing a source
   repair. Classify the finding as inherited, introduced by the pipeline, or uncertain.
   A failed candidate or an unvalidated helper is not authorization to change a clean
   source. Correct the pipeline first when it introduced the defect; unresolved
   responsibility blocks source repair, not merely delivery.

These checks supplement the mesh-health gate; they do not replace visual, interface,
motion, material-transfer or user-acceptance evidence, and do not reset attempt limits.


## Regression stop

**Contradictory diagnostics block geometry edits, not just delivery.** Check units,
coordinate frames, object identity and expected invariants before treating a report as
an asset defect. On a contradiction, invalidate the affected claim, inspect the current
partially applied state and independently validate the diagnostic. Isolate operand
health from operation-result health before another Boolean or rebuild. Do not change
operation order or rebuild the host merely because an aggregate check failed.

Follow `docs/agent-procedures.md` sections 5 and 15: count failed repairs against the unresolved criterion,
not successful inspected construction steps or ordinary approved artistic direction.
At six failed repairs review progress; at seven stop autonomous retries. A user-approved
additional bounded repair batch must name its hypothesis, scope, checks and attempt budget
while retaining the prior ledger. After two unchanged failures validate the diagnostic.
A new defect class stops the current edit chain: restore the last good scoped checkpoint and
explain the alternative before proceeding within approved scope. Do not reset the attempt
count by changing strategy names. Preserve unrelated work; reopening a whole `.blend` needs
approval if it discards changes. If restoration is unsafe, stop and report.

The budget permits investigation, not moving goalposts. Threshold changes, overlap/collapse
exceptions and geometry exclusions require explicit approval. Never convert uncertainty to
a confident semantic label to obtain zero unknowns, or apply a tool already judged unsuitable.


## Character and variant authoring

Treat a new species/variant as a rig and delivery contract, not only a new silhouette.

1. Decide whether the variant shares an existing rig or needs its own. Reuse the source
   skeleton and clip names when the proportions and deformation allow it; duplicate only
   with an explicit reason.
2. Keep one authoritative editable source. Name the `.blend` checkpoint and record it in
   the asset manifest; local ignored checkpoints are not backups.
3. Preserve the rest pose and root motion contract before export. Check unweighted vertices
   and test representative bends, twists, squash and stretch from several views.
4. Keep variant materials parameterized (colour, transmission, roughness, coat) rather
   than duplicating the rig for each look. Export only the intended meshes and slots.
5. Write the asset manifest beside the delivery: tracked file, hash, scale/axis, bounds,
   mesh/skin/clip/material inventory, extensions, source and rights. Run
   `node scripts/glb-inventory.mjs <asset>.glb`; run the relevant `node --test` fixtures
   under `tools/asset-pipeline/tests/` when the delivery contract is active. A matching
   destination-side loader/manifest check is separate evidence; no local game path is
   assumed.
6. Add the species entry with `asset` and `assetManifest`; start from
   `docs/legacy/species-template.md` (historical destination context only). For Glass/Gummy/Bear, record which runtime path the asset
   uses: skinned GLB, 24-body metaball, or a future authored hybrid. Do not promise
   runtime mesh blending.


## Deformation and export (only when requested)

- For subdivided morph assets, demonstrate the delivery method on a separate copy before
  committing to conversion. Compare evaluated source against the delivery/re-imported Basis,
  every required morph state and representative intermediate weights under matched conditions.
  Verify target identity, correspondence and motion, not only counts or the neutral shape.
  Do not assume applying subdivision or enabling exporter modifiers preserves shape keys.
  Keep source editable; an unsupported transfer blocks delivery, not permission to drop morphs.
- Physics bodies, deformation controls/bones and the visible surface are separate.
  Do not assume 24 physics spheres require 24 bones. Inspect the current runtime:
  the bear baseline uses sphere physics and a generated metaball surface, not an
  authored skinned mesh. A new rendering path needs explicit approval.
- For a skinned asset, inspect unweighted vertices and test representative bends,
  twists and compression from several views. Automatic weights are a starting
  point, not a verified result. Restore the intended rest pose before export.
- Export only intended objects to the approved path. Check scale, axis conversion,
  origin, normals, material support and required extensions. Blender is Z-up;
  glTF is Y-up: verify conversion rather than adding an untested extra rotation.
- Check rendered material coverage; missing material slots must be intentional, not unnoticed
  default grey. Rebuilt or replaced objects start with zero slots, so check the object's slot
  list after every rebuild, not the material datablock. Require valid UVs where textures/bakes
  or the destination need them, not on every untextured mesh. Inspect islands, checker
  distortion, overlap and padding at the intended resolution; a UV layer or successful
  automatic unwrap alone does not establish suitability.
- Blender procedural graphs generally do not transfer faithfully to glTF/FBX. Preserve original
  graphs and bake required channels where unsupported. Newly generated noise is a replacement,
  not a transfer of the original appearance. Compare source and baked materials under matching
  lighting, cameras and view transform.
- Separate per-object material copies when distinct bake images need them, unless an intentional
  shared atlas is used. Prepare active image targets in every relevant material; resolve missing-target
  warnings before claiming complete coverage. Set colour/data spaces before baking and saving.
- A colour bake does not transfer procedural roughness, metallic, bump or coat. Bake required
  channels too, or obtain approval for a documented simplification; do not silently replace their
  drivers with constants. Save/reload images deliberately and inspect the connected maps.
- For self-contained packaging, re-import in a disposable scene with original texture paths
  unavailable. Inspect resolved images, actual material connections and rendered appearance—not
  just image-node counts. Embedding depends on exporter/importer support; a Blender round trip
  does not prove destination-engine support. If unverified, say so and offer a relative-path
  texture bundle rather than promising the FBX alone is sufficient.
- Quads/ngons triangulate on glTF export; UV/normal discontinuities can increase
  vertex counts. Record exported stats and validate the GLB with Khronos's validator
  when available. Its browser tool processes files locally; no new project package
  is required. If unavailable, report that validation is outstanding.
- Structural validation does not prove appearance. When integration is approved,
  inspect in the project's pinned three.js runtime with the real lighting/materials.
  Keep Blender/MCP out of runtime dependencies. Record source/reference provenance;
  do not assume a recreated branded character grants redistribution rights.

> Sections that duplicated stage policy, catalogued optional tooling, or served the
> finished game/truck assets were moved verbatim to
> `docs/legacy/authoring-handbook-archived-sections.md`. Read that file only when a
> route below points at it; it is not current instruction.
