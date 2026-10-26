# Live Blender ownership

Project: `C:/Users/Hydra/Documents/GitHub/AssetWorkshop`.
Coordination record, not a technical lock or permission to drive Blender.
Current card only; superseded cards are archived at
`docs/legacy/blender-owner-history-2026-10.md`.

## Current state — soap-bottle appearance, Qwen sticker and exports complete (2026-10-26)

- **Owner: none.** No owned Blender process remains. No live MCP. The earlier
  interactive Blender session (PID 27664, unsaved) was not driven and is no longer
  running. The user's ComfyUI server was used through the HTTP Qwen runner only; it
  was not started, restarted or reconfigured.
- **Final appearance checkpoint:**
  `.dev-shots/frutiger-aero-bottle-01/soap-01/appearance/appearance_final.blend`,
  SHA256 `1a7fc773d028c3055cde1a121876a546b18d4f2d963cca943dc4546792bd7000`.
  Clear aqua glass, blue liquid, dark-teal pump/collar, chrome stem/top rim, bubbles,
  aqua studio world/floor and hero camera.
- **UV checkpoint:** `appearance/appearance_uv.blend`, SHA256
  `eb6f89f9bc4589dcf3f4355be09e62adc1587859c537f4645e2b4740ac8bb681`.
  All visible objects have UVs; label dedicated 0–1; body/label gates clean; pump
  has zero pixel conflicts but internal self-overlap from its Boolean topology.
- **Qwen sticker:** `appearance/textures/label_aquaria_qwen_v1.png`, SHA256
  `16fa13b589e3f83607f954d4d39f512fbbcf82d84cf553379d93bc121da16686`.
  Live Qwen 2.1 image-edit run `appearance/qwen/run-001`: one 1024² output, 110 s,
  success, 0 failures; text intact. The flat v3 label remains the fallback.
- **Exports:** `exports/aquaria_soap_bottle_v1.glb` (glTF 2.0, SHA256
  `737460eef6e6ce08ea89a60be83a1a47172a016b568d3b40826a284308bbcd5b`) and
  `exports/aquaria_soap_bottle_v1.fbx` (SHA256
  `65d83434da7eaed9b88766a88a2b9739107ecb6424ee0656e9e417e156ab8cde`).
  Eight meshes; FBX embeds label/normal/baked-roughness textures and uses alpha for
  glass/liquid; presentation and hidden pump sources excluded. Reimport report:
  `exports/verify-imports.json`.
- **Module status:** `references/construction-curved-products.md` marked verified for
  this recorded product pass, with explicit scope/limits; not a generator.
- **Final renders (bounded):** `appearance/final_renders/hero.png` and `label.png`;
  64 samples, AgX Medium High Contrast; no render suite.
- **Last completed:** Frutiger Aero soap-bottle shape, user pump correction, full UVs,
  materials, Qwen sticker and FBX/GLB exports. Record:
  `.dev-shots/frutiger-aero-bottle-01/soap-01/brief.md`.
- **Next authorized action:** user review of the exports. No export acceptance,
  game integration, rebake or further render suite without a new request.
  StableMaterials live generation remains deferred.
- **Last benchmark:** four-legged stool A / repeat-A / B parameter-only benchmark,
  executed by the parent. The approved operator `deepseek/deepseek-flash` was **not
  invoked**. This run proves tool reuse and parameter-only variation, not operator
  capability. Result: `docs/reusable-asset-pipeline-test/results.md`; brief:
  `docs/reusable-asset-pipeline-test/benchmark-brief.md`.
- **Editable master A:**
  `.dev-shots/reusable-pipeline-test-01/benchmark-stool-a-01/geometry/master.blend`,
  SHA256 `0add93c0d87da4cc5836000e0e8c8dd67f79490830644119727c181dd630563e`.
- **Baked A:**
  `.dev-shots/reusable-pipeline-test-01/benchmark-stool-a-01/atlas/baked.blend`,
  SHA256 `22c074d6149d0121d996608407d2ac10b9a573fdc58391cd97af92eaa27184c7`.
- **B master:**
  `.dev-shots/reusable-pipeline-test-01/benchmark-stool-b-01/geometry/master.blend`,
  SHA256 `447738c0608fb5dc…` (truncated in the prior card; re-hash before use).
- **A vs repeat-A:** equivalent within the declared tolerances (identical parts,
  packed `AtlasUV`, 6e-8 max delta on the legacy `UVMap` layer, all five baked maps
  pixel-identical). `.blend` bytes are not reproducible. B differs only in leg height,
  leg z-origin and seat z-origin.
- **Unverified:** live mouse/UI responsiveness, quantified shader-transfer error,
  lower-mip safety, embedded texture packaging, production furniture quality and
  byte-reproducible `.blend` output.
- **Seat-01 and truck:** historical. Do not resume their earlier instructions from this
  card; follow the archived ownership/history records if the user reopens them.
- **Interactive filepath/dirty state:** unknown and untouched.
- **Next authorized action:** user Gate A decision on the soap-bottle envelope.
  No detail, appearance, export, integration, install or live MCP is authorized by
  this card.

## Environment

- Windows Blender 5.2.3 LTS, explicit executable
  `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`.
- Execution modes: `docs/execution-modes.md`.
- Actual MCP tools: `docs/mcp-tools.md`.
- Approved operator: `docs/operators.md`.

## Card policy

Replace this card at each handoff; keep asset evidence/history in the brief's linked
records or `docs/legacy/`, not a growing stack of ownership cards. One live owner across
all projects that share this machine; follow `AGENTS.md` for handoff and timeout
reconciliation.
