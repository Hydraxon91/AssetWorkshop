---
name: gummy-3d-authoring
description: Create, edit, inspect and export Blender assets with scripted disposable Blender by default and live MCP for read-only inspection or an approved scoped edit. Use for 3D models, meshes, materials, UVs, baking, geometry nodes, reference matching and GLB work. Load only the active-stage references. Asset work does not authorise game integration.
---

# Gummy 3D authoring

## Minimum path for one bounded local pass

For a single scoped correction on an existing asset, read exactly these three and stop:

1. `AGENTS.md` (repository root) — safety, ownership, scope.
2. [stage review](references/stage-review.md) — progression, review level, evidence, budget/handoff.
3. The one construction reference for the form (see the routing table below).

Everything else is opt-in when a condition in this file says it applies. Do not scan the
31 references or load the handbook first.

Default execution mode is `scripted-disposable`. Live MCP is parent-owned read-only
inspection, or a parent-owned scoped-edit exception. Full policy: repository
`docs/execution-modes.md` (read when the mode is unclear or a live edit is proposed;
actual tool names are in repository `docs/mcp-tools.md`).

Follow repository `AGENTS.md` for scope, safety and approval. Paths below are
relative to this skill unless labelled repository-relative. This entry is a
router, not a requirement to read every linked document. Select the relevant
construction category and current-stage routes; follow cross-links only when
their stated condition applies. Do not preload unrelated categories or the whole
handbook. For example, a car starts with stage review and vehicle guidance; add
reference review for supplied references, curved-products guidance for smooth
bodywork, and assembly/material/UV/export guidance only as those tasks become active.

## Select the active stage

Read [stage review](references/stage-review.md) when starting/resuming asset
work: it owns progression, review points, the current-state record format and the
verification matrix. Actual live ownership and checkpoint identity are recorded in
the repository `BLENDER_OWNER.md` and the asset brief. For reference-led shaping or
likeness claims also read
[reference review](references/reference-review.md). Reuse the existing approved
agreement; do not restart a substantial brief for a local edit.

Agree scope, fidelity (stylized/gameplay-read, reference-faithful or reconstruction),
required cues, omissions, dimensions/axes, protected state and review points.
Propose purpose-appropriate geometry/material/texture budgets and viewing or
physical scale for approval. For game/runtime assets also establish likely
instances and motion needs. Do not invent missing decisions or assume game use.
Fidelity changes likeness expectations, not user approval or delivery quality.

Agree the destination explicitly; this generic workspace has no default game.
For runtime assets read [game asset contract](references/game-asset-contract.md)
and select the destination contract separately. Dense sources require an approved
purpose and budget. No destination authorizes integration by implication.

## Decision loop

1. Choose the execution mode from repository `docs/execution-modes.md` (default
   `scripted-disposable`). For a saved-file pass, verify the checkpoint path and
   hash and use the staged runner. For `mcp-inspect`, check `BLENDER_OWNER.md` and
   inspect the actual filepath, unsaved state, target identity, dependencies and
   shared data with the read-only tools in `docs/mcp-tools.md`. Do not open another
   file over unrelated unsaved work. Live editing is a parent-owned `mcp-edit`
   exception, not a default.
2. For shaping, build the reference plane first: for any supplied reference view, including a
   single side view, place a locked, uniformly scaled plane in the scene at a known
   model-units/px and judge the form against it. Use physical units only when
   established. Get scale authority from a declared dimension or explicit user
   decision; a plane does not prove source projection or physical calibration.
   Never stretch non-uniformly. If scale or view orientation is unknown, state the
   limitation and agree the substitute authority
   before building. Then inspect the reference and demonstrate the comparison
   relevant to the intended contour change. Distinguish observations, assumptions
   and user decisions. In a scripted pass the plane must be built and saved by an
   approved stage; until a reusable reference-plane stage exists, reference-led
   shaping that needs a plane is `mcp-edit` or an explicit development brief.
3. Preserve the editable cage/profiles/paths and operands, with a recoverable
   new-name checkpoint before destructive work. Make one scoped control change.
4. Inspect the affected result using the active task route. Shape work needs neutral
   reference comparisons; selection/origin maintenance does not require new reference
   calibration. Check affected health and protection, not a full delivery suite.
5. Decide from that evidence: improved, still mismatched, regressed or unverified.
   Name the changed contour and remaining discrepancy. Continue within the approved
   stage; stop at its agreed boundary or on a blocking failure.

Live MCP Python is for scoped, already-proven operations and inspection; unproven
native construction goes to a disposable process first. If MCP disconnects, stop
live editing. Scripts are not transactions: inspect partially applied state after
errors. Restore temporary diagnostic state in `finally`. Respect user resource pauses.

## Construction references — only the applicable category

Use the [construction brief](references/construction-brief.md) as a short decision
aid for a new form or strategy; its extended prompts are optional unless the task's
risks require them. Choose the method from the shape, not an existing generator.
Preserve editable controls and prove a difficult representative region before
replication. Existing category guidance is unvalidated, not an accepted recipe.

| Shape driver | Read |
| --- | --- |
| Fabric/contact/folds | [Soft goods](references/construction-soft-goods.md) |
| Moulded shells, lofts, sweeps | [Curved products](references/construction-curved-products.md) |
| Vehicle body and running gear | [Vehicles](references/construction-vehicles.md) |
| Architectural shells | [Buildings](references/construction-buildings.md) |
| Human proportions/articulation | [Humanoids](references/construction-humanoids.md) |
| Species silhouette/articulation | [Animals](references/construction-animals.md) |
| Rigid frames and furniture | [Rigid furniture](references/construction-rigid-furniture.md) |

For assisted stylized props also use [stylized game props](references/stylized-game-props.md).
Its limited human-assisted trial evidence is not autonomous-production validation.

## Specialist routes — load when that work becomes active

The preserved [authoring handbook](authoring-handbook.md) is an on-demand technical
index. Read a named section, not the whole handbook. For standalone Blender work,
do not assume or request a game-verification skill unless integration is separately
authorised; none is bundled here.

| Active task | Technical reference |
| --- | --- |
| Execution mode or live ownership | Repository `docs/execution-modes.md`, `docs/mcp-tools.md`, `docs/operators.md` |
| Existing-part identification or shared data | Handbook “Inspect before editing” and “Locating geometry before you touch it” |
| Selection, origins, assembly controls or editing lag | [Editability verification](references/editability-verification.md) |
| Shape health or repair | Handbook “Mesh health gate”, “Regression stop”; repository `docs/authoring-operations.md` |
| Attachment/interface | [Assembly verification](references/assembly-verification.md); handbook “Fitting attachments to host surfaces” |
| Proving a required surface is seen, not buried | Sampled exposure: repository `tools/asset-pipeline/scripts/check_exposure.py` (see `docs/exposure-check-stage.md`); contact and interface checks stay separate |
| Proving an edit did not delete the evaluated body | Evaluated retention: repository `tools/asset-pipeline/scripts/check_retention.py` (see `docs/evaluated-retention-audit.md`); authored preservation and `mesh_health` cannot see a modifier collapse |
| Reference-faithful/measured matching | Reference review, then handbook “Reference calibration” and “Direct comparison with reference planes” |
| Material-only change | [PBR](references/pbr-materials.md); preserve geometry and unrelated assignments; historical diagnosis notes only if needed (`docs/legacy/authoring-handbook-archived-sections.md`) |
| UV template/island delivery | [UV templates](references/uv-template-delivery.md), [UV islands](references/uv-island-export.md) only as requested |
| Qwen/StableMaterials texture generation | [UV island export](references/uv-island-export.md) first: name the current islands, review the guide, then use that layout as the generation canvas. Never generate before the UV work; applies to every workflow |
| Bake/atlas | [Baking](references/texture-baking.md), [atlas delivery](references/atlas-delivery.md) |
| Geometry Nodes | [Geometry Nodes](references/geometry-nodes.md) |
| Libraries/generation | [Asset libraries](references/asset-libraries.md); approval before paid generation |
| Rig/morph work | Handbook “Character and variant authoring” and “Deformation and export” |
| Export/transfer | Handbook “Geometry transfer verification” and “Deformation and export”; repository `tools/asset-pipeline/README.md` |
| Historical specialised tooling | Archived catalogue (`docs/legacy/authoring-handbook-archived-sections.md`); historical reference only, not current policy. Prefer current repository tools. |

## Review and delivery

For bounded delegation, use stage-review's worker brief checklist: define a save
deadline, review level/agreed “good enough” outcome, targeted evidence and reserve.
Return the pass's actual result, including failed/unverified criteria; do not add
perfection gates or pad completion with extra audits. Required safety and user
gates remain in force; budgets are adjustable parent-set defaults, not worker discretion.

Use the stage-review matrix, not a full delivery suite after every edit. Required
features must each be present with evidence before the next gated stage. A missing
feature is a defect, not a residual. Report topology, likeness, fit, preservation,
motion and user acceptance separately where relevant.

Helpers validate only their documented scope. A successful exporter does not
establish likeness or permission. Arbitrary MCP Python is not sandboxed by helper
approval files. Current suspect diagnostics and deferred repairs are recorded in
repository `docs/3d-workflow-review.md`; do not use their outputs to accept or
rebuild geometry pending independent verification.

At a review/handoff state the authoritative checkpoint versus live state, current
part/stage, evidence, pending decision, blocked work and next authorised action.
Distinguish live-only, saved, exported, standalone-verified and in-game-verified.
Do not claim game readiness from polygon counts or a Blender round trip. Stop at
the agreed boundary; passing checks never approves the shape on the user's behalf.
