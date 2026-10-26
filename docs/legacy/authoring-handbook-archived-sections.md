# Authoring handbook — archived sections

> **Archived 2026-10-25.** Moved verbatim out of the live handbook to keep the active
> skill small. These sections duplicate `references/stage-review.md`, catalogue optional
> or old tooling, or describe completed truck/game work. Not current instruction; consult
> only when a skill route explicitly points here. Execution policy has moved to
> `docs/execution-modes.md`; any "live MCP first/default" wording below is historical.

## Game-first destination

Runtime game assets are the default across every construction category. Read the shared
[game-asset contract](../../.opencode/skills/gummy-3d-authoring/references/game-asset-contract.md) before the construction brief
and applicable module. It is **unvalidated** guidance, not a guarantee of performance.
Agree role, camera/screen coverage, instances, geometry/material/texture budgets and
required motion first. Prefer modest editable sources and budgeted delivery copies;
dense CGI/sculpt sources need an explicit approved purpose and a delivery strategy.
Game-first and reference fidelity are independent: preserve the approved likeness mode.
This does not authorize optimization of unrelated assets or game integration.


## Fidelity and production route

Agree the mode and required cues before modelling; do not default every reference image
to exact reconstruction. If unspecified, propose the mode and budget and wait for the
normal plan approval. Use this choice consistently in all construction references below.

| Mode | Acceptance target | Reference procedure |
| --- | --- | --- |
| Stylized / gameplay read | Approved identifying silhouette, major forms and readability at intended game scale; explicitly simplify secondary details | Inspect images as visual guides, declare dimensions, compare neutral multi-angle views; calibrated overlays only when measured matching is requested |
| Reference-faithful | Specified structural proportions, interfaces and reference features | Calibrated authority view, locked planes, aligned overlays and stated uncertainty |
| Reconstruction | Measured multi-view matching of the agreed visible structure | Calibration/overlays plus explicit landmark, coverage and discrepancy analysis; unsupported hidden structure remains unverified |

Modes do not waive mesh health, protected-state checks, required openings/contact,
source preservation, export gates or runtime verification. Required versus optional/
omitted features come from the approved brief, not every visible wrinkle in an image.
Changing an existing brief's fidelity requires approval and invalidates affected acceptance
claims; it does not retroactively turn failed benchmarks into successes.

For assisted stylized background props read
[stylized game props](../../.opencode/skills/gummy-3d-authoring/references/stylized-game-props.md), then the applicable construction
module. This route is **partially verified only for one human-assisted DeepSeek beanbag
trial**; the general method, independent/autonomous production, broader use and a
higher-tier control remain unvalidated. It prioritizes useful human art-direction checkpoints,
existing materials and a budgeted delivery copy, not exhaustive reconstruction analysis.
Record camera distance or screen coverage, likely instances, triangle/material/texture
budgets, motion/collision needs, available source materials and authorized delivery stages.
Do not call a Blender source game-ready without the export/runtime evidence that claim needs.


## Default authoring workflow: live MCP first

`references/stage-review.md` governs progression. At a stage review or
handoff, state the checkpoint, current part, pending approval, blocked downstream work
and next action. Preserve a user-requested part-first gate even inside an approved batch.
A fidelity clarification changes likeness expectations only: it is not approval of the
visible shape or permission to begin another part. Obtain approval at the agreed review boundary.

Use live Blender MCP as the primary shape-authoring workflow. MCP can execute Python;
the distinction is visually guided, incremental modeling versus blind batch generation,
not Python versus Blender. Choose construction from the requested form and references,
not from whichever existing builder or prototype happens to be available.

1. Inspect the live scene, unsaved state and references; agree on scope, construction,
   dimensions, axes and acceptance criteria before editing.
2. Establish a recoverable checkpoint. Build an editable primary form with small scoped
   changes through MCP: inspect with `look`, edit, then inspect again.
3. Review the silhouette, contact and major sections in neutral multi-angle views and
   obtain silhouette approval before detail or material polish.
4. Add details, UVs and materials only as needed for the approved outcome. Continue
   inspecting affected areas and preserve unrelated geometry and placement.
5. Check mesh health and inspect final multi-angle captures. Numerical checks support
   visual judgment; successful scripts and populated reports do not establish likeness.
6. Bake, export or integrate only when separately in scope; report each delivery state.

Python is appropriate for scoped modeling operations, repetition, measurement, diagnostics,
captures and export. It must not replace inspecting form changes or repeatedly regenerate
the whole asset to avoid looking. Live MCP can also run checks and capture views; headless
Blender is optional, not a prerequisite for verification. Procedural construction is an
explicit method choice to justify and test, not the default for every asset.

For soft goods, prefer an editable quad cage with broad contact, controlled subdivision,
deformation and folds. Test the seat/contact transition first: subtracting a cavity from
a smooth primitive can read as a rigid bowl rather than a yielding fabric form.

Before building, check supplied views for design contradictions as well as scale using
the [construction brief](../../.opencode/skills/gummy-3d-authoring/references/construction-brief.md). When motion is requested,
use its unvalidated control-selection guide and short motion contract: rest/recovery,
allowed combinations, support/contact and prohibited outcomes. Choose controls before
detail; after primary-form approval, prove one moving region before replication or rig
polish. A static prop does not need a rig, and a squash does not automatically need bones.


## Construction routing

Before completing the construction brief, read the shared game-asset contract and the
applicable modules below. These are
specialist references under this skill, not separate installed skills or generators.
**All seven are unvalidated:** practical candidate procedures, not established project
recipes. They do not authorize edits, override approvals or justify rebuilding a source.

Route by geometric drivers, required movement and intended use, not object name alone.
Load more than one module when the asset contains different construction systems.

| Form / task | Construction reference | Difficult test before detail | Status |
| --- | --- | --- | --- |
| Upholstery, beanbags, cushions, fabric | [Soft goods](../../.opencode/skills/gummy-3d-authoring/references/construction-soft-goods.md) | Loaded seat/contact-to-back transition | unvalidated |
| Moulded shells, flowing continuous surfaces, swept/revolved products | [Curved products](../../.opencode/skills/gummy-3d-authoring/references/construction-curved-products.md) | Tightest curvature, rim and opening | unvalidated |
| Cars and other vehicles | [Vehicles](../../.opencode/skills/gummy-3d-authoring/references/construction-vehicles.md) | Arch/fender/body interface and wheel clearance | unvalidated |
| Houses, buildings, architectural shells | [Buildings](../../.opencode/skills/gummy-3d-authoring/references/construction-buildings.md) | Wall/opening/roof junction with thickness | unvalidated |
| Human-like characters | [Humanoids](../../.opencode/skills/gummy-3d-authoring/references/construction-humanoids.md) | Characteristic proportions and required joint bend | unvalidated |
| Animals and species-based creatures | [Animals](../../.opencode/skills/gummy-3d-authoring/references/construction-animals.md) | Species silhouette, shoulder/haunch and articulation | unvalidated |
| Timber/metal furniture and rigid frames | [Rigid furniture](../../.opencode/skills/gummy-3d-authoring/references/construction-rigid-furniture.md) | Seat/back/frame joint and ground contact | unvalidated |

A wooden chair routes to rigid furniture; a moulded chair also loads curved products;
a beanbag routes to soft goods. An upholstered frame loads furniture plus soft goods.
An animated animal also uses this skill's rigging/deformation guidance. Frutiger Aero
and other aesthetic directions supplement construction through look-development guidance;
they do not determine topology or replace a geometry module.

Each module supplies conditions, editable controls, failure diagnosis and a representative
test. Agree on numeric tolerances in the brief rather than importing tutorial constants.
Use the module in this order; do not simply report that it was read:

1. Use the applicable method guidance; record the decision, not a recital of table rows.
2. State the first representative part/region, editable controls, protected state and
   agreed checks. If essential dimensions, movement or tolerances are missing, ask;
   do not invent them to make a procedure executable.
3. Build only that test in approved scope and inspect its named captures. Change one
   control family at a time while diagnosing; record expected versus actual behaviour.
4. Report **proceed / revise / stop**, the evidence for that decision and what remains
   unverified. An absent required feature blocks progression. A method change requires
   evidence and approval under the shared rules, not just another method-table row.

If no module fits, state the gap and propose a method; do not force an unrelated recipe.
Record test evidence and coverage in `docs/3d-authoring-notes.md`. A pass validates only
the tested method and conditions; do not remove a module's unvalidated label merely
because its links, prose or one mesh-health check pass.

These modules are project-authored guidance, with related reading identified where used;
no upstream scripts are installed and no upstream test result transfers to them. External
collections considered for routing/procedure design are
[Blender Expert](https://github.com/edemaistre/blender-expert-skills),
[EL4CTEO](https://github.com/EL4CTEO/blender-skills),
[RobLe3](https://github.com/RobLe3/cc-blender-skill) and
[Blender Agent Studio](https://github.com/ifBars/blender-agent-studio).
Existing adapted resources retain their attribution in `THIRD_PARTY.md`. The modules
do not install another router, change the MCP backend or replace project safety rules.


## Optional workflows and tools

For related props, materials, sprites or UI-art states, read
[asset families](../../.opencode/skills/gummy-3d-authoring/references/asset-families.md). For approved dynamically lit sprites or
animated sheets, also read [sprite normals](../../.opencode/skills/gummy-3d-authoring/references/sprite-normals.md). Both are
**unvalidated** source-production guidance, not installed tools or authorization for
game integration. They supplement construction/material gates, not replace them.

Load focused references only when the task needs them. Asset-specific trial histories,
revision status and benchmark numbers belong in project reports, not general authoring
instructions. A historical builder is neither a required starting point nor proof that
its construction method suits a new asset.

The experimental unified entry point is `tools/asset-pipeline/pipeline.py`, driven
by JSON jobs (inspect/uv/bake/hybrid/check/render/export/verify). See the pipeline
README for exact supported graph patterns and limitations. `hybrid` keeps source
parts/material classes and combines dedicated panel bakes with repeated UV image
sampling for plain plastics; it is not general shader conversion. Export still
delegates to the existing approval gate. New generic regression fixtures live in
`tools/asset-pipeline/fixtures/`; old phase scripts stay in `tests/`.
Vertex-distance preservation and an inspected Blender candidate are not clean-import
or destination-engine verification. Inherited zero-area geometry remains a delivery
finding, not permission to change a protected source or waive acceptance.

For shared-atlas delivery copies, selectable atlas/guide resolutions and staged publication,
follow [references/atlas-delivery.md](../../.opencode/skills/gummy-3d-authoring/references/atlas-delivery.md). Existing source UVs and
materials stay protected; failed unwraps are diagnostics, not accepted deliveries. The default
generation guide is 1280²; resolution changes do not authorize a different UV layout.

For a paint template or UV wireframe delivery, follow
[references/uv-template-delivery.md](../../.opencode/skills/gummy-3d-authoring/references/uv-template-delivery.md): decode saved images,
record the exact source/UV fingerprint and inspect a same-resolution albedo overlay. A PNG
header or old filename is not evidence that a guide is valid or current.
For island ids, zone/id maps, per-island masks and label manifests, follow
[references/uv-island-export.md](../../.opencode/skills/gummy-3d-authoring/references/uv-island-export.md): render per object, never
merge separate UV spaces, and never invent island part names.

For automatic semantic-naming experiments, use
[references/semantic-uv-prototype.md](../../.opencode/skills/gummy-3d-authoring/references/semantic-uv-prototype.md). The prototype
prepares multi-view, face-grounded evidence and sampled shell pairing; its 24-island vehicle
development benchmark is not a general naming guarantee or an unattended vision service.
For same-asset held-out checks, `scripts/uv_semantic_holdout.py` separates prediction freezing,
numbered capture and scoring; `scripts/test_uv_holdout.py` tests scoring in plain Python.
Keep failed holdout results and do not retune or relabel them into a reported pass.

Additional tools: `scripts/png_report.py` (read-only structural check),
`scripts/test_png_report.py` (pure Python fixtures), `scripts/uv_template_export.py`
(approved background export of template/layer/overlay/manifest) and
`scripts/uv_island_export.py` (per-object id/zone maps, labelled overlay, island manifest
and binary masks with dilation; deterministic ids, non-zero exit on failed validation) and
`scripts/uv_label_review.py` (numbered review sheet plus a proposed-name JSON template; a human
must review it before `--names` is used). Project-local `tools/asset-pipeline/scripts/capture_review.py`
provides staged solid/material/final captures with render-state restoration,
`check_evidence.py` validates pose/frame/hash/fingerprint evidence, `check_interface.py` is an
experimental local signed-surface diagnostic, `construction_gate.py` validates brief/ledger
and source-bound evidence (required by detail/delivery and delivery exporters), `check_shape_gate.py` is a read-only bounds, hinge, modifier and default-scene hygiene
gate, and `export_approved_asset.py` is the gated GLB export entry point.
`reference_sheet.py` crops explicit view rectangles, enforces one shared scale and builds
locked, render-hidden reference planes; it does not detect views or infer dimensions.
`run_comfy_workflow_qwen_image_edit.py` runs job-driven Qwen Image 2.1 image-edit jobs
(UV template as image 1, references after it) against the ComfyUI HTTP API;
`run_comfy_workflow_stable_materials.py` does the same for StableMaterials map sets. Both
are dry-runnable and write a manifest; neither starts or reconfigures ComfyUI.
**ComfyUI contract:** a job JSON plus an **API-format** workflow, dry-run before
submission, server passed with `--base-url` or the job's `base_url`. Workflows live in
`tools/asset-pipeline/workflows/`, jobs in `tools/asset-pipeline/examples/`. Workflow
format, prompt-length limits, the colour gate and map-application procedure are in
`docs/comfyui-materials.md`.

For requested export verification, use
`tools/asset-pipeline/scripts/verify_asset.mjs` with the workflow in
`tools/asset-pipeline/README.md`. It links node/Python GLB inventories, the pinned
Khronos validator, a disposable clean import and a standalone three.js preview. Validator
conformance, preview compatibility and human visual inspection remain separate claims;
the preview does not modify the game loader or authorize integration.

Fixture passes establish only their tested scope, not arbitrary-asset support or user
acceptance. Preserve high-resolution material sources and choose delivery resolution
from the closest intended views. Atlas size reductions do not prove adequate texel
density, and a successful bake does not prove faithful transfer of every channel.

For the standalone UV sheet renderer, gate and optional per-chart repair workflow, follow
[references/uv-layout-extractor.md](../../.opencode/skills/gummy-3d-authoring/references/uv-layout-extractor.md). Those tools are
external and do not authorize game integration, material transfer or a bake.
The local line-guide CLI accepts `--placements` for explicit reviewed UV rectangles,
per-placement masks and source-object affine mappings; see its README. Raster island
coverage does not establish obstacle clearance. `tools/asset-pipeline/scripts/
process_sticker_sheet.py` supports closed-white-border sticker extraction and optional
colour grading, with saved-colour/alpha fixtures in `test_sticker_processing.py`.
It is not general segmentation; binary-alpha edges still need close-up visual review.

Read [references/asset-workflows.md](../../.opencode/skills/gummy-3d-authoring/references/asset-workflows.md) for hard-surface
modifier/shading choices, UV preparation, asset budgets and the local reporting tools.
Load the focused references when the task needs them:

- [references/assembly-verification.md](../../.opencode/skills/gummy-3d-authoring/references/assembly-verification.md): mandatory
  acceptance loop for assembly edits, structural completeness, connections, neighboring
  clearances and protected-surface preservation. Apply before calling a stage verified.
- [references/pbr-materials.md](../../.opencode/skills/gummy-3d-authoring/references/pbr-materials.md): Principled values, color
  spaces, ORM, normals, alpha, view transforms and glTF material export.
- [references/texture-baking.md](../../.opencode/skills/gummy-3d-authoring/references/texture-baking.md): high-to-low and
  procedural-to-texture baking, cages, map setup and the 5.2.2 bake API split.
- [references/openings-and-glazing.md](../../.opencode/skills/gummy-3d-authoring/references/openings-and-glazing.md): finding an opening's
  rim in a shelled body, building panes from it, sealing and occlusion checks, and the glass
  material choice. Load for windows, windscreens, lenses and grilles.
- [references/geometry-nodes.md](../../.opencode/skills/gummy-3d-authoring/references/geometry-nodes.md): editable parametric
  sources, fields/domains, modifier inputs, instancing and evaluated export.

These are selectively adapted from EL4CTEO/blender-skills for Blender **5.2.2 LTS**;
see [THIRD_PARTY.md](../../.opencode/skills/gummy-3d-authoring/THIRD_PARTY.md) for the pinned source and MIT notice.
This skill and `AGENTS.md` remain authoritative. Helpers never authorize repairs,
applying modifiers, exports or game integration. Do not install the upstream suite,
run its installer, or import its web compression defaults automatically.

- `scripts/asset_qa.py`: read-only evaluated topology and winding diagnostics; strict
  closed-solid default, explicit open-panel mode. No automated report proves correct
  outward/cavity orientation, attachment fit or reference fidelity.
- Repository `tools/asset-pipeline/scripts/mesh_diagnostics.py`: separate base and
  evaluated mesh-local reports; evaluation failures raise. Its Boolean helper retains
  operands and leaves modifiers unapplied. See the pipeline README for units,
  explicit ledger classifications/continuations and the disposable regression commands.
- `scripts/uv_report.py`: read-only world-space texel-density/UV-area report. Does not
  unwrap, pack, modify UVs or certify overlap/padding.
- `scripts/render_state_audit.py`: read-only visibility and material-slot audit — objects
  hidden in the viewport but still rendered, meshes without slots, object-linked slots, and
  shared mesh/material users. Reports state; it does not decide whether a hidden object is
  intentional.
- `scripts/glb_report.py`: standalone standard-library GLB inventory, exported vertex
  and triangle counts, materials and extension requirements. Not a glTF validator.
- `scripts/texture_inventory.py`: read-only resolved slots, image paths/packing/colour spaces,
  UV references and shader dependencies. Explicit targets via `run(objects=["Body"])`.
  Node groups remain unresolved; unconnected images are not deletion candidates.
- `scripts/test_helpers.py`: isolated synthetic regression checks; run only in a
  disposable background Blender, never the user's live scene.

Paths in this section and the supporting workflow are relative to this skill directory,
unlike project paths elsewhere in this skill. Load modules by absolute script path via
`importlib.util.spec_from_file_location` to avoid name collisions; do not execute fetched
remote code in Blender. Report limitations alongside results, not just a pass flag.


## Diagnosing appearance discrepancies

### Separate display, surface, UV and shader causes — unvalidated extension

Edit Mode may show the selected control cage and subdivided result crossing each other.
Compare the same region in Object Mode with overlays off before diagnosing duplicate faces
or self-intersection from patchy edit overlays. Then isolate uniform clay, checker mapping
and individual material channels under matched framing/lighting. A temporary subdivision
comparison can test surface approximation; restore the original setting and do not infer
a permanent geometry/budget change from it. No visible difference at one view rules out
neither other views nor untested causes. Do not merge, delete, recalculate normals or
reshape the source without evidence identifying the defective representation and region.
Preserve user mode/selection and restore temporary diagnostic state in `finally`.

### Material-boundary repair procedure

Identify the visible object and faces using picking/raycast or a restored flat-colour
isolation probe. Record face bands, material regions and shared boundary loops before
editing. Prefer existing rounded loops over face-centre thresholds; create a deliberate
boundary only where none exists. Do not add subdivision to disguise misclassification.
Inspect every affected corner close up and at an oblique angle. Compare geometry and
unrelated assignments (including rear surfaces) before/after. Preserve diagnostic colours
only in explicitly labelled scratch captures; restore source materials in `finally`.

`tools/asset-pipeline/scripts/check_material_boundaries.py` (repo-relative) is a read-only
advisory helper. Inside Blender use `snapshot(obj)` and `analyze(current, baseline,
allowed_faces)` with stable mesh indexing; alternatively pass snapshot JSON to its CLI.
It reports material regions, separating edges, endpoints/branches, single-face regions
and out-of-scope assignment changes. It cannot certify likeness, smooth curves or visual
correctness: even a closed toothed boundary can pass, and intentional accents can trigger
warnings. Tests: `python3 tools/asset-pipeline/tests/phase7/test_material_boundaries.py`.

### Generated-material colour gate

StableMaterials (and similar generators) is known to follow surface detail and tiling
more reliably than prompt colour. **Colour drift is an expected limitation, not a failed
prompt.** Raw base colour is therefore a candidate, never a delivery.

1. Inspect the raw base colour, a 3×3 repeat and a 50% offset. Record seam/tiling,
   stain/lighting and content findings separately from colour.
2. Compare the mean against an approved target palette. Record a review entry. Correct
   **only** when the failure is classified `colour_only`; do not use colour correction to
   disguise a seam, stain, lighting or texture-content defect.
3. Use the established deterministic correction (`tools/asset-pipeline/tests/phase5/
   review_colour.py`) with the explicit palette and review record. It applies bounded
   luminance modulation and replaces chroma while preserving generated detail; raw files
   and normal/roughness/height/metallic maps remain untouched.
4. Re-inspect the corrected tile and offset preview. Wire only the corrected base colour
   plus the reviewed detail maps; preserve stable alpha/transmission and do not alter
   unrelated channels to make the colour pass.
5. Record the raw/corrected hashes, review classification, correction report and
   limitations. A corrected map is not pure-generation evidence.

Rendered and viewport appearances can disagree for reasons unrelated to the material. Before
editing shader values, establish what a capture is actually showing.

1. Separate the visibility switches. `hide_set()` is viewport-only; `hide_viewport` (the monitor
   icon) is also viewport-only in 5.2.2 and does not prevent rendering. `hide_render` is the render
   switch. Reference planes, datum markers and superseded sources are routinely hidden in the
   viewport and still appear in every render and `look` capture. Reference and construction
   collections must set `hide_render = True`, and a render-only appearance problem starts with an
   audit of objects that are viewport-hidden but renderable.
2. Confirm the object and its slots, not just the material datablock: slot count, each slot's
   material, and `slot.link`. Object-linked slots override the mesh and can differ between users
   of the same mesh.
3. Map visible faces to slots with a probe: distinct flat colours on slots 0/1/2, a close-up
   render, then one colour on every slot. Geometry that keeps its old colour does not belong to
   that object at all. Restore the original materials in `finally`.
4. Judge metals under neutral lighting: Base Color tints their specular reflection, while the
   environment and roughness strongly affect appearance. Coatings need separate consideration.
5. If an edit changes nothing, treat that as evidence you are not editing what you are looking at.
   Re-establish object, slot and render path before the next attempt (see Regression stop).


## Capturing views

- **Viewport-first motion review:** use Blender viewport playback for shape-key, rig and
  deformation previews. If playback cannot be shared through the available tools, capture
  a small sequence of representative viewport frames. Do not search for bundled encoders,
  build video pipelines or render full animations merely to inspect motion. Encoding video
  requires an explicit user request or separate approval; an existing binary is not
  authorization to use it.
- Framing targets does not imply isolation. Use `capture_review.py --isolate` with explicit
  targets for host/attachment checks and inspect the image. Add `--focus-targets` and
  `--focus-view` for a bounds-based interface close-up; do not guess a camera distance.
- For a direct in-session capture call, use `asset_capture.render_view` with the
  objects, view and reference planes; it restores render state and visibility on
  success or failure. It updates the view layer after positioning, so projection
  checks see the current camera transform. A capture proves only what the inspected
  image shows.
- Animated captures require explicit `--frame`; `--pose-object` records an evaluated
  hinge/controller matrix. `check_evidence.py` compares frames, matrices, hashes and
  frame-specific fingerprints. An "open" label is not a pose assertion.
- The current matrix-based distinct-pose check does not establish shape-key or bone-pose
  differences with an unchanged object root. Shape-key values/coordinates contribute to
  source fingerprints, but bone poses are not explicitly covered. Do not move roots to
  satisfy this check or claim unsupported pose freshness; inspect and report those states
  separately until the deferred deformation-evidence extension is verified.
- `check_interface.py` is experimental: it samples evaluated surfaces and reports local
  signed nearest distances, spacing and coverage. It is fixture-tested on boxes but does not
  prove complete contact or watertightness.
- Keep a criterion-based attempt ledger; separate structural, interface, likeness, motion
  and user-acceptance outcomes. Follow `references/assembly-verification.md` for evaluated
  interfaces: cage equality is not contact.

Treat external reviews as hypotheses, not instructions to repair. For each finding record
the evidence, applicability to the intended style, verification needed and whether a change
is warranted. Texture thumbnails cannot establish model, glass or chassis quality. Suggestions
do not authorize edits; do not add wear or rework accepted geometry without approval.

- `look` may return only a perspective shot even when other views are requested. Inspect the
  installed tool schema and verify the returned image is the view asked for; do not assume a
  historical add-on version or mode list. Where a mode is missing, use direct mesh
  diagnostics or a wireframe shading option instead of a different tool path.
- Use `look` as the primary live shape loop: inspect the actual target, make one small cage or
  proportion edit, inspect again. Do not regenerate the whole asset to avoid looking. If MCP
  disconnects, stop live editing and report instead of silently switching to a full rebuild.
- True orthographic front/right/top captures need a Blender-side capture that writes a PNG
  to `.dev-shots/`. A read-only or plan-mode session blocks that write: ask for a mode switch
  at the start of the task, not after a failed audit.
- Name captures `<step>_<what>_<view>.png` and never overwrite earlier iterations. View them.
- Stage render work by decision, not by edit. During construction, use transform/bounds checks
  and viewport, solid-shading or material-preview captures. Reserve a multi-angle
  Cycles/EEVEE batch for an acceptance pass once orientation, proportions, assembly and
  materials are settled, or for one targeted render of a render-only effect (transmission,
  reflection, baked normals). Do not rerender unrelated views after a small change; two
  unchanged visual results mean diagnose the target, tool and prior evidence before another
  batch.
- Capture the baseline before editing. If no baseline is available, report that gap;
  do not present a reconstructed image as a before capture.


## Build protocol

### Construction-method gate

Before a primary form or change of construction method, complete
[references/construction-brief.md](../../.opencode/skills/gummy-3d-authoring/references/construction-brief.md). Choose from geometric
drivers, compare the main alternative and test the difficult section/interface first.
Reuse the brief for incremental edits; do not repeat it before every vertex movement.
Changing methods does not reset the criterion's attempt budget. The brief must also decide
which details are geometry and which are texture/material at the closest intended view.
This documented gate is not automated builder enforcement or a validated pattern library.

Within the authorised stage, block out and construct before detail, UVs or materials. Verify proportions,
openings and assembly in neutral solid views before adding bevel detail, paint or lighting.
Do not use polish to conceal weak construction. Plan major paintable panels, trim, glass,
material boundaries and seams for the intended delivery before multiplying components.

Classify the form first (fabricated hard surface, moulded product, or soft goods) and settle
primary silhouette, major sections, thickness and ground/contact before bevel detail, seams,
materials or delivery exports. Choose views that answer the question rather than a fixed
four-view ceremony: [stage review](../../.opencode/skills/gummy-3d-authoring/references/stage-review.md) owns progression, review
levels and evidence sufficiency. `capture_review.py` provides cheap neutral captures and
`check_shape_gate.py` an optional structural/freshness check with its own caller-specific
approval format — neither replaces an inspected result or creates user approval.

Approved **feature presence** matters more than a tidy surface: inspect views that actually
contain cavities, openings and recline, and treat a missing required feature as blocking the
next stage regardless of how finished the rest looks. In calibrated/reference modes a
visual comparison needs overlays; bounds and counts alone do not demonstrate the shape.

Prove one representative difficult part and its interfaces/evaluated topology before
replicating it. Prove UV/export transfer when that authorised stage becomes active,
not during a shape-only task. Inspect modifier-generated bevel corners,
Boolean walls, coincident/split surfaces, sliver triangles and generated UVs: a healthy base
mesh does not establish healthy evaluated geometry. Preserve good existing parts; a rebuild
is a proposed design choice, not an automatic response to a diagnostic failure.

1. One system or part per step (chassis, wheels, suspension, cage, body). Report and wait
   for the user's go before the next one, unless an approved chunk says otherwise.
2. Prefer primitives and modifiers (Mirror, Bevel, Solidify, Array, Subdivision Surface,
   Boolean) for mechanical forms. For moulded and soft forms, deliberate cage, edge-loop and
   proportional edits are appropriate when they establish the silhouette; avoid ad-hoc
   face patches and primitive stacking that substitutes for the required form. Model symmetric parts
   as one half plus a Mirror modifier with clipping on.
3. Prefer Bridge Edge Loops for interactive section construction. Procedural revolutions,
   lofts and sweeps are allowed when their profiles/paths remain editable and their
   generated loops have consistent connectivity and winding. Avoid ad-hoc face patches
   used to conceal a failed transition. Regenerating a derived mesh from preserved
   parameters is not a reset; preserve unrelated geometry, state and accepted features.
   Where a surface will later be smoothed, subdivided,
   remeshed or boolean-cut as a solid, build it as a closed manifold solid. Intentional
   open panels may be smoothed or subdivided, but must not be treated as closed volumes.
4. Cut openings (wheel arches, windows) with closed Boolean cutters kept unapplied in dedicated
   collections. Inspect existing collection-boolean consumers before adding operands; never
   put a new cutter into a shared collection merely because it is named `Cutters`. Apply only
   when approved. Build flares and trim separately so their edits do not reshape the shell.
   Glazed openings follow [references/openings-and-glazing.md](../../.opencode/skills/gummy-3d-authoring/references/openings-and-glazing.md):
   the pane is built from the opening's rim loop, not floated over it.
5. When salvaging a model, keep the parts that match the references. Hide, do not delete,
   a replaced shape and use it as a size guide.
6. Match the silhouette in solid shading before polishing glass or lighting. Keep
   construction objects, modifiers or reproducible parameters editable. Avoid repeatedly
   deleting and rebuilding the only model.
7. Change only the requested region. For percentage edits, record the baseline
   dimensions/parameters and preserve unrelated regions. Applied unions make isolated
   edits harder: preserve the source operands before applying them.
   For primitive-derived soft forms, inspect the unsubdivided cage, pole placement,
   edge spacing and deformation support across the intended cavity and protected
   crown/rim. Test cavity footprint and transition shape separately from depth and
   any raised cushion. During diagnosis, change one control family per checkpoint
   and compare matched front, side, top and oblique views. Measure protected-region
   movement using established correspondence; distinguish cage displacement from
   evaluated-surface changes. If pinching persists, inspect edge convergence and
   spacing before increasing subdivision or smoothing. Change construction only
   when a representative test demonstrates inadequate control.
8. Temporary hiding for isolation is diagnostic state: restore it in `finally`. Superseding
   or excluding geometry from delivery requires a component inventory, preserved source and
   silhouette/completeness checks; do not confuse temporary isolation with asset removal.


## Painting-guide and verification contract

- Preserve recognisable, contiguous main-panel charts. Thousands of fragments are not a
  substitute for the requested painting template. Keep small mechanical detail on separate
  sheets where approved, and distinguish artist outlines from triangulation diagnostics.
- Every island needs a stable ID for the delivered layout and an evidence-backed part name,
  or an explicitly unresolved tag. Put readable names inside major islands and use numbered
  leader-line callouts for tiny islands. No silently skipped tags; verify correspondence with
  the manifest, maps and masks. A populated name field or a rule-coverage score does not
  establish semantic correctness.
- Treat IDs as layout-derived. A repack or re-unwrap can reorder them; store island face
  sets and rebind names by exact face set after the layout changes. Preserve prior review
  state rather than silently reusing ID-keyed names.
- Report geometric overlaps and raster pixel conflicts separately. Adjacent-face sub-pixel
  slivers are not the same as texture collisions; do not call a guide clean from a triangle
  test alone, or generation-ready from a render alone.
- When both are requested, deliver the line guide and colored sheet as two views of the same
  layout. The colored sheet is a layout visualization, not an albedo, bake or material-
  transfer proof.
- Repair charts on a disposable copy with isolated operands fitted back into their original
  footprint. A full-sheet repack can improve coverage but will move labels and IDs; recheck
  label placement and rebind names afterward.
- Validate helper units, coordinate mapping, selection isolation and failure detection on
  known-good and deliberately failing fixtures before using results to accept or alter assets.
  One-off scripts remain experimental until their assumptions and limitations are tested.
- Use asymmetric test patterns, per-object and area-weighted errors, and matched before/after
  views. Report thin/sliver geometry separately without silently excluding it. Check both tail
  errors and coverage; a good median or a distant checker render cannot establish a pass.
- A gradient bake tests mapping only. It does not prove original albedo, roughness, metallic,
  tangent-space normals, transparency or coat survived. Verify required channels and material
  behaviour separately; classification as inherited degeneracy is explanation, not acceptance.
- Record actual saved image dimensions: declaring a 4096 atlas in metadata does not deliver a
  4096 image. Inspect saved guides against the user's readability reference before completion.
- When the user pauses Blender for headroom, do documentation/CPU-only work within scope;
  do not restart Blender or rendering without permission.


## Inspect the result

Use the [stage-review matrix](../../.opencode/skills/gummy-3d-authoring/references/stage-review.md) for targeted construction
views or stage-acceptance views. Compare against the reference rather than declaring
success from tool output. Use explicit targets so unrelated objects do not spoil framing.
Judge transmission, highlights and colour in separate material/rendered views. Keep a
clearly named shared material colour input when easy recolouring is required. Do not alter
unrelated lighting or cameras to conceal shape defects.


## Blender Python gotchas

- Query installed API/tool capabilities rather than guessing arguments or enums.
  Look shader nodes up by type (e.g. `BSDF_PRINCIPLED`), not localized names.
- Set rendered colour through shader inputs; `material.diffuse_color` alone only
  controls viewport colour.
- `bpy.ops` depends on mode, active object, selection and editor context. Establish
  those preconditions explicitly; prefer direct data access when practical. Do not
  swallow context errors with empty exception handlers.
- Do not parallelise dependent operations against the same live Blender scene.
- Make temporary capture setup exception-safe: restore visibility, display modes, selection,
  active object, overlays and shading in `finally`, even when capture fails. Use verified
  orthographic views or a tested camera-framing helper rather than repeated guessed
  perspective rotations. Inspect the capture before claiming the intended framing worked.
- BMesh element references become invalid after `bm.free()` or deletion of those elements;
  topology changes can invalidate retained references/indices. Copy coordinates or collect
  indices while valid, and refresh index/lookup tables after topology edits. `bm.to_mesh()`
  writes a mesh but does not itself free the BMesh.
- Scripts are not transactions: an exception can follow successful earlier edits. Inspect
  the actual scene before retrying, avoid double-applying changes, and restore temporary
  selection, visibility, material overrides and render/bake settings in `finally`.
- RNA mesh/UV references can become stale across mode changes, layer creation/removal or
  topology-changing operators, not only add-on calls. Retain stable names/identities and
  re-fetch the object, mesh and `ob.data.uv_layers[name]` after those transitions before
  copying or auditing. Revalidate index correspondence; do not retry with an old reference
  after `bpy_prop_collection`, `IndexError` or invalid-data errors.
- `uv.pack_islands` can reorder islands. Treat IDs, label placement and names as invalid
  after a pack; recompute islands and rebind names by face set.
- `autounwrap.smart_uv` has a blocking `execute` path for scripts, but the organic
  `autounwrap.unwrap` path is modal/panel-only. Do not fake a scripted call to a panel-only
  operator; report it and use a supported fallback.
- `bmesh.ops.create_cube(size=s)` has full side length `s` and spans ±s/2; object `scale`
  multiplies that. Decide the intended span, then verify evaluated world dimensions after
  updating the view layer/depsgraph before building anything on top of it.
- `v.co` is local. On a rotated or offset object, edit through `matrix_world` (or
  `matrix_world.inverted()`); a local Z change does not move the object vertically in world
  space. Moving a cylinder along its local Z slides it along its own axis.
- Keep one coordinate space per build script. A rim authored at world X 0.65 on an object
  sitting at X 0.53 lands 0.65 m outboard. Build one instance, print its world bounding box
  against the target, then replicate — do not rebuild all four and discover it afterwards.
- `hide_set` is viewport-only: hidden objects still evaluate into booleans and modifiers, but
  are excluded from `visible_get()` and from an export built on visible objects.
- Prefer complete connected components, isolated copies or closed operands for cuts. Partial
  face operations can leave T-junctions/open boundaries; verify selection, closure and neighboring
  topology and run the health check immediately. They are not inherently invalid in every case.
- A beveled curve with `use_fill_caps` can still produce coincident cap-rim vertices. Inspect
  evaluated boundaries and weld/fill only where approved and necessary; preserve intentional holes.
- Never start a clean scene with `bpy.ops.wm.read_factory_settings()` or `wm.read_homefile()`
  through the MCP bridge: both reload Blender's startup file, which **unregisters the MCP
  addon and drops the connection mid-call**. The scene may already be reset and the script's
  output lost. To build a new asset, delete the existing objects explicitly (or work in a new
  collection), and use `wm.save_as_mainfile` to a new checkpoint; a UI-driven reload is the
  user's call, not a scripted side effect.
- Keep MCP local-only. Do not enable paid generators/download integrations without
  approval or use Blender scripting to bypass repository file-edit requirements.


## Asset libraries (Poly Haven, Sketchfab, Poly Pizza)

Coverage is sample-level, not blanket asset or exporter certification; the exercised
providers and trial dates are recorded in `docs/3d-authoring-notes.md`.
Follow [references/asset-libraries.md](../../.opencode/skills/gummy-3d-authoring/references/asset-libraries.md) for provider-specific
arguments, transform preservation, animation checks and resource safeguards. Treat each
new library asset as untrusted until checked:

- Record source, asset id, author and licence beside the import. Check compatibility and meet
  each asset's attribution/redistribution obligations; different licences may coexist when compatible.
- Inventory the exact objects created by each import. Measure evaluated descendant-mesh
  bounds, not empty bounds; preserve imported scale and axis conversions under a placement
  controller rather than overwriting them. Validate one instance before duplication.
- A library asset is not evidence of reference fidelity. Do not substitute it for a part the
  user calibrated against a reference sheet without approval, and do not let a download
  stand in for a requested silhouette.
- Keep downloads inside the project's approved asset folder. `inspiration/` and third-party
  caches are never committed.
- Report the import as a separate delivery state: present in the scene is not integrated,
  textured, or verified in-game.
- `generate_3d` is a paid, single-object generator, not a scene builder. Confirm the target,
  provider and credit cost before using it; generated output still needs reference, topology,
  material, export and in-game checks.


## Cleanup and reuse

- Before cleanup, propose exact keep/move/delete sets, destination collision handling and
  rationale. Preserve accepted source checkpoints and important baseline/verification captures;
  retaining only the newest files or a fixed capture count is not sufficient justification.
  Follow the project's deletion approval gate and verify the resulting inventory afterward.
- Reusable guidance is a separate copied/generalized deliverable. Keep this project's adapted
  skill, instructions and local resources intact unless replacing them or adding an external
  dependency is explicitly requested and approved.
- When extracting tooling, remove project object names, material-zone maps, evidence
  fingerprints, absolute paths and project `.blend` assets; keep a small shared core and
  thin CLIs rather than shipping the project-specific exporter.
- Ship generic clean and deliberately failing fixtures, including a gate PASS/FAIL case,
  PNG structural checks and name-rebinding coverage.
- Decide the licence after provenance review. Do not bundle GPL or paid add-on code;
  optional tools such as Mio3 remain external and documented as optional.


## Step report format

Keep each step report short and in the same shape:

1. What changed (objects, modifiers) and what was deliberately left untouched.
2. Health: non-manifold edges, loose vertices, flipped faces, evaluated tri/vertex counts.
   For UV work, also report geometric overlaps, raster pixel conflicts, out-of-bounds UVs
   and degenerate triangles; name residual slivers instead of saying only "clean".
3. Dimensions versus reference in mm, with the measurement noise.
4. Files: saved path and dirty state, or "live scene only", or exported path.
5. Captures viewed (paths), and anything that could not be verified.

Stop at the agreed review boundary, not after each edit within an approved stage or
chunk. Follow `references/stage-review.md`. State when the result is live-only or not
integrated. Do not claim visual acceptance on the user's behalf.


## Sources

- MCP image/inspection modes: https://www.mcp-for-blender.com/docs/tools/look
- MCP Python and scripting pitfalls: https://www.mcp-for-blender.com/docs/tools/execute-blender-code
- Blender operator context: https://docs.blender.org/api/current/info_gotchas_operators.html
- Blender glTF export: https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html
- Structural validation: https://github.com/KhronosGroup/glTF-Validator

The silhouette-first, scoped-percentage-edit and capture-retention requirements
are project policies informed by the MSN figurine iterations. The calibration, build
protocol, health gate and regression stop come from the Raptor RC truck test. They are
project policies, not universal API rules.
Consult documentation matching the installed Blender version before using examples.
