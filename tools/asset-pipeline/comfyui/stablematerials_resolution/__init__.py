"""StableMaterials image-conditioned PBR generation at a custom resolution.

Standalone ComfyUI extension. Copy this folder into ``ComfyUI/custom_nodes/``
and restart ComfyUI. The original StableMaterials nodes are neither imported
nor modified; this module only contributes a new node ID.
"""

import inspect

import numpy as np
import torch
from PIL import Image

import comfy.model_management as mm


NODE_ID = "StableMaterialsFromImageResolutionV1"
DISPLAY_NAME = "Generate PBR (Image, Custom Resolution)"
CATEGORY = "StableMaterials/Resolution"

MAP_NAMES = ("basecolor", "normal", "height", "roughness", "metallic")

MIN_DIMENSION = 256
MAX_DIMENSION = 2048
DIMENSION_STEP = 8
MAX_SEED = 0xFFFFFFFFFFFFFFFF


class StableMaterialsResolutionError(RuntimeError):
    """Actionable failure raised by the custom-resolution image node."""


def validate_dimensions(width, height):
    """Return validated ``(width, height)`` integers.

    ComfyUI may hand us arbitrary Python values when a workflow is loaded or
    edited, so the execution path re-checks type, bounds and model-friendly
    divisibility instead of trusting the widget hints.
    """

    values = {}
    for name, value in (("width", width), ("height", height)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise StableMaterialsResolutionError(
                f"{name} must be an integer, got {type(value).__name__}."
            )
        if value < MIN_DIMENSION or value > MAX_DIMENSION:
            raise StableMaterialsResolutionError(
                f"{name} must be between {MIN_DIMENSION} and {MAX_DIMENSION}, "
                f"got {value}."
            )
        if value % DIMENSION_STEP != 0:
            raise StableMaterialsResolutionError(
                f"{name} must be a multiple of {DIMENSION_STEP} for the "
                f"StableMaterials model, got {value}."
            )
        values[name] = value
    return values["width"], values["height"]


def validate_generation_controls(seed, steps, guidance_scale, tileable):
    """Validate the scalar controls before touching the pipeline."""

    if isinstance(seed, bool) or not isinstance(seed, int):
        raise StableMaterialsResolutionError(
            f"seed must be an integer, got {type(seed).__name__}."
        )
    if seed < 0 or seed > MAX_SEED:
        raise StableMaterialsResolutionError(
            f"seed must be between 0 and {MAX_SEED}, got {seed}."
        )

    if isinstance(steps, bool) or not isinstance(steps, int):
        raise StableMaterialsResolutionError(
            f"steps must be an integer, got {type(steps).__name__}."
        )
    if steps < 1 or steps > 50:
        raise StableMaterialsResolutionError(
            f"steps must be between 1 and 50, got {steps}."
        )

    if isinstance(guidance_scale, bool) or not isinstance(
        guidance_scale, (int, float)
    ):
        raise StableMaterialsResolutionError(
            f"guidance_scale must be numeric, got {type(guidance_scale).__name__}."
        )
    if not np.isfinite(guidance_scale):
        raise StableMaterialsResolutionError(
            "guidance_scale must be finite."
        )

    if not isinstance(tileable, bool):
        raise StableMaterialsResolutionError(
            f"tileable must be a boolean, got {type(tileable).__name__}."
        )

    return seed, steps, float(guidance_scale), tileable


def _keyword_parameter(parameters, name):
    """Return an explicit keyword-passable parameter, or ``None``.

    ``**kwargs`` deliberately does not count: accepting arbitrary keywords is
    not evidence that a pipeline implements an ``image`` or a ``width``
    parameter.
    """

    parameter = parameters.get(name)
    if parameter is None:
        return None
    if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
        return None
    return parameter


def inspect_pipeline_signature(pipeline):
    """Return the callable signature, or raise an actionable error."""

    call = getattr(pipeline, "__call__", None)
    if call is None or not callable(call):
        raise StableMaterialsResolutionError(
            "pipeline does not expose a callable __call__. Connect the "
            "SM_PIPELINE output from LoadStableMaterials."
        )
    try:
        return inspect.signature(call)
    except (TypeError, ValueError) as exc:
        raise StableMaterialsResolutionError(
            "Unable to inspect the StableMaterials pipeline __call__ "
            "signature, so the conditioning mode cannot be chosen safely."
        ) from exc


def choose_conditioning_route(signature):
    """Choose ``"image"`` or ``"prompt"`` from explicit parameters only.

    An explicit ``image`` parameter is used as ``image=<PIL>``. Otherwise an
    explicit ``prompt`` parameter receives the PIL image, which is how the
    published ``gvecchio/StableMaterials`` pipeline accepts image input.
    """

    parameters = signature.parameters
    image_parameter = _keyword_parameter(parameters, "image")
    prompt_parameter = _keyword_parameter(parameters, "prompt")

    if image_parameter is not None:
        return "image"
    if prompt_parameter is not None:
        return "prompt"

    has_var_keyword = any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
    extra = (
        " The signature only has **kwargs, which is not treated as image "
        "support."
        if has_var_keyword
        else ""
    )
    raise StableMaterialsResolutionError(
        "The pipeline __call__ must explicitly declare either an 'image' "
        "parameter or a 'prompt' parameter so the input image can be "
        "conditioned safely." + extra
    )


def build_pipeline_call_kwargs(
    pipeline,
    conditioning_image,
    width,
    height,
    steps,
    guidance_scale,
    tileable,
    generator,
):
    """Build pipeline kwargs after validating the supported signature.

    Width and height must be explicit parameters (not merely accepted through
    ``**kwargs``); otherwise the pipeline could silently fall back to its own
    1024px default and return maps of the wrong size.
    """

    signature = inspect_pipeline_signature(pipeline)
    parameters = signature.parameters

    for name in ("width", "height"):
        if _keyword_parameter(parameters, name) is None:
            raise StableMaterialsResolutionError(
                f"The pipeline __call__ does not explicitly expose '{name}'. "
                "Refusing to pass it through **kwargs because the pipeline "
                "may silently use its default resolution instead."
            )

    route = choose_conditioning_route(signature)

    kwargs = {
        "num_inference_steps": steps,
        "guidance_scale": guidance_scale,
        "tileable": tileable,
        "width": width,
        "height": height,
        "generator": generator,
    }

    if route == "image":
        kwargs["image"] = conditioning_image
        if _keyword_parameter(parameters, "prompt") is not None:
            kwargs["prompt"] = None
    else:
        kwargs["prompt"] = conditioning_image

    return kwargs, route


def tensor_to_pil(image):
    """Convert a ComfyUI IMAGE batch to a single RGB PIL conditioning image.

    Exactly one image is accepted. RGBA input is converted to RGB and the
    alpha channel is discarded explicitly. The input resolution is retained;
    this function never resizes the conditioning image.
    """

    shape = getattr(image, "shape", None)
    if shape is None or len(shape) != 4:
        raise StableMaterialsResolutionError(
            "image must be a ComfyUI IMAGE tensor with shape [B, H, W, C]."
        )

    batch, height, width, channels = (int(value) for value in shape)
    if batch != 1:
        raise StableMaterialsResolutionError(
            f"image batch size must be exactly 1 for this node, got {batch}. "
            "Split or select a single image before generating a material."
        )
    if height < 1 or width < 1:
        raise StableMaterialsResolutionError(
            "image height and width must both be positive."
        )
    if channels not in (3, 4):
        raise StableMaterialsResolutionError(
            f"image must have 3 (RGB) or 4 (RGBA) channels, got {channels}."
        )

    array = image[0].cpu().numpy()
    if not np.isfinite(array).all():
        raise StableMaterialsResolutionError(
            "image contains non-finite values (NaN or infinity)."
        )

    array = np.clip(array, 0.0, 1.0)
    array = np.rint(array * 255.0).astype(np.uint8)

    pil_image = Image.fromarray(array)
    if pil_image.mode != "RGB":
        # RGBA (and any other mode) is explicitly converted to RGB.
        pil_image = pil_image.convert("RGB")
    return pil_image


def pil_to_tensor(pil_image):
    """Convert one material map to a ComfyUI IMAGE tensor [1, H, W, 3]."""

    array = np.asarray(pil_image)
    if array.ndim == 2:
        array = np.stack([array, array, array], axis=-1)
    if array.ndim != 3 or array.shape[2] != 3:
        raise StableMaterialsResolutionError(
            "A generated material map must be grayscale or RGB so it can be "
            "expanded to a 3-channel ComfyUI IMAGE tensor."
        )

    array = array.astype(np.float32) / 255.0
    if not np.isfinite(array).all():
        raise StableMaterialsResolutionError(
            "A generated material map contains non-finite values."
        )

    return torch.from_numpy(np.ascontiguousarray(array)).unsqueeze(0)


def extract_material(result, width, height):
    """Validate the result and return its single material object.

    Map sizes are checked before any tensor conversion. A mismatch is an
    error, never an implicit resize; resizing normal maps would corrupt their
    encoded vectors.
    """

    images = getattr(result, "images", None)
    if images is None:
        raise StableMaterialsResolutionError(
            "The pipeline result does not expose an 'images' collection."
        )
    try:
        count = len(images)
    except TypeError as exc:
        raise StableMaterialsResolutionError(
            "The pipeline result 'images' value is not a sized collection."
        ) from exc

    if count != 1:
        raise StableMaterialsResolutionError(
            "Expected exactly 1 generated material for a batch size of 1, "
            f"got {count}. This node does not silently pick one result."
        )

    material = images[0]
    missing = [
        name for name in MAP_NAMES if getattr(material, name, None) is None
    ]
    if missing:
        raise StableMaterialsResolutionError(
            "The generated material is missing required map(s): "
            + ", ".join(missing)
            + "."
        )

    expected = (width, height)
    for name in MAP_NAMES:
        map_image = getattr(material, name)
        size = getattr(map_image, "size", None)
        if size is None:
            raise StableMaterialsResolutionError(
                f"The generated {name} map does not expose a PIL size."
            )
        actual = tuple(size)
        if actual != expected:
            raise StableMaterialsResolutionError(
                f"The generated {name} map is {actual} but the requested "
                f"resolution is {expected}. Refusing to resize material maps, "
                "especially normal maps."
            )

    return material


class StableMaterialsFromImageResolutionV1:
    """Generate five PBR maps from one image at an explicit resolution."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pipeline": ("SM_PIPELINE",),
                "image": ("IMAGE",),
                "seed": (
                    "INT",
                    {"default": 0, "min": 0, "max": MAX_SEED},
                ),
                "steps": ("INT", {"default": 4, "min": 1, "max": 50}),
                "guidance_scale": (
                    "FLOAT",
                    {"default": 7.5, "min": 1.0, "max": 20.0, "step": 0.5},
                ),
                "tileable": ("BOOLEAN", {"default": True}),
                "width": (
                    "INT",
                    {
                        "default": 1024,
                        "min": MIN_DIMENSION,
                        "max": MAX_DIMENSION,
                        "step": DIMENSION_STEP,
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 1024,
                        "min": MIN_DIMENSION,
                        "max": MAX_DIMENSION,
                        "step": DIMENSION_STEP,
                    },
                ),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = MAP_NAMES
    FUNCTION = "generate"
    CATEGORY = CATEGORY

    def generate(
        self,
        pipeline,
        image,
        seed,
        steps,
        guidance_scale,
        tileable,
        width,
        height,
    ):
        width, height = validate_dimensions(width, height)
        seed, steps, guidance_scale, tileable = validate_generation_controls(
            seed, steps, guidance_scale, tileable
        )

        conditioning_image = tensor_to_pil(image)

        device = mm.get_torch_device()
        generator = torch.Generator(device=device).manual_seed(seed)

        call_kwargs, _route = build_pipeline_call_kwargs(
            pipeline=pipeline,
            conditioning_image=conditioning_image,
            width=width,
            height=height,
            steps=steps,
            guidance_scale=guidance_scale,
            tileable=tileable,
            generator=generator,
        )

        try:
            with torch.inference_mode():
                result = pipeline(**call_kwargs)
        except TypeError as exc:
            raise StableMaterialsResolutionError(
                "The StableMaterials pipeline rejected the node's call. This "
                "node requires an explicitly declared image or prompt "
                "parameter plus explicit width and height parameters. If the "
                "pipeline requires another parameter such as "
                "image_guidance_scale, that signature is not supported by "
                f"this node: {exc}"
            ) from exc

        material = extract_material(result, width, height)

        return tuple(
            pil_to_tensor(getattr(material, name)) for name in MAP_NAMES
        )


NODE_CLASS_MAPPINGS = {
    NODE_ID: StableMaterialsFromImageResolutionV1,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    NODE_ID: DISPLAY_NAME,
}
