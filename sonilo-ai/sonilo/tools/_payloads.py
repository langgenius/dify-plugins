"""Request/response helpers shared by the four Sonilo generation tools."""

from __future__ import annotations

from typing import Any, Optional

MIME_BY_FORMAT = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "aac": "audio/aac",
    "flac": "audio/flac",
}


def build_text_payload(
    *,
    prompt: str,
    duration: Optional[float],
    mode: Optional[str],
    output_format: Optional[str],
) -> dict[str, Any]:
    """Body for POST /v1/text-to-music and POST /v1/text-to-sfx
    (``TextPromptRequest`` in the Sonilo OpenAPI spec)."""
    payload: dict[str, Any] = {"prompt": prompt}
    if duration is not None:
        payload["duration"] = duration
    if mode:
        payload["mode"] = mode
    if output_format:
        payload["output_format"] = output_format
    return payload


def build_video_url_payload(
    *,
    video_url: str,
    prompt: Optional[str],
    mode: Optional[str],
    output_format: Optional[str],
) -> dict[str, Any]:
    """Body for POST /v1/video-to-music and POST /v1/video-to-sfx
    (``VideoUrlRequest`` in the Sonilo OpenAPI spec). Only the JSON
    ``video_url`` variant is implemented; the multipart binary-upload
    variant is not exposed by this plugin (see README)."""
    payload: dict[str, Any] = {"video_url": video_url}
    if prompt:
        payload["prompt"] = prompt
    if mode:
        payload["mode"] = mode
    if output_format:
        payload["output_format"] = output_format
    return payload


def guess_mime_type(output_format: Optional[str], content_type: Optional[str]) -> str:
    if content_type:
        return content_type.split(";")[0].strip()
    if output_format:
        return MIME_BY_FORMAT.get(output_format.lower(), "audio/aac")
    return "audio/aac"


def result_summary(*, tool_label: str, audio_url: Optional[str], task_id: Optional[str], status: Optional[str]) -> str:
    if audio_url:
        return f"{tool_label} succeeded. Audio URL: {audio_url}"
    if task_id:
        return f"{tool_label}: task {task_id} finished with status '{status}', but no audio URL was found in the response."
    return f"{tool_label} returned a response with no audio URL."
