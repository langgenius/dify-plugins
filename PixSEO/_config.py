"""Shared configuration for PixSEO Dify Plugin."""

from __future__ import annotations

import json
import os
from collections.abc import Generator
from typing import TYPE_CHECKING, Any, Optional

import requests

# shared_validation.py is copied from the workspace root during packaging.
# It remains a Dify-plugin-safe module (only stdlib) and contains no dify_plugin imports.
from shared_validation import (
    MAX_IMAGE_SIZE_MB,
    validate_image_base64,
    validate_image_url,
)

if TYPE_CHECKING:
    from dify_plugin import Tool
    from dify_plugin.entities.tool import ToolInvokeMessage

API_BASE = os.environ.get("PIXSEO_API_BASE", "https://api.hzhdmn.icu")
MAX_BATCH = int(os.environ.get("PIXSEO_MAX_BATCH", "10"))
DEFAULT_TIMEOUT = int(os.environ.get("PIXSEO_TIMEOUT", "30"))
MAX_WORKERS = int(os.environ.get("PIXSEO_MAX_WORKERS", "5"))

# Re-export for backward compatibility
validate_image_input = validate_image_base64
validate_url_input = validate_image_url


def safe_api_call(
    tool: Optional["Tool"],
    method: str,
    url: str,
    **kwargs: Any,
) -> requests.Response:
    """Make a safe HTTP request and handle errors consistently.

    On error, raises ValueError with a user-friendly message.
    Callers should catch ValueError and use yield_error() to send
    the message to the Dify UI.
    """
    try:
        resp = requests.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp
    except requests.exceptions.Timeout:
        raise ValueError(
            "Request to PixSEO API timed out. Please try again later."
        )
    except requests.exceptions.ConnectionError:
        raise ValueError(
            "Unable to connect to PixSEO API. Please check your network."
        )
    except requests.exceptions.HTTPError as e:
        detail = str(e)
        user_tip = detail
        try:
            body = e.response.json()
            detail = body.get("detail", detail)
            user_tip = body.get("user_tip", detail)
        except Exception:
            pass
        raise ValueError(user_tip or detail)


def yield_error(tool: "Tool", message: str) -> Generator["ToolInvokeMessage"]:
    """Yield a consistent error message."""
    yield tool.create_text_message(f"Error: {message}")
