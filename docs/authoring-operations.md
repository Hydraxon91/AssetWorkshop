# On-demand authoring operations

Use the skill's stage/reference policy as the authority, not historical game rules.
Choose construction from the shape, preserve editable controls, and prove a difficult
region before replication. Set fidelity/budgets explicitly. Separate visual likeness,
evaluated geometry health, assembly contact, motion, export and destination intake.

`check_evidence.py` validates pose/frame/hash freshness, not likeness.
`check_interface.py` samples mesh-to-mesh contact; it is NOT a delivery-contract or
game-intake checker. Nearest surface distance does not prove complete contact.
Validate contradictory measurements before repairing geometry. Preserve Boolean
operands and inspect evaluated results. A required feature missing blocks delivery.

Historical copied reports describe past trials, not current acceptance or portable
paths. Do not execute old jobs with absolute game-repository paths blindly.

## Delegation and efficient inspection

### Execution modes — scripted Blender and live MCP

Default: `scripted-disposable` (saved file, owned background process). Use saved,
parameter-driven builders for repeatable construction, and live MCP only for parent-owned
read-only inspection of the user's actual scene or a parent-owned approved scoped edit.
Subagents do not receive MCP tools in the current harness. Full policy:
[`docs/execution-modes.md`](execution-modes.md); actual tool names:
[`docs/mcp-tools.md`](mcp-tools.md). For a reviewed disposable stage plan use the
[fixed worker path](review-session-workflow.md), not another worker-written process
wrapper. Asset-local experiments/recovery scripts stay under `.dev-shots/<asset>/scripts/`;
reusable builders/tests belong in `tools/asset-pipeline/fixtures/`. Shared Blender
inspection/capture helpers belong in `tools/asset-pipeline/scripts/` (not the
repository-root preview `scripts/`). Never blindly rerun historical builders against
live state.

For reference-driven curved forms, prove exterior silhouette before introducing
wall thickness, detailed lip topology, UVs or export constraints. An exterior-only
prototype may intentionally have open boundaries; report those as expected at
this stage, not as a finished watertight asset. Retain a real editable profile/
cage and working derivation (for example Screw), not just a script and applied mesh.
Use a few low-dimensional candidates under identical framing, not repeated
whole-asset rewrites. Standard modifiers are permitted when appropriate; a method
ban needs an asset-specific reason. Parent briefs specify outcomes/protected state,
not unvalidated radius tables for the worker to follow blindly.

`tools/asset-pipeline/scripts/reference_compare.py` reuses `reference_sheet.py` axis/UV conventions and
provides one pixel frame for plane geometry, camera framing and contour overlays.
The asset-local reference record owns image/hash, crop, top-left pixel origin,
uniform scale, scale-authority landmarks, view assumptions and uncertainty. A
comparison must not silently independently rescale/translate or flip either image.
Validate landmarks and reference-only appearance before using shape comparisons.
Masked visible-contour scores are diagnostics, not proof of hidden geometry or
orthographic calibration of a perspective illustration. Keep thickness and cut/
opening checks separate until the outer form is settled.

For geometric diagnostics, identify exact feature sets before measuring: rim
planarity uses named rim rings/faces, not all vertices above a height threshold.
Record selected indices/counts and coordinate space. A contradictory broad fit
invalidates that measurement, not automatically the model. Distinguish radial
offset, normal thickness and projected versus in-plane opening dimensions.
Test reporting code on the actual data types (vectors are not scalars), and
restore temporary control edits in `finally`, including when capture fails.

Keep parent planning/independent review and one bounded modeller owner. Do not
introduce simultaneous geometry/shader writers or assume even inspection may run
against another owner's live scene. Briefs specify execution mode, targets,
baseline, protected state, evidence, diagnostic allowance and stop conditions.
Use the existing asset-local current record, not a second tracking system.

Inspect relevant target/dependency/protected state, not every unrelated scene item.
Return counts and anomalies first; page larger results (for example 10–20 relevant
objects), retaining full reports as linked artifacts. Batch related measurements
and repeatable calculations locally in Blender. Do not batch away visual decision
points or make a whole-asset regeneration script a substitute for inspected edits.

After two unsuccessful diagnostic approaches, return the blocker with expected/
actual evidence and attempted methods. Never reset repair history. Milestones are
baseline established → checks complete → evidence saved → stopped/handoff; these
are progress reports, not additional user approval gates. OpenCode's configured
model-step cap is not a timer and cannot guarantee cleanup if exhausted: stop early
enough to preserve state and report. Parent cannot retake Blender until stopped.

Save new-name source checkpoints; no automatic commits, resets, scene reloads or
discarding live-only data. On interruption inspect actual partial state first.
Filesystem edit permissions do not sandbox arbitrary Blender Python. Report mode
restrictions as procedural; only claim permission enforcement after testing it.

Validation: use synthetic disposable fixtures for restoration/evidence/preservation
and review permission rule ordering/config loading. Agent-policy changes require
a separately approved bounded behavior pilot before claiming demonstrated agent
reliability. ComfyUI remains DEFERRED; destination manifest/intake work still waits
for the destination owner's requirements, not local test success.

## Verified texture/UV recipe for a painted game asset

Learned on the truck asset (rounds 66–68); each step failed at least once before it
worked. Tools live in `pipeline/uv.py` and `pipeline/texture_composite.py`.

1. **Unwrap into a real 0–1 layout, then measure it.** `ensure_island_gaps()` shrinks
   islands about their own centres and reports a measured gap (or an explicit note when the
   mesh has no islands); `min_island_gap()` reports the gap in UV and pixels.
   Do **not** trust `bpy.ops.uv.pack_islands`: in background Blender it returned
   `FINISHED` while turning 0 overlapping island boxes into 53. `pack_islands_checked()`
   exists only to catch that regression.
2. **Report overlaps without a small cap.** `island_overlap_report()` returns total pairs,
   total px², the largest pair and an explicit `truncated` flag (default cap 200 000 pairs).
   A 64-pair cap once hid 72,744 pairs; if the flag is set, raise the cap and re-run rather
   than reading the number as clean.
   Evaluate the threshold at the intended texture size, not in raw UV units.
3. **Paint textures are tiled, livery atlases are not.** A generated paint map reads
   blotchy at 1:1 over an atlas; at ~8× tiling it reads as paint. A designed livery
   atlas is the opposite: 1:1 on the island layout, masked, palette-quantised.
4. **Mask and quantise generated art.** `composite_quantised()` keeps generator pixels
   inside island masks, erodes the rim, and classifies by HSV (white only when neutral
   and bright; orange only when saturated). Nearest-RGB snapping turns pale highlights
   into white hairlines.
5. **Bake the composite into delivery maps.** Base colour / roughness / normal at the
   delivery resolution, then assign a baked material; keep the procedural source.
6. **Export single-sided.** Enable backface culling on solid materials and leave only
   window panes double-sided; verify `doubleSided` in the GLB inventory, not in Blender.
7. **Verify with numbers plus an image.** GLB inventory (nodes, materials, images,
   extensions) and a render of the re-imported file. A successful export is not proof.

Reading image colours: load with `colorspace_settings.name = 'Non-Color'` to obtain the
stored sRGB bytes. The default sRGB conversion double-encodes and made orange average to
tan. Pure-Python tests: `tests/phase8/test_texture_tools.py`; Blender guard tests:
`tests/phase8/blender_uv_tools_check.py`.

### Wiring

The checks above are now the default path, not optional helpers:

- `python3 tools/asset-pipeline/pipeline.py uv --job job.json` unwraps, applies measured
  per-island gutters, and writes bounds + uncapped overlap totals + spacing into `uv.json`.
  Job keys: `unwrap`, `unwrap_margin`, `gaps` (default on with unwrap), `gap_margin`,
  `overlap_resolution`, `require_disjoint`, `max_overlap_fraction`. The verb exits non-zero
  when bounds fail, the overlap report truncates, `require_disjoint` is set and overlaps
  exist, or the fraction limit is exceeded. `pack_islands` is not called.
- The skill's `uv_island_export.py` now validates with a 1,000,000-pair cap and refuses a
  **truncated** result unless `--allow-overlap` is passed; its manifest records
  `overlap_pairs` and `truncated`. Per-pair px² totals stay in
  `pipeline.uv.island_overlap_report`, because computing them inside the exporter would
  compare every triangle of two whole islands.
- Blender checks: `tests/phase8/blender_pipeline_uv_check.py` (verb wiring) and
  `tests/phase8/blender_uv_tools_check.py` (guard behaviour).
