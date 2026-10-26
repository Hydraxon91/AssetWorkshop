# Approved operators

The operator is the model/agent that actually performs the work. A parent
executing commands, a static review, or a different provider is not an
equivalent substitute when the user requested a named operator.

## Current operator

**`deepseek/deepseek-flash`** — DeepSeek V4.1 Flash 1017 (provider `deepseek`).
This is the only operator currently approved for this workspace.

| Role | Status with the current operator |
| --- | --- |
| Parent / planner / adjudicator | Approved |
| `scripted-disposable` modeller | Approved for bounded, ready-operation passes |
| `review-only` text review | Approved |
| `reference-reviewer` (image inspection) | Only if the configured plan passes images to the model. Otherwise the reviewer must return `BLOCKED`; use a human or a vision-capable model. A configuration probe did not establish image capability; verify with one supplied image before assigning an image-dependent review. |
| `mcp-edit` live scene editing | Parent-owned exception only; subagents are not approved for live editing |

If a model variant is used (for example a reasoning variant), record the exact
suffix in the brief and result. Do not silently substitute a variant, provider
or model.

## Historical / unavailable identifiers

These appear in older records and must not be read as current:

- `opencode-go/deepseek-v4.1-flash`
- `opencode/deepseek-v4.1-flash-free`
- `refuseless/deepseek-v4.1-flash-abliterated`
- `deepseek-v4.1-flash#low` (OpenCode Go shorthand)

They may be retained as historical evidence, but a new brief or result must not
claim they were used unless they actually were.

## Rules

1. A brief names the exact operator ID. A brief that says only “DeepSeek” is
   incomplete.
2. A result names the operator and separates **toolchain execution**, **operator
   operation**, **visual quality** and **user acceptance**. Parent execution is
   not operator operation.
3. Changing the operator needs explicit user approval and a new brief. Do not
   switch providers to work around an availability, permission or quality
   problem.
4. An agent frontmatter `model:` must match the approved operator for that role,
   or the parent must pass the operator explicitly and record it. A pinned agent
   model that differs from the brief is a blocker, not a preference.
5. Model availability is not capability evidence. A successful response shows the
   model was reachable, not that it can operate the pipeline or judge an asset.

## Related authority

- Execution modes: [`docs/execution-modes.md`](execution-modes.md).
- Live ownership: [`BLENDER_OWNER.md`](../BLENDER_OWNER.md).
- Current benchmark/result: [`docs/reusable-asset-pipeline-test/results.md`](reusable-asset-pipeline-test/results.md).
