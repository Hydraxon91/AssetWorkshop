# Whole authoring pipeline migration inventory

> **Archival copy inventory.** Records what was copied out of the game repository and what
> stayed external. Current authorization and live state live in `AGENTS.md` and
> `BLENDER_OWNER.md`; execution policy is `docs/execution-modes.md`; evidence mechanics are
> in `docs/review-session-workflow.md`.

This is file/dependency coverage, not end-to-end operational validation. Original
game-repo files remain preserved; no legacy workflow deletion is authorized by this
inventory alone. Destination-local repairs were preserved with copy-if-absent.

| Authoring route | Local destination |
| --- | --- |
| Shape/reference/construction, rigs, Geometry Nodes | `.opencode/skills/gummy-3d-authoring/` including all references/scripts |
| Materials, texture inventory, UV, atlas, baking | Same skill plus `tools/asset-pipeline/pipeline/` and scripts/tests |
| UV sheets, gate and optional chart repair | `tools/uv-layout-extractor/`, including licensing/provenance |
| ComfyUI StableMaterials and Qwen Image Edit | `tools/asset-pipeline/workflows/`, runners, examples, tests; `docs/comfyui-materials.md` |
| Capture, mesh/assembly/evidence diagnostics | `tools/asset-pipeline/scripts/`, fixtures and tests |
| GLB export, clean import and validation | `tools/asset-pipeline/`, local skill GLB helpers, `scripts/glb-inventory.mjs` |
| Standalone browser preview/capture | `tools/asset-pipeline/preview/`, `scripts/browser-harness.mjs`, standalone `launch.py` |
| Profiles, schemas, jobs and provenance | `tools/asset-pipeline/{profiles,schemas,jobs,examples}/` |
| Historical authoring evidence | `docs/3d-authoring-notes.md`, `3d-workflow-review.md`, `asset-pipeline-roadmap.md` |
| Legacy technical rules / destination-specific species context | `docs/legacy/agent-procedures.md`, `docs/legacy/species-template.md`; archival only, not startup instructions |
| Historical watering-can sources/reference/evidence (not the active asset) | `.dev-shots/asset-pipeline/{wateringcan_body_trial,deepseep_wateringcan}/` |

## Dependency disposition

- Relative JS imports into browser-harness and glb-inventory are now local.
- The original game launcher requires game source and WASM; it was NOT copied.
  The local launcher serves only this workspace, binds localhost and never boots
  the game. Existing preview commands may use `--asset` for a local GLB; the old
  MSN default is a historical game example, not a bundled sample.
- Preview retains the existing pinned CDN three.js import map (network required).
  Chromium, Blender, Node, ComfyUI services/models and the pinned Khronos validator
  package are external prerequisites, not vendored code. No installs, downloads,
  service changes, generation or dependency upgrades performed.
- All source tool/skill files are covered except caches/Finder metadata and UV
  extractor CI configuration. CI migration requires separate approval.
- Historical jobs and ignored source histories may refer to old absolute output
  paths, unavailable asset examples or external textures. They are preserved, not
  certified executable; do not run them unchanged. Only the current relinked
  verification checkpoint has independently verified local dependencies.
- Game runtime/source, global credentials/config and unrelated asset histories
  are not authoring-tool dependencies and were not copied. Global Blender MCP is
  shared infrastructure, governed by BLENDER_OWNER.md.

## Deferred verification

GummyBearTest was the confirmed destination **for the migration phase that created this
workspace**. No destination is assumed for current standalone authoring; a delivery
contract is selected only when a destination task requires one. Versioned manifest
implementation is **deferred by user decision until working assets exist**; it no longer
blocks authoring or migration. When it starts, requirements still must come from the
destination (checklist in `contracts/gummy/README.md`) rather than guesses or unapproved
game-repository reads. Local validation is not destination compatibility. Actual intake
must be tested separately in GummyBearTest.
Live ComfyUI testing is **DEFERRED**. Historical job dispositions are recorded in
`tools/asset-pipeline/jobs/README.md`; originals are unchanged.

Local offline functional checks have now run; see `docs/migration.md` under
"Expanded migration review (offline)". Material unit tests and graph preparation,
JS imports/Phase 2 tests (validator skipped), and preview HTTP serving passed.
The migration green flag is scoped to the routes inventoried above, not uncopied
asset histories or destination/game responsibilities. No source cleanup occurred.

User will verify ComfyUI generation, material/bake routes, browser previews and
GLB delivery later. Local path/import coverage does not prove these routes work.
Versioned delivery contract/intake validation remains a separate unfinished task;
game-required contracts/validators stay in the game repository. Historical docs
are not blanket guidance to load game rules in this workspace.
