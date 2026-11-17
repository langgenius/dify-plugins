"""Shared result-emission logic for the four Sonilo tools.

Kept separate from ``_client.py`` (HTTP/task polling) and ``_payloads.py``
(request field builders) so each of the four ``tools/*.py`` files only has
to describe what's specific to it (its endpoint path, its field builder,
its label).
"""

from __future__ import annotations

from typing import Any, Generator, Optional

from dify_plugin.entities.tool import ToolInvokeMessage

from tools._client import (
    SoniloAPIError,
    SoniloTaskError,
    download_bytes,
    extract_audio_media,
)
from tools._payloads import guess_mime_type, result_summary


def emit_success(
    tool: Any,
    *,
    tool_label: str,
    result: dict[str, Any],
    output_format: Optional[str],
    filename: str,
) -> Generator[ToolInvokeMessage, None, None]:
    """Emit the standard json + text + (optional) blob messages for a
    ``succeeded`` task body."""
    media = extract_audio_media(result)
    audio_url = media.get("url") if media else None
    task_id = result.get("task_id")
    status = result.get("status")

    json_payload = {
        "success": bool(audio_url),
        "audio_url": audio_url,
        "content_type": media.get("content_type") if media else None,
        "task_id": task_id,
        "status": status,
        "duration_seconds": result.get("duration_seconds"),
        "cost": result.get("cost"),
        "raw": result,
    }
    yield tool.create_json_message(json_payload)
    yield tool.create_text_message(
        result_summary(tool_label=tool_label, audio_url=audio_url, task_id=task_id, status=status)
    )

    if not audio_url:
        return

    try:
        content, content_type = download_bytes(audio_url)
    except SoniloAPIError as exc:
        yield tool.create_text_message(
            f"Generated audio URL is ready, but downloading it failed: {exc}"
        )
        return

    mime = guess_mime_type(output_format, media.get("content_type") if media else content_type)
    yield tool.create_blob_message(blob=content, meta={"mime_type": mime, "filename": filename})


def emit_task_error(
    tool: Any, exc: SoniloTaskError
) -> Generator[ToolInvokeMessage, None, None]:
    """Emit a json + text message pair for a failed/timed-out task, so
    callers chaining this tool in a Workflow still get a structured
    result instead of only a text message."""
    yield tool.create_json_message(
        {
            "success": False,
            "audio_url": None,
            "task_id": exc.task_id,
            "status": exc.status,
            "refunded": exc.refunded,
            "error": str(exc),
        }
    )
    yield tool.create_text_message(str(exc))
