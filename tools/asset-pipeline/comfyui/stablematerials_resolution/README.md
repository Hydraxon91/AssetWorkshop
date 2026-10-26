# StableMaterials Custom Resolution (Image)

A standalone ComfyUI extension that adds one node:

- **Node ID:** `StableMaterialsFromImageResolutionV1`
- **Display name:** Generate PBR (Image, Custom Resolution)
- **Category:** `StableMaterials/Resolution`
- **Outputs:** `basecolor`, `normal`, `height`, `roughness`, `metallic`
  (five 3-channel `IMAGE` outputs, in that order)

It conditions StableMaterials on one input image and requests an explicit
output resolution. It is intentionally separate from the existing
StableMaterials nodes and does not override their IDs, loader, or cache.

## Installation

1. Copy this whole folder (`stablematerials_resolution`) into
   `ComfyUI/custom_nodes/`.
2. Restart ComfyUI. The restart is user-controlled; this extension does not
   contact, restart, or install anything itself.

No new loader or model download is added. Use the existing
`LoadStableMaterials` node and connect its `SM_PIPELINE` output to this node's
`pipeline` input.

## Usage

Connect a single `IMAGE`, configure the resolution and sampling controls, then
send the five outputs to five `SaveImage` nodes (or another consumer). The
output order matches the original image node.

`width` and `height` default to `1024 x 1024`, must be integers in
`256..2048`, and must be multiples of `8`. The widget step is `8`; the original
text node uses `64`. Validation runs again at execution time, including for
bools, floats, out-of-range values and non-divisible values.

The output maps must be exactly `width x height`. If the pipeline returns any
map of another size, this node raises an error instead of resizing. This is
deliberate: resizing a normal map corrupts the encoded vectors.

## Conditioning routing

The node inspects `pipeline.__call__` at execution time:

1. **Explicit `image` parameter:** calls `image=<PIL>` and, when `prompt` is
   also explicit, `prompt=None`.
2. **Explicit `prompt` parameter, no explicit `image`:** calls
   `prompt=<PIL>`. This is how the published
   `gvecchio/StableMaterials` pipeline accepts an image; it converts the image
   into a semantic embedding inside the pipeline.
3. **Neither explicit parameter, or no inspectable signature:** raises an
   actionable error.

`**kwargs` is never treated as evidence of image support. Likewise, `width`
and `height` must be explicit parameters; the node refuses to pass them only
through `**kwargs` because a pipeline could silently use its own 1024px
default and return mismatched maps.

If a pipeline explicitly accepts `image` but also requires a parameter this
node does not send (for example `image_guidance_scale`), the resulting
`TypeError` is reported with an explanation. This node does not guess or
auto-populate unsupported parameters.

## Input handling and limits

- Exactly one input image is accepted. A batch larger than one raises an error
  rather than silently dropping images.
- RGB and RGBA are accepted. RGBA is converted to RGB and the alpha channel is
  explicitly discarded.
- Non-finite values (NaN/infinity) are rejected. Finite values are clamped to
  `[0, 1]` before conversion.
- The conditioning image keeps its original resolution. It is not forced to
  512px and there is no post-upscaling step.
- Generated maps are converted to `[B, H, W, C]` float32 tensors in `0..1`,
  using the original `pil_to_tensor` convention. A scalar/grayscale map is
  expanded to three RGB channels.
- Exactly one material is required from the pipeline. Empty or multi-material
  results raise an error.

The `256..2048` range is a validated widget range, not a promise of unlimited
resolution. GPU memory use and quality at 1024px and above are **unverified**
by the offline tests, and this README does not promise fast generation.

## Removed controls relative to the original image node

The original `StableMaterialsFromImage` exposes `image_guidance_scale` and an
optional text `prompt`. The published upstream
`gvecchio/StableMaterials` `pipeline.py` does not explicitly accept `image` or
`image_guidance_scale`; unknown keywords can be swallowed by `**kwargs` and may
not affect generation. This new node therefore omits `image_guidance_scale`
and the optional text prompt rather than advertising controls that may have no
effect. The original node and its registrations are not modified.

## Important caveats

- The actual published pipeline signature does not declare `image`. In that
  case this node routes the image through `prompt=<PIL>`, which uses the
  pipeline's semantic image embedding. That is **not** a pixel-perfect PBR
  reconstruction of the input; it is image-conditioned generation.
- A running modified pipeline may differ from the published source. This node
  adapts only to explicit, inspectable signatures.
- Requesting a resolution does not by itself guarantee visual quality. Always
  review the generated maps.

## Tests

`tools/asset-pipeline/fixtures/test_stablematerials_resolution.py` contains
offline unit tests. They use only the standard library plus in-memory stubs for
`torch`, `numpy`, `PIL` and `comfy.model_management`. They exercise resolution
validation, signature routing, **kwargs refusal, batch/finite checks, output
size enforcement, grayscale expansion and output dimensions.

Those tests are **not** an actual ComfyUI server generation and do not load or
run the StableMaterials model. They are a stub-level contract check only.

## Rollback

Remove the `stablematerials_resolution` folder from `ComfyUI/custom_nodes/` and
restart ComfyUI. The existing StableMaterials node registrations are
unaffected.

## Requirements

The extension uses dependencies already present in a working ComfyUI
StableMaterials setup: `torch`, `numpy`, `PIL`, and
`comfy.model_management`. It does not install or download anything.
