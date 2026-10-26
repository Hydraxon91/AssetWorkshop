# MCP tool map

The Blender MCP server is configured outside this repository. This page records
the tool names exposed by the current server so instructions do not cite a
different add-on version. If a name below is missing, stop and update this page;
do not invent a tool or fall back to an older protocol name.

**Harness note:** in the current OpenCode setup, MCP tools are reached through the broad
`execute` transport, not the individual `blender_*` actions. The modeller denies
`execute` and therefore has no MCP tools; live inspection is parent-owned. Do not grant
`execute` to a subagent merely to obtain read-only tools. Re-test if the harness exposes
per-tool MCP permissions.

## Capability map

| Capability | Tool | Effect |
| --- | --- | --- |
| Inspect the current saved-file summary | `get_blendfile_summary_datablocks`, `get_blendfile_summary_missing_files`, `get_blendfile_summary_of_linked_libraries`, `get_blendfile_summary_path_info`, `get_blendfile_summary_usage_guess` | Read-only |
| Inspect an explicit `.blend` path in a CLI process | The same five tools with `_for_cli` and a `blend_file` argument | Read-only |
| List objects / inspect one object | `get_objects_summary`, `get_object_detail_summary` | Read-only |
| Screenshot the current window / a named area | `get_screenshot_of_window_as_image`, `get_screenshot_of_window_as_json`, `get_screenshot_of_area_as_image` | Read-only |
| Render a viewport or thumbnail to a path | `render_viewport_to_path`, `render_thumbnail_to_path` | Writes a capture file |
| Navigate the UI to a tab/object | `jump_to_tab_by_name`, `jump_to_tab_by_space_type`, `jump_to_view3d_object_by_name`, `jump_to_view3d_object_data_by_name` | Changes UI/view state, not asset data |
| Look up Blender API/manual material | `search_api_docs`, `get_python_api_docs`, `search_manual_docs` | Read-only |
| Execute Blender Python | `execute_blender_code`, `execute_blender_code_for_cli` | **Mutating**; live edit requires `mcp-edit` authorization |

`execute_blender_code_for_cli` also mutates, but in a Blender CLI process with an
explicit `blend_file`; it is still not a sandbox and must be treated as an
editing operation, not inspection.

## Read-only inspection rule

For `mcp-inspect`, prefer summaries and screenshots. Do not use
`execute_blender_code` merely to read a value that a summary tool already
returns. Do not use `jump_to_*` to drive a visual review; it changes the user's
UI state and is not evidence.

## Legacy names

Older skill and handbook text used names from a different add-on version:

| Old name | Current replacement |
| --- | --- |
| `look` | `get_screenshot_of_window_as_image`, `get_screenshot_of_area_as_image`, or `render_viewport_to_path` |
| `get_scene_info` | `get_objects_summary` + `get_object_detail_summary` + `get_blendfile_summary_path_info` |
| `get_addon_status` | No equivalent. Confirm the connection with one read-only summary call; the server does not expose add-on status. |

Historical `references/asset-workflows.md`, `docs/legacy/` records and old
ownership cards may still contain the old names. Treat those as historical, not
as current tool instructions.

## Authority

- Execution-mode choice: [`docs/execution-modes.md`](execution-modes.md).
- Safety/ownership: [`AGENTS.md`](../AGENTS.md).
- Approved operator: [`docs/operators.md`](operators.md).
