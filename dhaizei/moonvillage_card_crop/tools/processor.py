from __future__ import annotations

import io
import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


PRESETS_PATH = Path(__file__).resolve().parent / "moonvillage_card_crop_presets.json"
MAX_FILE_BYTES = 30 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 50_000_000


def load_presets() -> dict[str, dict[str, Any]]:
    with PRESETS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _shape_mask(size: tuple[int, int], preset: dict[str, Any]) -> Image.Image:
    shape = preset.get("shape", "rounded_rectangle")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    bounds = (0, 0, size[0] - 1, size[1] - 1)
    if shape == "ellipse":
        draw.ellipse(bounds, fill=255)
    elif shape == "ellipse_flat_bottom":
        scale = 8
        large = Image.new("L", (size[0] * scale, size[1] * scale), 0)
        ImageDraw.Draw(large).ellipse(
            (0, 1.5 * scale, (size[0] - 0.5) * scale, 232.5 * scale), fill=255
        )
        mask = large.resize(size, Image.Resampling.LANCZOS)
    elif shape == "rounded_rectangle":
        radius = max(0, min(int(preset.get("radius", 0)), min(size) // 2))
        draw.rounded_rectangle(bounds, radius=radius, fill=255)
    else:
        raise ValueError(f"Unsupported card shape: {shape}")
    return mask


def _apply_shadow(image: Image.Image, mask: Image.Image, settings: dict[str, Any]) -> Image.Image:
    opacity = max(0.0, min(float(settings.get("opacity", 0)), 100.0)) / 100.0
    if opacity == 0:
        return image
    color = str(settings.get("color", "#000000")).lstrip("#")
    if len(color) != 6:
        raise ValueError(f"Invalid shadow color: {settings.get('color')}")
    rgb = tuple(int(color[index:index + 2], 16) for index in (0, 2, 4))
    angle = math.radians(float(settings.get("angle", 90)))
    distance = float(settings.get("distance", 0))
    blur_size = max(0.0, float(settings.get("size", 0)))
    offset = (round(math.cos(angle) * distance), round(math.sin(angle) * distance))
    padding = max(2, math.ceil(blur_size + abs(distance) + 2))
    padded = Image.new("L", (mask.width + padding * 2, mask.height + padding * 2), 0)
    padded.paste(mask, (padding, padding))
    alpha = ImageChops.invert(padded).transform(padded.size, Image.Transform.AFFINE, (1, 0, -offset[0], 0, 1, -offset[1]))
    if blur_size:
        alpha = alpha.filter(ImageFilter.GaussianBlur(blur_size))
    alpha = alpha.crop((padding, padding, padding + mask.width, padding + mask.height))
    alpha = ImageChops.multiply(alpha, mask).point(lambda value: round(value * opacity))
    color_layer = Image.new("RGB", image.size, rgb)
    blended = ImageChops.multiply(image.convert("RGB"), color_layer)
    result = Image.composite(blended.convert("RGBA"), image, alpha)
    result.putalpha(mask)
    return result


def process_image(blob: bytes, preset_name: str) -> tuple[bytes, str]:
    presets = load_presets()
    if preset_name not in presets:
        raise ValueError(f"Unknown card preset: {preset_name}")
    preset = deepcopy(presets[preset_name])
    size = (int(preset["width"]), int(preset["height"]))
    with Image.open(io.BytesIO(blob)) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGBA")
        image = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    mask = _shape_mask(size, preset)
    image.putalpha(ImageChops.multiply(image.getchannel("A"), mask))
    shadows = list(preset.get("inner_shadows", []))
    if preset.get("inner_shadow"):
        shadows.insert(0, preset["inner_shadow"])
    for shadow in shadows:
        image = _apply_shadow(image, mask, shadow)
    output = io.BytesIO()
    output_format = str(preset.get("format", "png")).lower()
    if output_format == "jpg":
        background = Image.new("RGB", size, "#FFFFFF")
        background.paste(image, mask=image.getchannel("A"))
        background.save(output, "JPEG", quality=95, optimize=True)
        return output.getvalue(), ".jpg"
    if output_format not in {"png", "webp"}:
        raise ValueError(f"Unsupported output format: {output_format}")
    image.save(output, output_format.upper(), optimize=True)
    return output.getvalue(), f".{output_format}"

