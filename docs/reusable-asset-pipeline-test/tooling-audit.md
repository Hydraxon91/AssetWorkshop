# Tooling audit — 2026-10-26

## Result

**Reuse the local UV/bake tools and staged runner. Do not install another stack
yet.** A complete parameter-driven modelling → UV → bake interface is missing.
The missing work is a small explicit development stage, not another controller
modelling pass and not a reason to raise the model's step cap.

Audit scope: source/docs/tests and selected existing result records only. No
tests were run, no Blender process or live scene was accessed, no dependencies
were installed, and no source tools were modified. Historical pass records below
are not a fresh rerun, re-hash or visual certification of those assets.

## Local inventory

Paths below are relative to the repository root. Local version authority is Git
`21889f15dca81d851d4b549c845125575ad58b71` plus the exact source hashes below;
the initial scoped Git status showed no changes under the three audited tool
directories. Modules do not expose independent release versions.

| Capability / exact entry point | Status and evidence | Output / consequential limit |
| --- | --- | --- |
| Primitive/modifier modelling: Blender cube/transform/bevel operations, exercised by `tools/asset-pipeline/fixtures/review_panel.py` | Demonstrated in a historical synthetic trial; source inspected | Editable cube with an unapplied bevel. Dimensions and bevel values are hard-coded; CLI exposes only `before`/`after` and output, not modelling parameters. Not a stool or curved-shell template. |
| Other builders: `fixtures/build_wateringcan_profile.py`, `tests/phase7/build_equipment_case.py`, `tests/phase7/build_pebble_procedural_bake.py` | Existing fixed experiments; inspected, unsuitable as-is for this benchmark | Watering-can script has absolute macOS/asset paths. Equipment case takes texture paths, not general geometry parameters. Pebble fixture bundles construction/bake/export. Do not run unchanged or count modifying these scripts as parameter-only reuse. |
| General config-driven primitive assembly/template entry point | **Missing in inspected public local interfaces** | `fixtures/README.md` explicitly excludes geometry construction from `pipeline.py`. No supported stool generator was found in inspected builders. This is not a claim that every ignored historical script was searched. |
| Staged execution: `scripts/review_worker.py init/run/status`, `pipeline/review_runner.py` | Demonstrated historically for the fixed panel; source inspected | Background-only staged plans, saved checkpoints and hash-linked evidence. Existing preset is panel-specific. Generic plans accept reviewed scripts and arguments; they do not supply modelling operations. |
| Smart unwrap: `pipeline.py uv --job JOB.json` → `pipeline/uv.py::smart_unwrap` | Implemented; fresh Blender 5.2.3 run unverified in this audit | Uses Blender Smart UV Project with fixed 66° angle, job-controlled margin. Generic seam selection, minimum-stretch choice and user-directed artistic unwrap are not exposed by this job verb. Determinism across repeated runs/versions remains to be tested. |
| Shared packing: same `uv` verb with `pack:true` → `pipeline/atlas_layout.py` / `packing.py` | Demonstrated in historical atlas CLI fixture and reopen records | Packs charts globally using rectangles; reports global overlaps, UV degenerates and conservative box clearance. Can waste UV area/reject valid interlocking layouts. Shared mesh data must first be made single-user. |
| UV inspection: `tools/uv-layout-extractor/scripts/uv_layout_gate.py`, `uv_color_layout.py`, `uv_line_guide.py` | Implemented/documented; README reports Blender 5.2.2 testing, no fresh run | Read-only layout/gate images; **not an unwrapper**. Default gate is not the same as strict geometric rejection. Optional repair is separate and must run on copies. |
| Preserved-layout baking: `pipeline.py bake --job JOB.json` with `preserve_layout:true`, `export:false` | Demonstrated historically on a small CLI fixture, including reopen/corner records | CPU Cycles base colour/roughness/metallic/tangent normal + ORM. Retains parts and exact indexed geometry/UV corners. Requires opaque Principled materials, Object Mode, **no modifiers and single-user meshes**. Shader transfer/mips still need independent checks. |
| Derived atlas baking: same verb without `preserve_layout` → `pipeline/bake.py::bake_atlas` | Existing implementation/fixture history; not freshly validated here | Evaluates source modifiers, joins copies, unwraps a new atlas, then restores separate parts/parents. Rejects source `AtlasUV`; does **not** preserve a previously approved target atlas. Generated texture coordinates unsupported. Not a drop-in continuation of Step 5's frozen layout. |
| Material/checker assignment for benchmark | **No general job verb found** | Pipeline consumes source materials. Analytic/checker recipes exist inside fixtures, but choosing one does not create a reusable parameter-only assignment interface. A small frozen recipe adapter or prepared source material is needed. |
| Health/preservation/capture: `scripts/mesh_diagnostics.py`, `inspect_preservation.py`, `capture_review.py`, `pipeline.py check/render` | Existing implementations and fixture history | Reuse for scoped checks/captures. `review_blender.py` bundles a single-object panel contract, not arbitrary assembly/UI editability or shader-transfer validation. |

### Compatibility and licensing

- Local workspace code: repository MIT license; vendored UV-layout-extractor also
  MIT. Retain component notices; its `UPSTREAM.md` has no published URL/version.
- UV/packing/health operations do not require CUDA. Baker explicitly sets
  `scene.cycles.device = 'CPU'` (`bake.py:178–186`), so the recommended starting
  route does not depend on RX 9070 XT HIP setup. This audit did not test performance.
- Existing atlas fixture records use current Windows workspace paths. UV extractor
  claims 5.2.2 testing; current user target is 5.2.3. All selected operations still
  need a fresh target-version smoke test before freezing the benchmark.

## Existing evidence checked

- `.dev-shots/review-workflow-trial-02/parent_verification.json`: records 9/12
  runner operations, verified artifact hashes and matched capture metadata, no
  parent rescue, no live access. Model turns explicitly unmeasured.
- `.dev-shots/seat-01/tooling-tests/atlas_modes_04/PASS.json`: records global UV
  CLI packing, preserved bake CLI, rejection of unsafe dilation and bounds-only
  false positives, and interior roughness/metallic samples.
- Same folder `REOPEN_PASS.json`: records saved corner correspondence, global
  layout, texture existence and no duplicate baked objects.
- Source fixture `fixtures/test_atlas_modes_blender.py`: uses simple planes at
  128 resolution. These records do not prove a curved assembly or normal-detail
  transfer. Existing seat README also explicitly disclaims unrestricted mip safety.

## Public alternatives — targeted comparison

Read online on 2026-10-26; branches were not pinned or downloaded. These are
source/documentation findings, **not installed or locally demonstrated tools**.

| Candidate / sources | Relevant capability | Compatibility/license finding / decision |
| --- | --- | --- |
| [Infinigen](https://github.com/princeton-vl/infinigen), [pyproject](https://github.com/princeton-vl/infinigen/blob/main/pyproject.toml) | Real procedural asset/material library, stronger fit for template-driven generation than a chat-only addon | BSD-3-Clause top-level; dependency source inspection shows Python **3.11** and `bpy==4.2.0`, plus a substantial stack. Incompatible with simply loading it into the current 5.2.3 environment as specified; a separate approved environment could be evaluated. Windows/AMD performance and independent part editing unverified. Do not install for the first small test. An advertised individual-assets doc URL returned 404; no CLI was inferred from it. |
| [UVgami](https://github.com/danielboxer/UVgami), [README](https://github.com/danielboxer/UVgami/blob/master/README.md), [license](https://github.com/danielboxer/UVgami/blob/master/LICENSE) | Automated unwrap via OptCuts/xatlas CPU engines or PartUV GPU | Addon GPL-3.0; engines have separate terms. README requires engine download; PartUV segmentation is flagged non-commercial/NVIDIA licensed. CPU routes are plausible, but 5.2.3 compatibility and unattended API are unverified here. Defer unless native unwrap demonstrably fails the benchmark. |
| [Principled Baker](https://github.com/danielenger/Principled-Baker), [entry source](https://github.com/danielenger/Principled-Baker/blob/master/__init__.py) | Batch/combined/selected-to-active PBR baking and optional unwrap | Entry identifies **0.5.7**, Blender **2.83** minimum, GPL-3.0-or-later source header. This is not proof of 5.2.3 incompatibility, but compatibility is unverified. README warns of shared-material partial bakes and complex-shader limitations. Local baker already addresses the immediate need; no reason to replace it before a test. |

Search did not establish a ready compatible curved-shell template for the Steam
Controller. Do not turn this shortlist into a claim that none exists anywhere.

## Execution-path gaps that must not be hidden

1. **Modelling interface:** proven Blender operators exist; a reusable assembly
   parameter interface does not. A frozen adapter is development, not a benchmark
   success. Never ask DeepSeek to write a different asset script for every variant.
2. **Editable master vs bake geometry:** preserve-layout bake rejects modifiers.
   Preserve the editable master and explicitly prepare evaluated, independently
   editable bake copies, or choose modifier-free source parts for the first test.
   Do not apply modifiers to the only recoverable source merely to satisfy baking.
3. **Unwrap → bake continuity:** default baking unwraps again. Use approved bake
   copies → `uv` with explicit global packing → preserved-layout bake; otherwise
   the UV stage would not test the layout actually baked.
4. **Runner integration is partial, not automatic:** `review_runner.py:198–203`
   requires check reports with `status:'pass'` and matching `blend_sha256`.
   `pipeline.py check` reports `ok` rather than that exact fixture contract, and
   `review_blender.py` enforces a single object's expected-modifier conditions.
   Generic multi-part/UV/bake stages need explicit reviewed plan/report adaptation;
   a JSON plan alone does not bridge report semantics. Do not fake a pass or write
   wrappers during a modelling allowance. Imported dependencies are not exhaustively
   pinned by the current runner's main-script hash.
5. **UI editability and rendered transfer remain separate tests.** None of the
   above report schemas proves Object Mode responsiveness or good-looking bakes.

## Recommended route and next approval

**Recommended: stay with Blender's built-in operations and the existing local
UV/bake path. Approve one bounded setup/development batch before the agent trial.**

Proposed batch (not implemented/approved by this audit):

1. Re-run the existing fixed panel runner preset first, with no new geometry
   implementation. This verifies execution plumbing only, not parameter selection.
2. Add one small reusable primitive-assembly/config adapter: dimensions,
   transforms, named independent parts, optional live bevel and assembly root.
   A stool can be a data recipe, not a stool-specific geometry implementation.
3. Add only necessary frozen preparation: a known local procedural/checker recipe,
   evaluated bake copies retaining the master, and the minimal report/plan bridge
   to the existing runner. Reuse UV/bake/health/capture implementations unchanged
   where suitable; no new runner, environment, image service or UI framework.
4. Prove that whole small path on a minimal fixture before assigning DeepSeek the
   parameter-only A/repeat-A/B benchmark. Freeze exact inputs/tool hashes afterward.

For the first actual worker execution, parent hands over a reviewed operation
ready to invoke, not this entire audit. First execution action is the fixed test
after essential input/ownership verification. If setup blocks that action, stop
and report the specific blocker immediately; do not allocate another 30-turn design
exercise. Reserve a complete small result's check/save/capture allowance up front.

**Alternative with zero new development:** run the fixed panel trial and existing
atlas fixture separately. Useful tool smoke tests, but honestly report that no
parameterised end-to-end modelling benchmark has been demonstrated.

At the Step 1 gate, user chooses the recommended bounded setup or the zero-new-code
smoke-test-only route. No controller progression, installs or exports authorized.

## Exact inspected source identities (SHA-256)

These identify selected source files, not an exhaustive dependency lock:

```text
pipeline.py                    dcfbd9032d04178989ec33357e76782b5ee920c5febb36c9c8a299426223ebfe
pipeline/uv.py                 041b1f3b02abd41f5bef0736420d6c1fd40a1aa19e59bad4fbd5c2e33ec6efd4
pipeline/atlas_layout.py       b98646dbf7253ee7afca0d5aa1eef0028b78845d93c19e96dc4711906c7e8f2f
pipeline/bake.py               f651c4d1ecaabdfa9343801e9e6fe4e1daa2e64c07950a03f4dbc1564308c465
pipeline/review_runner.py      5703a0543add5a56a1a7058649122f6551b9c92620ec85027c259af523381343
scripts/review_blender.py      3aa4c578ed7efa950816e8bfdd5191d77ae67e8160afa269bb5ead50edcf535c
fixtures/review_panel.py       b42d19fae61542f26bb36f5f1de980b973bfa91310183c6c2c5ee7b5fe16d72a
```

## Handoff — STOPPED

Step 1 complete at source/evidence-review level; runtime compatibility, repeatability,
new parameter interface and end-to-end agent success remain unverified. Only plan/
audit documents changed. No current Blender ownership claimed; interactive state
unknown/untouched, all prior controller checkpoints preserved. Await route selection.
