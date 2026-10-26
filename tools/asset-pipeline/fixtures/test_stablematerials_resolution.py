"""Offline contract tests for the StableMaterials custom-resolution node.

These tests do NOT run ComfyUI or StableMaterials. They install small
in-memory stubs for torch, numpy, PIL and comfy.model_management, then load
the extension module directly. Run with:

    python3 -m unittest discover -s tools/asset-pipeline/fixtures \
        -p 'test_stablematerials_resolution.py'
"""

import contextlib
import importlib.util
import math
import sys
import types
import unittest
from pathlib import Path


NODE_PATH = (
    Path(__file__).resolve().parents[1]
    / "comfyui"
    / "stablematerials_resolution"
    / "__init__.py"
)

NODE = None
_SAVED_MODULES = {}


# ---------------------------------------------------------------------------
# Minimal dependency stubs
# ---------------------------------------------------------------------------


class FakeArray:
    def __init__(self, flat, shape):
        self._flat = list(flat)
        self._shape = tuple(shape)

    @property
    def ndim(self):
        return len(self._shape)

    @property
    def shape(self):
        return self._shape

    def __truediv__(self, value):
        return FakeArray([item / value for item in self._flat], self._shape)

    def __mul__(self, value):
        return FakeArray([item * value for item in self._flat], self._shape)

    def __rmul__(self, value):
        return self.__mul__(value)

    def astype(self, dtype):
        if dtype == "uint8":
            return FakeArray([int(item) for item in self._flat], self._shape)
        if dtype == "float32":
            return FakeArray([float(item) for item in self._flat], self._shape)
        return FakeArray(self._flat, self._shape)


class FakeMask:
    def __init__(self, values):
        self._values = list(values)

    def all(self):
        return all(self._values)

    def __bool__(self):
        return self.all()


class FakeImage:
    def __init__(self, size, mode="RGB", value=128, pixels=None):
        self.size = tuple(size)
        self.mode = mode
        channels = {"L": 1, "RGB": 3, "RGBA": 4}[mode]
        count = self.size[0] * self.size[1] * channels
        self._pixels = (
            [value] * count if pixels is None else [pixels] * count
            if not isinstance(pixels, list)
            else list(pixels)
        )

    def _as_array(self):
        width, height = self.size
        if self.mode == "L":
            return FakeArray(self._pixels, (height, width))
        channels = 3 if self.mode == "RGB" else 4
        return FakeArray(self._pixels, (height, width, channels))

    def convert(self, mode):
        if mode == self.mode:
            return self
        if self.mode == "L" and mode == "RGB":
            expanded = []
            for value in self._pixels:
                expanded.extend([value, value, value])
            return FakeImage(self.size, "RGB", pixels=expanded)
        if self.mode == "RGBA" and mode == "RGB":
            dropped = []
            for index in range(0, len(self._pixels), 4):
                dropped.extend(self._pixels[index : index + 3])
            return FakeImage(self.size, "RGB", pixels=dropped)
        if self.mode == "RGB" and mode == "L":
            pixels = self._pixels[::3]
            return FakeImage(self.size, "L", pixels=pixels)
        raise AssertionError(f"Unsupported stub conversion {self.mode}->{mode}")

    @classmethod
    def fromarray(cls, array):
        shape = array.shape
        if len(shape) == 2:
            height, width = shape
            return cls((width, height), "L", pixels=list(array._flat))
        height, width, channels = shape
        mode = {3: "RGB", 4: "RGBA"}[channels]
        return cls((width, height), mode, pixels=list(array._flat))


class FakeTensor:
    def __init__(self, flat, shape):
        self._flat = list(flat)
        self._shape = tuple(shape)

    @property
    def shape(self):
        return self._shape

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise AssertionError("FakeTensor only supports integer indexing")
        if not self._shape:
            raise IndexError(index)
        stride = 1
        for dimension in self._shape[1:]:
            stride *= dimension
        start = index * stride
        return FakeTensor(self._flat[start : start + stride], self._shape[1:])

    def cpu(self):
        return self

    def numpy(self):
        return FakeArray(self._flat, self._shape)

    def unsqueeze(self, dimension):
        if dimension != 0:
            raise AssertionError("FakeTensor only supports unsqueeze(0)")
        return FakeTensor(self._flat, (1,) + self._shape)


class FakeGenerator:
    def __init__(self, device=None):
        self.device = device
        self.seed = None

    def manual_seed(self, seed):
        self.seed = seed
        return self


class FakeResult:
    def __init__(self, images):
        self.images = images


class FakeMaterial:
    def __init__(self, **maps):
        for name, image in maps.items():
            setattr(self, name, image)


_MAP_VALUES = {
    "basecolor": 10,
    "normal": 20,
    "height": 30,
    "roughness": 40,
    "metallic": 50,
}


def make_material(width, height, mode="RGB"):
    maps = {}
    for name, value in _MAP_VALUES.items():
        map_mode = "L" if name == "height" else mode
        maps[name] = FakeImage((width, height), map_mode, value=value)
    return FakeMaterial(**maps)


def make_image_tensor(batch=1, height=48, width=64, channels=3, value=0.5):
    count = batch * height * width * channels
    return FakeTensor([value] * count, (batch, height, width, channels))


def _np_asarray(data, dtype=None):
    if isinstance(data, FakeImage):
        array = data._as_array()
    elif isinstance(data, FakeArray):
        array = data
    else:
        raise AssertionError("FakeNumpy.asarray only supports FakeImage/FakeArray")
    if dtype is not None:
        array = array.astype(dtype)
    return array


def _np_stack(arrays, axis=-1):
    arrays = list(arrays)
    if axis != -1 or len(arrays[0].shape) != 2:
        raise AssertionError("FakeNumpy.stack stub only supports 2D axis=-1")
    height, width = arrays[0].shape
    flat = []
    for index in range(height * width):
        for array in arrays:
            flat.append(array._flat[index])
    return FakeArray(flat, (height, width, len(arrays)))


def _np_isfinite(value):
    if isinstance(value, FakeArray):
        return FakeMask([math.isfinite(item) for item in value._flat])
    return FakeMask([math.isfinite(float(value))])


def _np_clip(array, low, high):
    return FakeArray(
        [min(max(item, low), high) for item in array._flat], array.shape
    )


def _np_rint(array):
    return FakeArray([float(round(item)) for item in array._flat], array.shape)


def _np_ascontiguousarray(array):
    return array


def _install_stubs():
    for name in (
        "torch",
        "numpy",
        "PIL",
        "PIL.Image",
        "comfy",
        "comfy.model_management",
    ):
        _SAVED_MODULES[name] = sys.modules.get(name)

    numpy_module = types.ModuleType("numpy")
    numpy_module.float32 = "float32"
    numpy_module.uint8 = "uint8"
    numpy_module.asarray = _np_asarray
    numpy_module.stack = _np_stack
    numpy_module.isfinite = _np_isfinite
    numpy_module.clip = _np_clip
    numpy_module.rint = _np_rint
    numpy_module.ascontiguousarray = _np_ascontiguousarray

    torch_module = types.ModuleType("torch")
    torch_module.Tensor = FakeTensor
    torch_module.Generator = FakeGenerator
    torch_module.from_numpy = lambda array: FakeTensor(
        array._flat, array.shape
    )
    torch_module.inference_mode = lambda: contextlib.nullcontext()

    image_module = types.ModuleType("PIL.Image")
    image_module.Image = FakeImage
    image_module.fromarray = FakeImage.fromarray
    pil_module = types.ModuleType("PIL")
    pil_module.Image = image_module

    comfy_module = types.ModuleType("comfy")
    model_management = types.ModuleType("comfy.model_management")
    model_management.get_torch_device = lambda: "cpu"
    comfy_module.model_management = model_management

    sys.modules["numpy"] = numpy_module
    sys.modules["torch"] = torch_module
    sys.modules["PIL"] = pil_module
    sys.modules["PIL.Image"] = image_module
    sys.modules["comfy"] = comfy_module
    sys.modules["comfy.model_management"] = model_management


def _restore_stubs():
    for name, module in _SAVED_MODULES.items():
        if module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = module


def setUpModule():
    global NODE
    _install_stubs()
    spec = importlib.util.spec_from_file_location(
        "stablematerials_resolution_under_test", NODE_PATH
    )
    NODE = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(NODE)


def tearDownModule():
    _restore_stubs()


# ---------------------------------------------------------------------------
# Fake pipelines with deliberate signatures
# ---------------------------------------------------------------------------


class RecordingPipeline:
    def __init__(self, material_factory=make_material):
        self.calls = []
        self.material_factory = material_factory

    def _result(self, width, height):
        return FakeResult([self.material_factory(width, height)])


class StandardPromptPipeline(RecordingPipeline):
    """Mirrors the published upstream signature: prompt, no explicit image."""

    def __call__(
        self,
        prompt,
        height,
        width,
        num_inference_steps=4,
        guidance_scale=7.5,
        tileable=True,
        generator=None,
        **kwargs,
    ):
        self.calls.append(
            {
                "prompt": prompt,
                "height": height,
                "width": width,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "tileable": tileable,
                "generator": generator,
                "extra": kwargs,
            }
        )
        return self._result(width, height)


class ExplicitImagePipeline(RecordingPipeline):
    def __call__(
        self,
        image,
        prompt=None,
        height=1024,
        width=1024,
        num_inference_steps=4,
        guidance_scale=7.5,
        tileable=True,
        generator=None,
        **kwargs,
    ):
        self.calls.append(
            {
                "image": image,
                "prompt": prompt,
                "height": height,
                "width": width,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "tileable": tileable,
                "generator": generator,
                "extra": kwargs,
            }
        )
        return self._result(width, height)


class ExplicitImageNoPromptPipeline(RecordingPipeline):
    def __call__(
        self,
        image,
        height=1024,
        width=1024,
        num_inference_steps=4,
        guidance_scale=7.5,
        tileable=True,
        generator=None,
        **kwargs,
    ):
        self.calls.append({"image": image, "width": width, "height": height})
        return self._result(width, height)


class KwargsOnlyPipeline(RecordingPipeline):
    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self._result(kwargs.get("width", 1024), kwargs.get("height", 1024))


class NoDimensionPipeline(RecordingPipeline):
    def __call__(
        self,
        prompt,
        num_inference_steps=4,
        guidance_scale=7.5,
        tileable=True,
        generator=None,
        **kwargs,
    ):
        self.calls.append({"prompt": prompt})
        return self._result(1024, 1024)


class RequiredGuidancePipeline(RecordingPipeline):
    def __call__(
        self,
        image,
        image_guidance_scale,
        prompt=None,
        height=1024,
        width=1024,
        num_inference_steps=4,
        guidance_scale=7.5,
        tileable=True,
        generator=None,
        **kwargs,
    ):
        self.calls.append({"image": image})
        return self._result(width, height)


class MultiMaterialPipeline(RecordingPipeline):
    def __call__(self, prompt, height, width, **kwargs):
        self.calls.append({"prompt": prompt})
        return FakeResult([make_material(width, height), make_material(width, height)])


class EmptyMaterialPipeline(RecordingPipeline):
    def __call__(self, prompt, height, width, **kwargs):
        self.calls.append({"prompt": prompt})
        return FakeResult([])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class RegistrationTests(unittest.TestCase):
    def test_unique_registration_and_display_mapping(self):
        self.assertEqual(
            list(NODE.NODE_CLASS_MAPPINGS),
            ["StableMaterialsFromImageResolutionV1"],
        )
        self.assertEqual(
            NODE.NODE_DISPLAY_NAME_MAPPINGS,
            {
                "StableMaterialsFromImageResolutionV1": (
                    "Generate PBR (Image, Custom Resolution)"
                )
            },
        )
        cls = NODE.NODE_CLASS_MAPPINGS["StableMaterialsFromImageResolutionV1"]
        self.assertEqual(cls.CATEGORY, "StableMaterials/Resolution")
        self.assertEqual(
            cls.RETURN_NAMES,
            ("basecolor", "normal", "height", "roughness", "metallic"),
        )

    def test_no_legacy_ids_cache_or_loader(self):
        for legacy in (
            "LoadStableMaterials",
            "StableMaterialsGenerate",
            "StableMaterialsFromImage",
            "CombinePBRPreview",
            "SplitPBRMaps",
        ):
            self.assertNotIn(legacy, NODE.NODE_CLASS_MAPPINGS)
        self.assertFalse(hasattr(NODE, "get_pipeline"))
        self.assertNotIn("_pipeline", vars(NODE))

        source = NODE_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "folder_paths",
            "from_pretrained",
            "empty_cache",
            "trust_remote_code",
            "cuda",
        ):
            self.assertNotIn(forbidden, source)

    def test_input_contract(self):
        required = NODE.StableMaterialsFromImageResolutionV1.INPUT_TYPES()[
            "required"
        ]
        self.assertEqual(required["pipeline"][0], "SM_PIPELINE")
        self.assertEqual(required["image"][0], "IMAGE")
        for name in ("width", "height"):
            spec = required[name][1]
            self.assertEqual(required[name][0], "INT")
            self.assertEqual(spec["default"], 1024)
            self.assertEqual(spec["min"], 256)
            self.assertEqual(spec["max"], 2048)
            self.assertEqual(spec["step"], 8)
        self.assertNotIn("prompt", required)
        self.assertNotIn("image_guidance_scale", required)


class DimensionAndControlTests(unittest.TestCase):
    def test_valid_square_and_non_square_dimensions(self):
        self.assertEqual(NODE.validate_dimensions(1024, 1024), (1024, 1024))
        self.assertEqual(NODE.validate_dimensions(1536, 768), (1536, 768))
        self.assertEqual(NODE.validate_dimensions(256, 2048), (256, 2048))

    def test_invalid_dimension_types_bounds_and_divisibility(self):
        bad = [
            (True, 1024),
            (1024, False),
            (1024.0, 1024),
            ("1024", 1024),
            (255, 1024),
            (2048 + 8, 1024),
            (1020, 1024),
        ]
        for width, height in bad:
            with self.subTest(width=width, height=height):
                with self.assertRaises(NODE.StableMaterialsResolutionError):
                    NODE.validate_dimensions(width, height)

    def test_generation_controls_reject_bools_and_nan(self):
        self.assertEqual(
            NODE.validate_generation_controls(0, 4, 7.5, True),
            (0, 4, 7.5, True),
        )
        with self.assertRaises(NODE.StableMaterialsResolutionError):
            NODE.validate_generation_controls(True, 4, 7.5, True)
        with self.assertRaises(NODE.StableMaterialsResolutionError):
            NODE.validate_generation_controls(0, True, 7.5, True)
        with self.assertRaises(NODE.StableMaterialsResolutionError):
            NODE.validate_generation_controls(0, 4, float("nan"), True)


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.image = FakeImage((32, 48), "RGB", value=100)

    def _build(self, pipeline):
        return NODE.build_pipeline_call_kwargs(
            pipeline=pipeline,
            conditioning_image=self.image,
            width=512,
            height=256,
            steps=4,
            guidance_scale=7.5,
            tileable=True,
            generator=FakeGenerator(),
        )

    def test_published_prompt_signature_routes_image_via_prompt(self):
        kwargs, route = self._build(StandardPromptPipeline())
        self.assertEqual(route, "prompt")
        self.assertIs(kwargs["prompt"], self.image)
        self.assertNotIn("image", kwargs)
        self.assertEqual(kwargs["width"], 512)
        self.assertEqual(kwargs["height"], 256)

    def test_explicit_image_signature_uses_image_and_prompt_none(self):
        kwargs, route = self._build(ExplicitImagePipeline())
        self.assertEqual(route, "image")
        self.assertIs(kwargs["image"], self.image)
        self.assertIsNone(kwargs["prompt"])
        self.assertNotIn("image_guidance_scale", kwargs)

    def test_explicit_image_without_prompt_does_not_invent_prompt(self):
        kwargs, route = self._build(ExplicitImageNoPromptPipeline())
        self.assertEqual(route, "image")
        self.assertIn("image", kwargs)
        self.assertNotIn("prompt", kwargs)

    def test_kwargs_alone_is_not_image_capability(self):
        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError, r"\*\*kwargs"
        ):
            self._build(KwargsOnlyPipeline())

    def test_width_height_are_not_passed_through_kwargs(self):
        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError,
            "does not explicitly expose 'width'",
        ):
            self._build(NoDimensionPipeline())


class GenerateTests(unittest.TestCase):
    def setUp(self):
        self.node = NODE.StableMaterialsFromImageResolutionV1()

    def test_non_square_resolution_forwarded_and_input_not_resized(self):
        pipeline = StandardPromptPipeline()
        image = make_image_tensor(height=48, width=64, value=0.5)

        outputs = self.node.generate(
            pipeline,
            image,
            seed=7,
            steps=4,
            guidance_scale=7.5,
            tileable=True,
            width=512,
            height=256,
        )

        call = pipeline.calls[0]
        self.assertEqual(call["width"], 512)
        self.assertEqual(call["height"], 256)
        self.assertEqual(call["num_inference_steps"], 4)
        self.assertEqual(call["guidance_scale"], 7.5)
        self.assertTrue(call["tileable"])
        self.assertEqual(call["generator"].seed, 7)
        self.assertEqual(call["generator"].device, "cpu")
        # Conditioning keeps its original size; outputs are the requested size.
        self.assertEqual(call["prompt"].size, (64, 48))
        self.assertEqual(call["prompt"].mode, "RGB")

        self.assertEqual(len(outputs), 5)
        for tensor in outputs:
            self.assertEqual(tensor.shape, (1, 256, 512, 3))
            self.assertTrue(all(0.0 <= value <= 1.0 for value in tensor._flat))

        expected_first_values = [10, 20, 30, 40, 50]
        for tensor, expected in zip(outputs, expected_first_values):
            self.assertAlmostEqual(tensor._flat[0], expected / 255.0, places=6)

    def test_explicit_image_signature_is_used_at_runtime(self):
        pipeline = ExplicitImagePipeline()
        image = make_image_tensor(height=32, width=40, value=0.25)

        outputs = self.node.generate(
            pipeline,
            image,
            seed=1,
            steps=4,
            guidance_scale=7.5,
            tileable=False,
            width=320,
            height=448,
        )

        call = pipeline.calls[0]
        self.assertIsInstance(call["image"], FakeImage)
        self.assertEqual(call["image"].size, (40, 32))
        self.assertIsNone(call["prompt"])
        self.assertNotIn("image_guidance_scale", call)
        self.assertEqual(len(outputs), 5)
        for tensor in outputs:
            self.assertEqual(tensor.shape, (1, 448, 320, 3))

    def test_rgba_input_discards_alpha_explicitly(self):
        pipeline = StandardPromptPipeline()
        image = make_image_tensor(height=32, width=40, channels=4, value=0.5)

        outputs = self.node.generate(
            pipeline,
            image,
            seed=0,
            steps=4,
            guidance_scale=7.5,
            tileable=True,
            width=256,
            height=256,
        )

        conditioning = pipeline.calls[0]["prompt"]
        self.assertEqual(conditioning.size, (40, 32))
        self.assertEqual(conditioning.mode, "RGB")
        self.assertEqual(len(outputs), 5)

    def test_batch_larger_than_one_is_rejected_before_pipeline(self):
        pipeline = StandardPromptPipeline()
        image = make_image_tensor(batch=2, height=32, width=40)

        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError,
            "batch size must be exactly 1",
        ):
            self.node.generate(
                pipeline,
                image,
                seed=0,
                steps=4,
                guidance_scale=7.5,
                tileable=True,
                width=256,
                height=256,
            )
        self.assertEqual(pipeline.calls, [])

    def test_nonfinite_input_is_rejected_before_pipeline(self):
        pipeline = StandardPromptPipeline()
        image = make_image_tensor(height=32, width=40)
        image._flat[5] = float("nan")

        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError, "non-finite"
        ):
            self.node.generate(
                pipeline,
                image,
                seed=0,
                steps=4,
                guidance_scale=7.5,
                tileable=True,
                width=256,
                height=256,
            )
        self.assertEqual(pipeline.calls, [])

    def test_wrong_map_dimensions_fail_without_resizing(self):
        def factory(width, height):
            material = make_material(width, height)
            material.normal = FakeImage((width // 2, height), "RGB", value=20)
            return material

        pipeline = StandardPromptPipeline(material_factory=factory)
        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError,
            "Refusing to resize",
        ):
            self.node.generate(
                pipeline,
                make_image_tensor(height=32, width=40),
                seed=0,
                steps=4,
                guidance_scale=7.5,
                tileable=True,
                width=512,
                height=256,
            )

    def test_result_requires_exactly_one_material(self):
        pipeline = MultiMaterialPipeline()
        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError,
            "Expected exactly 1 generated material",
        ):
            self.node.generate(
                pipeline,
                make_image_tensor(height=32, width=40),
                seed=0,
                steps=4,
                guidance_scale=7.5,
                tileable=True,
                width=256,
                height=256,
            )

    def test_empty_result_is_rejected(self):
        pipeline = EmptyMaterialPipeline()
        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError,
            "Expected exactly 1 generated material",
        ):
            self.node.generate(
                pipeline,
                make_image_tensor(height=32, width=40),
                seed=0,
                steps=4,
                guidance_scale=7.5,
                tileable=True,
                width=256,
                height=256,
            )

    def test_missing_material_attribute_fails(self):
        def factory(width, height):
            material = make_material(width, height)
            del material.metallic
            return material

        pipeline = StandardPromptPipeline(material_factory=factory)
        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError, "metallic"
        ):
            self.node.generate(
                pipeline,
                make_image_tensor(height=32, width=40),
                seed=0,
                steps=4,
                guidance_scale=7.5,
                tileable=True,
                width=256,
                height=256,
            )

    def test_unsupported_required_parameter_reports_actionable_error(self):
        pipeline = RequiredGuidancePipeline()
        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError, "image_guidance_scale"
        ):
            self.node.generate(
                pipeline,
                make_image_tensor(height=32, width=40),
                seed=0,
                steps=4,
                guidance_scale=7.5,
                tileable=True,
                width=256,
                height=256,
            )


class ConversionTests(unittest.TestCase):
    def test_grayscale_map_expands_to_rgb(self):
        tensor = NODE.pil_to_tensor(FakeImage((4, 3), "L", value=128))
        self.assertEqual(tensor.shape, (1, 3, 4, 3))
        self.assertEqual(len(tensor._flat), 3 * 4 * 3)
        self.assertAlmostEqual(tensor._flat[0], 128 / 255.0, places=6)
        self.assertAlmostEqual(tensor._flat[1], 128 / 255.0, places=6)

    def test_rgb_map_keeps_channels_and_normalizes(self):
        tensor = NODE.pil_to_tensor(FakeImage((4, 3), "RGB", value=64))
        self.assertEqual(tensor.shape, (1, 3, 4, 3))
        self.assertAlmostEqual(tensor._flat[0], 64 / 255.0, places=6)

    def test_nonfinite_material_map_is_rejected(self):
        image = FakeImage((2, 2), "RGB", pixels=[float("nan")] * 12)
        with self.assertRaisesRegex(
            NODE.StableMaterialsResolutionError, "non-finite"
        ):
            NODE.pil_to_tensor(image)


if __name__ == "__main__":
    unittest.main()
