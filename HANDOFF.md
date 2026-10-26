# AssetWorkshop handoff

Updated 2026-10-26. Orientation only; AGENTS.md owns safety/authorization.

## Resume without stale instructions

1. Read `AGENTS.md` and [BLENDER_OWNER.md](BLENDER_OWNER.md).
2. Read the current card in `BLENDER_OWNER.md`, not historical sections or old
   ownership cards. The seat and truck records are historical. Before Blender work
   inspect actual live filepath/dirty state; a previous clean observation is not
   proof of the present scene.
3. Load `gummy-3d-authoring` and only current-stage routes. Choose an execution
   mode from `docs/execution-modes.md`; actual MCP tools are in `docs/mcp-tools.md`;
   the approved operator is in `docs/operators.md`. Do not import instructions
   from another repository or load a game-specific destination contract by default.

## Current state and next boundary

- **No active asset; owner none.** Last completed: stool A/repeat-A/B benchmark
  (parent-executed; the approved operator was not invoked). See the current card in
  `BLENDER_OWNER.md` and [results](docs/reusable-asset-pipeline-test/results.md).
- **Seat-01 learning pass is stopped**, after UV repack and basic procedural textures.
  Its checkpoint, UV source and repair history are historical. Earlier Stage 2b repair
  instructions are not current.
- Interactive Blender filepath/dirty state is unknown; it was not driven during these passes.
- **Tooling closeout:** fixed-sheet packer tested; legacy UV CLI is not integrated with it.
  Opt-in `pack:true` UV and `preserve_layout:true` bake CLI modes are now implemented
  and disposable-fixture tested. Historical seat bake mapping/mip bleed remain
  unverified; the seat was not rebaked. No delivery/export/integration claim.
  [Closeout and residuals](.dev-shots/seat-01/closeout-2026-10-26.md).
- Use [the fixed worker path](docs/review-session-workflow.md) for reviewed disposable
  stage plans. Trial02 completed without rescue; it tested a synthetic bevelled panel,
  not complex modelling reliability. Do not recreate its one-off trial01 wrappers.
- **Truck is parked.** Its delivery/UV/source provenance remains in the truck brief
  and the parked section of `BLENDER_OWNER.md`; do not resume its old material-preview
  instructions as the active task.

## Workspace map

| Path | Role |
| --- | --- |
| `.opencode/agents/` | Bounded modeller, read-only reviewer, and a non-production `probe-ladder` diagnostic |
| `.opencode/skills/gummy-3d-authoring/` | Stage/task router and on-demand references |
| `docs/execution-modes.md` | Scripted-disposable vs live-MCP authority |
| `docs/mcp-tools.md` | Actual configured MCP tools and read-only/mutating capabilities |
| `docs/operators.md` | Approved model/agent operator identities |
| `BLENDER_OWNER.md` | Current live-ownership card only |
| `tools/blender-safe/` | Static direct-mesh preflight and owned timed pilot runner |
| `tools/asset-pipeline/` | Experimental authoring/verification tools; inspect before use |
| `.dev-shots/` | Ignored sources, references, checkpoints and evidence |
| `docs/3d-workflow-review.md` | Historical evidence behind workflow changes and known limits |
| `contracts/` | Opt-in delivery contracts; no default destination for standalone authoring |

No commits/pushes, dependencies, services or integration are implied. Ignored binary
sources need explicit transfer; a repository clone does not recover them.

## Historical record — not current authorization

The full pre-cleanup truck-focused handoff is preserved locally at
`.dev-shots/workflow-cleanup-03/source-before/HANDOFF.md`. Its "next approved" material
preview is historical, not an active instruction for the seat or this cleanup.

[The 2026-10-23 watering-can handoff](docs/legacy/handoff-watering-can-2026-10-23.md)
is preserved unchanged. Its checkpoint, next actions and MCP-opening precautions
belong to that past task; consult current ownership/safety rules rather than treating
the archived handoff as a second active instruction source.
