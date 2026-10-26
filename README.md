# AssetWorkshop

Experimental standalone Blender authoring tools and an OpenCode workflow for bounded
modelling, independent review, UV layout, baking, inspection and export.

This is a work-in-progress authoring workspace, not a Blender add-on or a turnkey
asset generator. Historical examples may require local inputs not distributed here.
No destination game or integration is assumed.

## Getting started

- Python 3 runs the preview and standard-library checks below.
- Blender is needed for scene operations; configure its executable explicitly for
  disposable runs. Interactive MCP work also needs a connected Blender MCP add-on
  and your own OpenCode configuration.
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
Review scripts and historical job paths before execution. Automated checks do not
establish visual quality, editability or destination compatibility.

## Workspace map

- `AGENTS.md`: lean scope, preservation, ownership and evidence contract.
- `HANDOFF.md` and `BLENDER_OWNER.md`: current task routing and live ownership;
  the active asset is the standalone seat, not the parked truck.
- `.opencode/skills/gummy-3d-authoring/`: copied authoring skill and technical routes.
- `tools/asset-pipeline/`: copied experimental tools and tests, not all yet portable.
- `.dev-shots/`: ignored asset sources, historical builders, checkpoints and evidence;
  current seat agreement is `.dev-shots/seat-01/brief.md`.
- `docs/review-session-workflow.md`: current fixed worker/manifest/budget contract.
- `docs/migration.md`: migration status, remaining verification and provenance.
- `docs/pipeline-migration-inventory.md`: whole-pipeline file coverage and external prerequisites.
- `python3 launch.py --localhost`: serve the standalone preview without the game.

## What a clone does not contain

`.dev-shots/`, Blender sources and GLB/glTF exports are ignored. References,
checkpoints, evidence and some provisioned dependencies are local-only: links to
these paths document history but may not resolve in a clone. GitHub is not a
backup of those assets. `HANDOFF.md` and `BLENDER_OWNER.md` are workflow records,
not proof of another machine's current Blender state.

Blender MCP uses separately configured OpenCode settings; credentials and global
configuration are not distributed. No Git LFS is configured. The legacy skill name
is retained for compatibility; Gummy delivery is opt-in.

## License

MIT; see [LICENSE](LICENSE). Bundled components retain their own notices, including
`tools/uv-layout-extractor/LICENSE` and `UPSTREAM.md`.
