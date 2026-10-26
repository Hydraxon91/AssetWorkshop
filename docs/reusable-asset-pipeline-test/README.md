# Reusable asset pipeline — step-by-step plan

## Goal

Test whether the approved operator can select parameters and operate existing, reusable tools
to produce editable geometry, UVs and baked textures **without freshly generated
asset-specific implementation scripts**. A saved `.blend` alone is not success.

Status: **adapter technical fixture and parent-executed A/repeat-A/B benchmark
complete. Agent operation remains untested.** This document is the plan, not
evidence that any capability has passed. Initial workflow findings are in
[workflow-review.md](workflow-review.md); the completed source/evidence inventory
and recommendation are in [tooling-audit.md](tooling-audit.md). The audit itself
did not run runtime tests. [Fixed-panel smoke result](panel-smoke-result.md):
subsequently approved and passed; [Adapter result](adapter-result.md): user-approved
parent implementation and two-box geometry/UV/bake/reopen fixture completed. The
frozen agent-operated A/repeat-A/B benchmark remains untested; the parent-executed
run is recorded in [results.md](results.md). The historical
`opencode/...-free` and `refuseless/...abliterated` identifiers are not current;
see repository `docs/operators.md`. [Final historical review](final-code-review.md)
succeeded for its stated static-review scope, with no blocker for a same-revision
bounded parameter-only trial.

## Agreed direction and boundaries

- Modelling worker: `deepseek/deepseek-flash` (current approved operator; see
  repository `docs/operators.md`). Historical records named
  `opencode/...-free` and `refuseless/...abliterated`; those are not current.
  Parent plans and independently reviews; modeller executes bounded approved
  stages. For adapter development only, user explicitly approved parent-direct
  source implementation after worker write denial; the initial DeepSeek review and
  later parent-only fixes/testing are distinguished in the adapter result.
- Local asset processing: Blender 5.2.3, AMD RX 9070 XT, 32 GB RAM. Do not assume
  CUDA support. The language-model provider above is remote; local Blender and
  image generation do not make LLM inference local.
- ComfyUI and Modly/Hunyuan3D-2 multiview are already available, but neither is a
  prerequisite for the first test. Generated meshes do not prove editable modelling.
- Preserve the Steam Controller photos, preparations and reference checkpoint at
  `.dev-shots/steam-controller-test-01/`. Pause its custom cage work.
- No live Blender access without the ownership handoff required by `BLENDER_OWNER.md`.
  Prefer owned disposable processes for tests; never open over unrelated unsaved work.
- The user approved Step 1's read-only audit after creating this plan. Later
  execution/development scopes remain subject to the gates below. No installs,
  downloads, service startup, paid generation, commits,
  exports or destination integration are implied.

## What counts as reuse

Allowed in the frozen pipeline: parameter/config files, documented tool calls and
existing reviewed operations. Small orchestration adapters may be necessary, but
must be identified and counted as **new development**, reviewed and tested before
the benchmark. They must not hide per-asset geometry, UV or bake code.

An existing operation is a candidate, not automatically proven. Record its version,
supported Blender version, inputs, outputs, limitations and actual test evidence.
Repeatable inputs need equivalent geometry/UV/channel results, not byte-identical
`.blend` files or necessarily bit-identical GPU renders.

## 1. Audit existing tools — read only

Include the execution path as well as the tools. Identify duplicated preparation,
worker-authored wrappers and the reason a first tested result was delayed. Keep
observed failures separate from hypotheses about agent/model efficiency. Use the
existing runner where suitable rather than building another orchestration layer.

1. Inspect the local modelling operations/templates, UV and baking entry points,
   tests and known failures. Start with `tools/asset-pipeline/README.md`,
   `tools/uv-layout-extractor/`, and `tools/blender-safe/README.md`.
2. Inspect relevant implementation/tests only as needed. Distinguish unwrap,
   packing, auditing and UV-image extraction: these are different capabilities.
3. Compare a short list of public reusable tools where the local audit finds a
   concrete gap. Check source/docs, licensing, platform requirements and evidence;
   do not install or clone dependencies during this audit.
4. Produce one compact inventory: operation, exact entry point/version, evidence,
   editable outputs, AMD/Blender compatibility, status and missing capability.

**Output:** `tooling-audit.md` in this folder, with statuses demonstrated,
documented-only, incompatible, missing or unverified. Include a recommended route.
**Gate:** user selects the route and approves any bounded tool-development scope.
If suitable modelling templates do not exist, say so rather than restarting custom
controller scripting and calling it reuse.

## 2. Choose one complete, small benchmark

1. Select an asset the audited operations actually support. Suggested default:
   a simple four-legged stool with a separately selectable seat and legs, using
   exposed dimensions rather than reference-matched organic curvature.
2. Agree dimensions/units, required parts, useful origins/assembly control,
   normal desktop inspection scale, topology budget, texture resolution and maps.
   Suggested starting budgets: <=5,000 evaluated triangles and one 1024 texture
   set; these are proposals, not constraints until approved.
3. Set fixed parameters A and one variant B (for example seat width/leg height).
   Use neutral geometry views and a deliberately readable UV checker/material.
4. Set a complete small-run allowance, construction deadline and evidence reserve.
   Do not exhaust the allowance on planning or screenshots before health checks.
   Agree an early first-disposable-test milestone before assigning execution. For
   a ready, frozen operation the first execution action should be its invocation,
   following essential ownership/input verification. If the entry point is not
   ready, return a specific setup blocker rather than spend a modelling allowance
   developing it. Record model turns, runner operations and elapsed time separately;
   do not imply one measures the others.

**Output:** `benchmark-brief.md`, naming the asset, exact tools, inputs, criteria,
ownership, new output paths, recovery checkpoint and review boundaries.
**Gate:** user approves the benchmark and implementation scope. Body/form approval
precedes appearance. Export is excluded unless separately requested.

## 3. Close only the selected tool gaps, then freeze

1. Skip this step if the required operations already work.
2. For an approved gap, implement the smallest reusable operation/adapter, with a
   documented parameter interface and representative fixture tests. Test unproven
   native geometry in an owned disposable process before any live use.
3. Review and retain exact scripts, input/version hashes, test outcomes and known
   limits. Separate native construction, validation, save and capture commands.
4. Freeze the toolchain and input schema for the benchmark. Changes after this
   point invalidate the affected benchmark run and are recorded as development.

**Output:** tested, reviewed toolchain plus `toolchain.md` with exact commands and
versions. **Gate:** parent verifies readiness within approved development scope;
new dependencies or expanded scope go back to the user.

Before delegating execution, parent supplies a short handoff: authoritative input
and recovery baseline, approval/ownership, selected parameters and references,
exact reviewed runner entry point/next command, one expected artifact, early-test
milestone, final save/check reserve and stop condition. Worker verifies consequential
facts; it does not repeat the full audit, choose a new method or write wrappers.

## 4. Run editable modelling through the frozen interface

1. DeepSeek selects/sets the approved parameters and invokes the existing operation.
   It must not write new geometry code to rescue the asset.
2. Save a new checkpoint; verify affected base and evaluated geometry health.
3. Inspect whole-asset neutral views against the agreed stool/template criteria.
4. Check actual Object Mode selection, meaningful part transforms, origins,
   assembly control, dependency motion, evaluated retention and responsiveness.
   Names and transform matrices alone do not establish usability.

**Output:** editable model checkpoint, health/editability results and a small
inspected capture set. **Gate:** user accepts primary form before UV/appearance.

## 5. Run deterministic UV tools

1. Use the frozen unwrap/seam policy and explicit packing or preserve-layout mode.
   Do not silently rely on legacy defaults.
2. Audit global overlap, degenerates, occupied coverage and padding at the agreed
   resolution; inspect a checker for visible stretching and inconsistent scale.
3. Verify the UV operation preserved protected geometry, transforms and parts;
   reopen the saved checkpoint and compare actual corner UVs, not bounds alone.

**Output:** UV checkpoint, checker views and scoped audit report.
**Gate:** parent verifies technical and visible UV criteria. Failure stops the
pipeline for a tool/parameter decision, not ad-hoc per-asset UV scripting.

## 6. Apply a repeatable material and bake

1. Start with a fixed local procedural material containing readable colour,
   roughness and surface detail. This isolates pipeline transfer from AI-image
   generation quality. ComfyUI is a later optional experiment.
2. Use the frozen baking tool with explicit channels, colour spaces, normal
   convention, resolution, dilation and material assignment.
3. Compare source and baked appearance in matched views and inspect individual
   maps for empty outputs, channel mistakes, seams and projection errors.
4. Verify exact protected geometry/UV preservation and reopen the saved result
   with its packed or explicitly collected textures.
5. State the supported filtering/mip conditions. Native-resolution padding is
   not proof of lower-mip safety; existing seat tests found that distinction.
   Test the agreed reduced scales or explicitly leave them uncertified.

**Output:** baked editable checkpoint, maps, matched comparisons and scoped result.
**Gate:** user reviews appearance. No game-readiness or portability claim beyond
what was actually inspected and checked.

## 7. Prove reuse, not a one-off rescue

1. From a clean disposable scene, repeat A using the same frozen tools/config.
2. Run B by changing only the agreed parameters, not implementation code.
3. Check both runs against geometry, editability, UV and bake criteria. Compare
   repeat A semantically/numerically with tolerances recorded before execution.
4. Record failures, manual interventions, parent rescue, tool/code changes and
   observed calls/time/cost where available. Unknown costs remain unknown.

**Pass:** A, repeated A and B complete the agreed pipeline with no fresh
asset-specific implementation code or unplanned manual rescue. Tool reliability
and agent operation success are reported separately. A rescued asset can be
useful but is a failed agent-operated benchmark run.
**Output:** `results.md` with passed/failed/blocked/unverified criteria and evidence.
**Gate:** user decides whether this route is worth extending.

## 8. Return to the Steam Controller only after the benchmark

1. Map controller forms to demonstrated operations: curved shell, grip-to-bridge
   transition, separate controls and later UV/bake. Identify unsupported forms.
2. Do not claim the stool test proves curved-product modelling. If shell support
   is missing, propose a reusable curved-shell operation and one representative
   transition test as explicit new development, not another full-controller try.
3. Reuse the inspected reference checkpoint; add side-view authority as needed.
   Hold approximate 160 mm width as the scale anchor. Clarify the user's 120 mm
   'thinnest' measurement and 60–70 mm height axes before treating them as constraints.
4. Agree a new bounded body-only stage, with user shape approval before controls,
   UVs, textures or export.

## Evidence and stop rules

- Plan/audit/results documents live here. Binary sources, test runs, screenshots,
  reports and checkpoints go under a new ignored `.dev-shots/reusable-pipeline-test-01/`
  folder after execution is approved. Use unique filenames, not overwrites.
- Keep one current benchmark state record; link checkpoint identity, exact scripts/
  inputs, captures/view settings, failures and next authorized action. Preserve
  rejected attempts. Do not modify another asset's ownership/history to simplify this test.
- No concurrent Blender owners. Timeouts mean unknown/in-flight execution: reconcile
  the owned process before any retry. Never terminate interactive Blender automatically.
- Use the repository's existing review/repair rules and bounded handoffs, not a new
  orchestration framework. After two unsuccessful diagnostic approaches, return
  the blocker for a decision; a provider/model switch does not prove a tool fix.
- A failed gate leads to one concrete decision: change approved parameters, repair
  a reusable tool in explicit development scope, choose a supported simpler target,
  or stop. Do not conceal missing capability with another bespoke asset script.

## Next authorized action

**Audit, fixed-panel smoke, adapter fixture and parent-executed benchmark completed.**
The agent-operated benchmark remains untested; see [results.md](results.md). Next gate:
user decides whether to run the approved operator (`deepseek/deepseek-flash`) on the
frozen parameter-only benchmark and which UI/editability checks to add. Existing
Blender/local UV/bake tools were reused, with the new parameter/preparation/report
adapter tested on two boxes. No automatic provider change, new asset, controller
progression, install or export.
