# Execution modes — scripted Blender vs live MCP

This is the single authority for choosing how Blender is driven in this
workspace. `AGENTS.md` owns safety and authority; this page owns the mode choice.
A brief that does not name an execution mode is incomplete.

## Default

**`scripted-disposable`.** Live MCP is not a construction default. Use live MCP
only when the subject is the user's actual live/unsaved scene, or for one
explicitly authorized scoped edit. A stronger model does not change this: better
reasoning buys better scripts and better inspection, not an untimed edit of the
user's open session.

## Modes

| Mode | Use when | Blender | Evidence | Who may run |
| --- | --- | --- | --- | --- |
| `review-only` | Judging supplied images, captures or reports; no scene access | None | Supplied evidence only; no Blender ownership | Reviewer |
| `scripted-disposable` **(default)** | Saved `.blend`; unproven native geometry; repetition; measurement; UV/bake/export; any batch | Owned `--background --factory-startup` process, time-limited, hashed | Staged checkpoint / check / capture; script and input hashes | Parent or modeller |
| `mcp-inspect` | The user's live/unsaved scene, viewport, selection or current filepath is the subject | Live MCP, **no mutation** | Session note + screenshots/metadata; never promoted to final-saved evidence | Parent only in the current harness; subagents receive no MCP tools |
| `mcp-edit` **(exception)** | One scoped visual change that cannot be judged from a saved copy, with explicit user handoff | Live MCP `execute_blender_code`; one change, inspect, then save-as | Before/after captures + saved checkpoint + ownership record | Parent only in the current harness |

## Decision order

Use the first matching line:

1. Is the subject the user's live/unsaved scene or viewport? → `mcp-inspect`.
   If a change is needed, stop and obtain an `mcp-edit` handoff.
2. Is the task only judging supplied evidence? → `review-only`.
3. Is it unproven native geometry, a difficult junction, repetition,
   measurement, UV/bake/export, or any batch? → `scripted-disposable`.
4. Is it a parameter-only change to a frozen operation or recipe? →
   `scripted-disposable`, using the reviewed CLI/runner and no new scripts.
5. Otherwise stop and ask. Do not improvise a mode.

## Rules

- **Name the mode.** The brief must state the mode and the exact entry point.
  Generated runner plans carry `execution_mode: scripted-disposable`;
  `review_worker` rejects any other value. Live modes are parent-owned
  checklists, not runner plans.
- **Unproven native geometry is scripted first.** Boolean, BMesh,
  `from_pydata`, remesh and similar operations go to an owned disposable
  process with reviewed input, preflight and a timeout before any live use.
- **`mcp-inspect` is read-only.** Use the tools listed in
  [`docs/mcp-tools.md`](mcp-tools.md). Do not use `execute_blender_code`,
  `open_mainfile`, export, bake or UV operations in this mode. Subagents in the current
  harness receive no MCP tools: MCP is reached through the broad `execute` transport,
  which the modeller denies. Do not grant `execute` merely to obtain read-only tools;
  it also exposes mutating tools. A future harness that enforces per-tool MCP
  permissions must be tested before this rule changes.
- **`mcp-edit` preconditions.** Record the current `BLENDER_OWNER.md` line,
  actual filepath and dirty state, a recovery checkpoint, one intended change,
  a save-as name and a stop condition. No bulk loops, no file switching, no
  UV/bake/export. Restore temporary selection/visibility/transform state in
  `finally`. A tool timeout is unknown/in-flight execution, not cancellation.
- **One owner.** No live MCP while another worker or the parent owns the scene.
  The project card is not a machine-global lock; record the handoff wherever the
  other project keeps its ownership card.
- **Evidence is mode-specific.** Scripted work records script/input hashes,
  stage reports and checkpoint hashes. Live inspection records a session note
  and screenshots. Live evidence is not final-saved evidence unless a saved
  checkpoint and matched capture are produced. Do not promote a screenshot of
  an unsaved live edit to delivery evidence.
- **Reference planes.** For any supplied reference view, build a locked,
  uniformly scaled in-scene plane before shaping. In a scripted pass the plane
  must be built and saved by an approved stage. Until a reusable
  reference-plane stage exists, reference-led shaping that needs a plane is
  `mcp-edit` or an explicit development brief; do not silently eyeball a
  detached image.
- **Failure is a stop.** If MCP disconnects, stop live editing. If a scripted
  process fails or times out, inspect the partial state and reconcile the owned
  process before any retry. No automatic retry, rollback or substitute
  interpreter.
- **Do not use one mode to avoid the work of the other.** Do not use live MCP
  to avoid writing a reviewed script; do not use a script to avoid inspecting a
  visible change. The distinction is failure containment and feedback cadence,
  not programming language.

## Related authority

- Safety, ownership and approvals: [`AGENTS.md`](../AGENTS.md).
- Progression, review level and evidence matrix:
  [`references/stage-review.md`](../.opencode/skills/gummy-3d-authoring/references/stage-review.md).
- Current live owner: [`BLENDER_OWNER.md`](../BLENDER_OWNER.md).
- Actual MCP tool names: [`docs/mcp-tools.md`](mcp-tools.md).
- Approved operator: [`docs/operators.md`](operators.md).
