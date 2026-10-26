# AssetWorkshop handoff

Updated 2026-10-26. Orientation only; AGENTS.md owns safety/authorization.

## Resume without stale instructions

1. Read `AGENTS.md` and [BLENDER_OWNER.md](BLENDER_OWNER.md).
2. Read the active [seat brief](.dev-shots/seat-01/brief.md), not old ownership
   cards. Before Blender work inspect actual live filepath/dirty state; a previous
   clean observation is not proof of the present scene.
3. Load `gummy-3d-authoring` and only current-stage routes. Do not import instructions
   from another repository or load a game-specific destination contract by default.

## Active asset and next boundary

- **Seat-01 learning pass is stopped**, after UV repack and basic procedural textures.
  Current appearance checkpoint: `seat_01_uv_08_baked_review.blend`; UV source uv_05.
  See the seat brief's current-state card; earlier Stage 2b repair instructions are historical.
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
| `.opencode/agents/` | Bounded modeller and read-only reviewer prompts |
| `.opencode/skills/gummy-3d-authoring/` | Stage/task router and on-demand references |
| `tools/blender-safe/` | Static direct-mesh preflight and owned timed pilot runner |
| `tools/asset-pipeline/` | Experimental authoring/verification tools; inspect before use |
| `.dev-shots/` | Ignored sources, references, checkpoints and evidence |
| `docs/3d-workflow-review.md` | Evidence behind workflow changes and known limits |
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
