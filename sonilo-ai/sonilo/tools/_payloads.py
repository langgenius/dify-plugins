"""Request/response helpers shared by the four Sonilo generation tools.

Field names and enums here follow the real backend contract (FastAPI
``Form(...)`` params), which differs from endpoint to endpoint:

- Music endpoints (``text-to-music``, ``video-to-music``) use
  ``output_format`` with values ``m4a`` (default) or ``wav``, and accept a
  ``mode`` field. This plugin always sends ``mode="async"`` (see
  ``tools/_client.py`` for why) so ``mode`` is not exposed as a
  user-facing parameter.
- SFX endpoints (``text-to-sfx``, ``video-to-sfx``) use a differently
  named field, ``audio_format``, with values ``wav``/``mp3``/``aac``/
  ``flac`` and no documented default, and accept no ``mode`` field at all
  -- they are unconditionally async.
"""

from __future__ import annotations

from typing import Any, Optional

MIME_BY_FORMAT = {
    "m4a": "audio/mp4",
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "aac": "audio/aac",
    "flac": "audio/flac",
}


def coerce_duration(value: Any, *, min_seconds: int, max_seconds: int) -> tuple[Optional[int], Optional[str]]:
    """Validate/convert a user-supplied duration before spending a billed
    call on it. Returns ``(seconds, error_message)`` -- exactly one of the
    two is set."""
    if value is None or value == "":
        return None, "duration is required."
    try:
        seconds = int(float(value))
    except (TypeError, ValueError):
        return None, f"duration must be a whole number of seconds, got {value!r}."
    if not (min_seconds <= seconds <= max_seconds):
        return None, f"duration must be between {min_seconds} and {max_seconds} seconds, got {seconds}."
    return seconds, None


def build_music_text_fields(
    *,
    prompt: str,
    duration: int,
    output_format: Optional[str],
) -> dict[str, Any]:
    """Form fields for POST /v1/text-to-music. Always async (see module docstring)."""
    fields: dict[str, Any] = {"prompt": prompt, "duration": duration, "mode": "async"}
    if output_format:
        fields["output_format"] = output_format
    return fields


def build_music_video_fields(
    *,
    video_url: str,
    prompt: Optional[str],
    output_format: Optional[str],
) -> dict[str, Any]:
    """Form fields for POST /v1/video-to-music. Always async (see module docstring)."""
    fields: dict[str, Any] = {"video_url": video_url, "mode": "async"}
    if prompt:
        fields["prompt"] = prompt
    if output_format:
        fields["output_format"] = output_format
    return fields


def build_sfx_text_fields(
    *,
    prompt: str,
    duration: int,
    audio_format: Optional[str],
) -> dict[str, Any]:
    """Form fields for POST /v1/text-to-sfx. No mode field -- this endpoint
    is unconditionally async."""
    fields: dict[str, Any] = {"prompt": prompt, "duration": duration}
    if audio_format:
        fields["audio_format"] = audio_format
    return fields


def build_sfx_video_fields(
    *,
    video_url: str,
    prompt: Optional[str],
    audio_format: Optional[str],
) -> dict[str, Any]:
    """Form fields for POST /v1/video-to-sfx. No mode field -- this endpoint
    is unconditionally async."""
    fields: dict[str, Any] = {"video_url": video_url}
    if prompt:
        fields["prompt"] = prompt
    if audio_format:
        fields["audio_format"] = audio_format
    return fields


def guess_mime_type(output_format: Optional[str], content_type: Optional[str]) -> str:
    if content_type:
        return content_type.split(";")[0].strip()
    if output_format:
        return MIME_BY_FORMAT.get(output_format.lower(), "audio/mp4")
    return "audio/mp4"


def result_summary(*, tool_label: str, audio_url: Optional[str], task_id: Optional[str], status: Optional[str]) -> str:
    if audio_url:
        return f"{tool_label} succeeded. Audio URL: {audio_url}"
    if task_id:
        return f"{tool_label}: task {task_id} finished with status '{status}', but no audio URL was found in the response."
    return f"{tool_label} returned a response with no audio URL."
