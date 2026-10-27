# AssetWorkshop

Experimental standalone Blender authoring tools and an agent-assisted workflow for bounded
modelling, independent review, UV layout, baking, inspection and export.

This is a work-in-progress authoring workspace, not a Blender add-on or a turnkey
asset generator. Historical examples may require local inputs not distributed here.
No destination game or integration is assumed.

## Getting started

- Python 3 runs the preview and standard-library checks below.
- Blender is needed for scene operations; configure its executable explicitly for
  disposable runs. Interactive MCP work also needs a connected Blender MCP add-on
  and your own harness-specific MCP configuration.
- Node.js is required for JavaScript tools. Browser, glTF-validator and ComfyUI
  routes have additional prerequisites in `tools/asset-pipeline/README.md`;
  these are not installed automatically.

From the repository root:

```sh
python launch.py --localhost
```

Open the printed localhost URL. The preview needs an asset supplied separately;
this command does not launch Blender or generate one.

Lightweight checks (no Blender or generation service required):

```sh
python tools/asset-pipeline/fixtures/test_pipeline.py
python tools/uv-layout-extractor/tests/test_atlas_checks.py
python -m unittest discover -s tools/blender-safe -p "test_*.py"
```

Start agent sessions in this directory and read `AGENTS.md` before authoring.
Execution mode is chosen from `docs/execution-modes.md` (default
`scripted-disposable`); actual MCP tools are in `docs/mcp-tools.md`; the approved
operator is in `docs/operators.md`.
Review scripts and historical job paths before execution. Automated checks do not
establish visual quality, editability or destination compatibility.

### Agent harnesses

The canonical authoring skill is `.agents/skills/gummy-3d-authoring/`. Codex,
OpenCode and DeepSeek Harness document `.agents/skills` discovery. Claude Code
uses the small discovery adapter in `.claude/skills/`, which directs it to that
same canonical skill; `CLAUDE.md` directs it to the shared `AGENTS.md` policy.
Start sessions at the repository root and verify the skill is available in your
installed harness version. No `.dsh/skills` or `.opencode/skills` copy is needed.

Discovery is not proof of equivalent execution or safety: the configured agents in
`.opencode/agents/`, their permissions and the MCP transport are OpenCode-specific.
Other harnesses must independently establish equivalent permissions, delegation,
image handling and tool access before running a bounded stage; otherwise stop and
report the limitation. The approved operator remains governed by `docs/operators.md`;
changing harness does not approve a different model. See `docs/mcp-tools.md` for the
current OpenCode-specific MCP limitation. Compatibility is not yet runtime-tested
across all four harnesses.

## Workspace map

- `AGENTS.md`: lean scope, preservation, ownership and evidence contract.
- `BLENDER_OWNER.md`: current live-ownership card only; superseded cards are
  archived at `docs/legacy/blender-owner-history-2026-10.md`.
- `HANDOFF.md`: orientation and next boundary; it links to the current card rather
  than naming its own active asset.
- `docs/execution-modes.md`: single authority for scripted disposable Blender vs live MCP.
- `docs/mcp-tools.md`: actual configured MCP tool names and read-only/mutating capabilities.
- `docs/operators.md`: approved model/agent operator identities.
- `.agents/skills/gummy-3d-authoring/`: canonical authoring skill and technical routes.
- `tools/asset-pipeline/`: copied experimental tools and tests, not all yet portable.
- `.dev-shots/`: ignored asset sources, historical builders, checkpoints and evidence;
  the last completed benchmark is under `.dev-shots/reusable-pipeline-test-01/`.
- `docs/review-session-workflow.md`: current fixed worker/manifest/budget contract.
- `docs/migration.md`: historical migration record, remaining verification and provenance.
- `docs/pipeline-migration-inventory.md`: whole-pipeline file coverage and external prerequisites.
- `python3 launch.py --localhost`: serve the standalone preview without the game.

## What a clone does not contain

`.dev-shots/`, Blender sources and GLB/glTF exports are ignored. References,
checkpoints, evidence and some provisioned dependencies are local-only: links to
these paths document history but may not resolve in a clone. GitHub is not a
backup of those assets. `HANDOFF.md` and `BLENDER_OWNER.md` are workflow records,
not proof of another machine's current Blender state.

Blender MCP uses separately configured harness settings; credentials and global
configuration are not distributed. No Git LFS is configured. The legacy skill name
is retained for compatibility; Gummy delivery is opt-in.

## License

MIT; see [LICENSE](LICENSE). Bundled components retain their own notices, including
`tools/uv-layout-extractor/LICENSE` and `UPSTREAM.md`.
