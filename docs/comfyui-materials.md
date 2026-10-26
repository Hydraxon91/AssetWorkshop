# ComfyUI materials and generated PBR sets

**Live testing: DEFERRED.** Offline runner tests, template preparation and the
StableMaterials dry-run passed locally; live generation, server/model availability
and generated-material quality have not been validated in AssetWorkshop. Do not
contact or start ComfyUI without a later approved test. Historical results below
are not fresh live-service acceptance.

**Update 2026-10-26:** a separately approved live Qwen 2.1 image-edit sticker run
succeeded for the soap-bottle label (`appearance/qwen/run-001`): one 1024² output,
110 s, status success, text intact. That validates only the Qwen image-edit path for
this label; StableMaterials live PBR generation remains deferred and unvalidated.

Operating notes for the StableMaterials and Qwen runners, and for applying generated
PBR maps in Blender. This file holds the details and the failure modes; `AGENTS.md`
and the authoring skill keep only the rules and point here.

## Precondition: UV islands before Qwen

**Project-wide rule, all workflows.** Do not generate a Qwen texture for an asset
surface before the UV work exists. The required order is:

1. Build or assign the UV layout for the surface.
2. Export a current named-island guide with the vendored UV tooling
   (`tools/uv-layout-extractor/` and/or `scripts/uv_island_export.py`).
3. Review the guide: island count, names, bounds, overlaps and the tags the Qwen
   prompt will use.
4. Use that guide/layout as the Qwen canvas (`<image1>`), naming each island and the
   detail it should receive.
5. Apply the returned image through the same reviewed UV layout; treat the raw
   output as artwork until that placement and the material wiring are verified.

A Qwen run against an un-unwrapped, packed-away or unnamed surface is not a valid
texture pass. It produces an unplaceable image and cannot certify the result. Stop
and return the UV step as a blocker; do not invent island names or paint around a
missing layout. This rule applies to one-off stickers, label films, livery atlases
and any future material workflow.

### Multi-island Qwen canvases

A single labelled atlas with many islands is not a reliable placement contract. In the
2026-10-26 RC-car livery pass, Qwen painted only one flank's mouth and wordmark, put the
mouth at the tail, and assigned endplate/panel colours to the wrong islands despite
explicit per-island instructions. Treat raw output as artwork: inspect every named island
on the model, prefer one focused canvas per side or part for direction-dependent art, and
repair the rest deterministically through the same UV layout. Keep a scripted
text/wordmark fallback for legibility.

### StableMaterials colour drift

Generated base colours can be far from the authored target (blue-grey "black", neon red).
Grade the base colour with a script against the authored look, keep the generated
normal/roughness/metallic maps, and do not regenerate solely for colour. Record the
grading and judge the result in the scene under neutral, non-blown lighting.

## Separate image-resolution node and user-tested API graph

The user reports successful image-conditioned generation with the separate node
`StableMaterialsFromImageResolutionV1` (not an independently reviewed map-quality
or output-size certification). Its implementation and installation notes are in
`tools/asset-pipeline/comfyui/stablematerials_resolution/`.

`tools/asset-pipeline/workflows/stablematerials_image_pbr_api.json` preserves the
user's API graph from `Stable Materials Image 2 PBR-2.json` in Downloads, with JSON
formatting normalized only. It requests Standard mode, 50 steps, 1024×1024, and
saves five maps separately: Advanced saver for sRGB basecolor, ordinary SaveImage
for normal/height/roughness/metallic, plus an optional combined preview saver.
Its wiring/configuration has been inspected; no new generation was submitted.

The graph requires the original StableMaterials loader/preview nodes, the separate
resolution extension and SaveImageAdvanced. Its LoadImage filename is an example
already uploaded on the user's server; change/upload the input before reuse. The
existing text runner does not automatically support this image-node class or the
Advanced basecolor saver. Do not claim runner compatibility merely because the
manual/API graph is valid. Load data maps as Non-Color in Blender. Eight-bit height
is suitable for a preview baseline, not guaranteed high-precision displacement.

## Runners

- `tools/asset-pipeline/scripts/run_comfy_workflow_stable_materials.py`
- `tools/asset-pipeline/scripts/run_comfy_workflow_qwen_image_edit.py`

Both take a **job JSON** (`tools/asset-pipeline/examples/`) plus an **API-format
workflow** (`tools/asset-pipeline/workflows/`). They are dry-runnable (`--dry-run`),
write a manifest, and never start, restart or reconfigure ComfyUI. Pass the server with
`--base-url` or the job's `base_url`.

## Workflow format

- **API format only.** A UI save (`nodes` / `links`) fails `validate_template`; in
  ComfyUI use *Save (API Format)*.
- **One `SaveImage` per map.** The StableMaterials runner infers output maps from
  `SaveImage` nodes wired directly to `StableMaterialsGenerate` outputs 0–4
  (basecolor, normal, height, roughness, metallic). A UI export that kept only a
  `SaveImageAdvanced` on the combined preview produces no usable maps.
- **Mode and steps can disagree** in an exported graph (e.g. mode `Standard`,
  steps 4). The runner overrides steps from the job; record both in the job.
- Output files are `<prefix>_<material>_seed<seed>_<map>.png`.

## Prompt limits

CLIP allows **77 tokens per prompt and per negative prompt**. A long comma-separated
negative list fails the job with `Sequence length must be less than max_position_embeddings`.
Keep each near 40 words. A run that fails this way still writes a manifest and is useful
evidence; fix the list rather than trimming terms that matter.

Pristine surfaces need the request in **both** prompt and negative prompt: dirty, dirt,
grime, oil, stains, dust, fingerprints, scratches, scuffs, chips, cracks, damage, wear,
aged, fading, mottling, blotches, plus lighting/shadow/reflection/highlight/vignette/
gradient/banding. Generation does not prove cleanliness — inspect the maps.

## Run outputs

Each run writes `run-manifest.json` (prompts, seeds, server details, per-map hashes,
failures) **and** a phase-5 compatible `summary.json` that `review_colour.py` consumes.
A missing `summary.json` means an incomplete run, not a file to hand-write.

## Colour gate

Raw base colour is a candidate, never a delivery. Correct only a `colour_only` finding:

1. Approve a palette (`palette.json`) with hex targets.
2. Record a review (`review.json`) with `inspected: true` and per-material
   `classification: "colour_only"` plus a note.
3. Run `review_colour.py` with `--run-dir`, `--palette`, `--review`, `--out-dir`,
   `--report`. Raw files are never overwritten.

The correction replaces chroma with the target and modulates luminance within ±6 %,
preserving generated detail. It cannot fix banding, shadows, stains, scratches or tiling.

Measured on the desk fan (`pristine-004`):

| material | mean before | target | delta before | delta after | detail preserved |
| --- | --- | --- | --- | --- | --- |
| shell_black | 0.31/0.32/0.33 | `#141416` | 0.417 | 0.0004 | correlation 0.90 |
| copper_metal | 0.86/0.68/0.59 | `#B87333` | 0.471 | 0.0026 | correlation 0.97 |
| blade_dark | 0.45/0.47/0.48 | `#2B2D30` | 0.497 | 0.0012 | correlation 0.97 |

When adapting a runner output by hand, the summary needs
`{"results": [{"material", "seed", "status": "success", "files": {"basecolor": {"path"}}}]}`.

## Tile reuse and corrected maps

A hybrid bake keeps tileable surfaces crisp by re-binding base colour to the **source
image** through `TileUV` instead of sampling the atlas. The bake therefore only carries a
colour-gated map when the material points at it. Use the job override rather than swapping
image datablocks by hand:

```json
"tile_materials": {
  "SM_shell_black": {"base": ".dev-shots/.../corrected/deskfan4_shell_black_..._basecolor_corrected.png"},
  "SM_copper_metal": {"base": "..._copper_metal_..._basecolor_corrected.png"},
  "SM_blade_dark": {"base": "..._blade_dark_..._basecolor_corrected.png"}
}
```

- A plain list of names keeps the old behaviour (raw source image).
- A missing override path fails the bake with `tile override map not found`.
- The bake report records `repeated_plastics.base_sources`, so the reviewed file is
  auditable in the candidate.

## Applying generated maps in Blender

- **Tiling recipe:** Object coordinates → POINT Mapping → FLAT/REPEAT images for base
  colour, roughness and metallic. Drive roughness through a linear Map Range so the
  hybrid bake recipe accepts the graph.
- **Normal maps need UVs.** Never feed object coordinates into a tangent-space Normal
  Map. Unwrap first, then drive the normal texture from `UVMap`. Start at strength
  0.30 and UV scale ~3; full strength bands along thin parts and shows UV seams.
- **Judge under a recorded view transform.** `AgX` lifts a near-black albedo into
  mid-grey; use `Standard` for prop reviews. A large soft area light also sheens a
  matte black into grey through broad specular — shrink the light and drop its energy
  before concluding a dark map is wrong.
- **Verify the file, not the render.** A corrected `#141416` map read back as
  `14 14 16` at the byte level while the render looked mid-grey; the lighting was the
  difference.
- **Probe discipline.** After a shader edit call `update_tag()` and
  `view_layer.update()`, then confirm with an isolation render and a flat-colour probe.
  A stale EEVEE shader looks identical to a wrong material.
- **Audit every slot.** Check `slot.link` and every mesh object's material, including
  parts you did not consciously assign. A forgotten part keeps the review clay and
  reads as a material bug through several renders.
