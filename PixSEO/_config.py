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

API_BASE = os.environ.get("PIXSEO_API_BASE", "https://api.pixseo.cc")
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
            "请求 PixSEO API 超时，请稍后重试。"
        )
    except requests.exceptions.ConnectionError:
        raise ValueError(
            "无法连接到 PixSEO API，请检查网络。"
        )
    except requests.exceptions.HTTPError as e:
        detail = str(e)
        user_tip = None
        try:
            body = e.response.json()
            # 后端统一错误格式: {"error": {"code": ..., "message": ..., "user_tip": ...}}
            err = body.get("error") if isinstance(body, dict) else None
            if isinstance(err, dict):
                user_tip = err.get("user_tip")
        except Exception:
            pass
        raise ValueError(user_tip or "请求处理失败，请稍后重试")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"请求失败: {e}")


def yield_error(tool: "Tool", message: str) -> Generator["ToolInvokeMessage"]:
    """Yield a consistent error message."""
    yield tool.create_text_message(f"错误：{message}")
