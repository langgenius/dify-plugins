"""Shared input validation logic for PixSEO clients.

This module is the single source of truth for:
- Maximum image size
- Allowed image formats (magic bytes)
- Base64 image decoding and validation
- URL format validation

Both the Dify plugin and Coze skill should align with this file.
"""

from __future__ import annotations

import base64
import binascii
import re
from typing import Optional

MAX_IMAGE_SIZE_MB = 10


def check_image_magic(data: bytes) -> bool:
    """Check whether image magic bytes are in the allowed whitelist."""
    if len(data) < 12:
        return False
    # JPEG
    if data[:3] == b"\xff\xd8\xff":
        return True
    # PNG
    if data[:4] == b"\x89PNG":
        return True
    # WebP: RIFF....WEBP
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    # AVIF: ....ftypavif / ftypavis
    if data[4:8] == b"ftyp" and data[8:12] in (b"avif", b"avis"):
        return True
    # TIFF
    if data[:4] in (b"II*\x00", b"MM\x00*"):
        return True
    return False


def validate_image_base64(image_base64: str) -> Optional[str]:
    """Validate a base64-encoded image: size and format."""
    if not image_base64:
        return None
    try:
        data = base64.b64decode(image_base64, validate=True)
    except binascii.Error:
        return "Invalid base64 image data."
    except Exception:
        return "Unable to decode image data."

    size_mb = len(data) / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        return (
            f"Image too large ({size_mb:.1f} MB). "
            f"Maximum allowed size is {MAX_IMAGE_SIZE_MB} MB."
        )

    if not check_image_magic(data):
        return "Unsupported image format. Only JPEG, PNG, WebP, AVIF, TIFF are allowed."
    return None


def validate_image_url(url: str) -> Optional[str]:
    """Validate an image URL format."""
    if not url:
        return None
    if not re.match(r"^https?://", url, re.IGNORECASE):
        return "Image URL must start with http:// or https://."
    return None
