"""Shared HTTP client for all four Sonilo generation tools.

Built directly against Sonilo's backend route contract (confirmed against
the backend source and the official JS/Python SDKs), not against a
third-party SDK -- this intentionally does not import the ``sonilo`` PyPI
package. Every request carries the user's own API key as a Bearer token;
the key is never logged or included in any error message or return value.

Request encoding
-----------------
All five Sonilo POST endpoints
(``/v1/text-to-music``, ``/v1/video-to-music``, ``/v1/audio-ducking``,
``/v1/text-to-sfx``, ``/v1/video-to-sfx``) bind their fields with FastAPI
``Form(...)`` parameters, so they accept **multipart/form-data only** --
a JSON body will not bind. :func:`submit_generation` always sends
``multipart/form-data`` (via ``requests``' ``files={name: (None, value)}``
trick, which multipart-encodes plain form fields with no attached file).

Async handling
---------------
- ``/v1/text-to-sfx`` and ``/v1/video-to-sfx`` are unconditionally async:
  every call returns a 202-style ack, always exactly
  ``{"task_id": ..., "status": "processing"}``. They accept no ``mode``
  field at all.
- ``/v1/text-to-music`` and ``/v1/video-to-music`` accept ``mode`` =
  ``"stream"`` (default) or ``"async"``. The default ``"stream"`` mode
  returns an NDJSON event stream (``audio_chunk``/``title``/``complete``/
  ``error`` events) rather than a single JSON body. This plugin does not
  implement that streaming protocol; instead it always submits
  ``mode="async"`` for both music endpoints and polls the task API below,
  so every tool in this plugin follows the same submit-then-poll path.

Either way, :func:`resolve_generation` submits the request and polls
``GET /v1/tasks/{task_id}`` until the task reaches a terminal status.
Per the real backend contract, a task's ``status`` is one of
``processing | succeeded | failed`` -- ``succeeded`` is the only success
terminal state, and there is no ``canceled`` state.
"""

from __future__ import annotations

import time
from typing import Any, Optional

import requests

API_BASE_URL = "https://api.sonilo.com"
DEFAULT_REQUEST_TIMEOUT = 60.0
DEFAULT_POLL_INTERVAL = 3.0
DEFAULT_POLL_TIMEOUT = 600.0

# Per GET /v1/tasks/{task_id} on the real backend: processing | succeeded | failed.
_TERMINAL_STATUSES = {"succeeded", "failed"}

# Terminal task result media fields to look for, per endpoint family.
_MEDIA_KEYS = ("audio", "sfx", "music", "music_processed", "video")


class SoniloAPIError(Exception):
    """Raised for a non-2xx HTTP response from the Sonilo API."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class SoniloTaskError(Exception):
    """Raised when an async Sonilo task ends in ``failed``, or when polling
    gives up before a terminal status is reached."""

    def __init__(
        self,
        message: str,
        *,
        task_id: str,
        status: str,
        refunded: Optional[bool] = None,
    ):
        super().__init__(message)
        self.task_id = task_id
        self.status = status
        self.refunded = refunded


def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}


def _raise_for_status(response: requests.Response) -> None:
    if response.ok:
        return
    detail: Optional[str] = None
    try:
        body = response.json()
        if isinstance(body, dict):
            detail = body.get("detail") or body.get("error") or body.get("message")
    except ValueError:
        detail = response.text[:500] if response.text else None
    if response.status_code == 401:
        message = "Sonilo API rejected the API key (401 Unauthorized). Check the key in the plugin credentials."
    elif response.status_code == 402:
        message = "Sonilo account has insufficient credits (402 Payment Required)."
    elif response.status_code == 429:
        message = "Sonilo API rate limit exceeded (429). Retry after a short wait."
    else:
        message = f"Sonilo API request failed with HTTP {response.status_code}."
    if detail:
        message = f"{message} Detail: {detail}"
    raise SoniloAPIError(message, status_code=response.status_code)


def validate_api_key(api_key: str, *, timeout: float = 15.0) -> None:
    """Cheap, read-only credential check used by the provider.

    Hits ``GET /v1/account/usage``, which needs no request body and does not
    consume generation credits. (This is a plain GET, unrelated to the
    multipart-only POST endpoints above.)
    """
    response = requests.get(
        f"{API_BASE_URL}/v1/account/usage", headers=_headers(api_key), timeout=timeout
    )
    _raise_for_status(response)


def submit_generation(
    api_key: str,
    path: str,
    fields: dict[str, Any],
    *,
    timeout: float = DEFAULT_REQUEST_TIMEOUT,
) -> dict[str, Any]:
    """POST a generation request as ``multipart/form-data``.

    ``fields`` values of ``None`` are dropped. Every remaining value is
    stringified and sent as a plain multipart form field (no attached
    file) using the ``files={name: (None, value)}`` trick, which is the
    standard way to force ``requests`` to emit ``multipart/form-data``
    without an actual file upload -- required here because the backend
    binds these fields with FastAPI ``Form(...)``, not a JSON body.
    """
    multipart_fields = {
        key: (None, str(value)) for key, value in fields.items() if value is not None
    }
    response = requests.post(
        f"{API_BASE_URL}{path}",
        headers=_headers(api_key),
        files=multipart_fields,
        timeout=timeout,
    )
    _raise_for_status(response)
    try:
        return response.json()
    except ValueError as exc:
        raise SoniloAPIError("Sonilo API returned a non-JSON response.") from exc


def get_task(api_key: str, task_id: str, *, timeout: float = 15.0) -> dict[str, Any]:
    """GET /v1/tasks/{task_id}."""
    response = requests.get(
        f"{API_BASE_URL}/v1/tasks/{task_id}", headers=_headers(api_key), timeout=timeout
    )
    _raise_for_status(response)
    return response.json()


def wait_for_task(
    api_key: str,
    task_id: str,
    *,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    timeout: float = DEFAULT_POLL_TIMEOUT,
) -> dict[str, Any]:
    """Poll ``GET /v1/tasks/{task_id}`` until it reaches a terminal status.

    Returns the task body on ``succeeded``. Raises :class:`SoniloTaskError`
    on ``failed`` or if ``timeout`` elapses first (the task may still
    complete later server-side; the caller can resume polling with the
    same ``task_id``).
    """
    deadline = time.monotonic() + timeout
    status = "processing"
    while True:
        task = get_task(api_key, task_id, timeout=15.0)
        status = task.get("status", status)
        if status in _TERMINAL_STATUSES:
            if status != "succeeded":
                error = task.get("error")
                message = None
                if isinstance(error, dict):
                    message = error.get("message")
                message = message or f"Sonilo task {task_id} ended with status '{status}'."
                raise SoniloTaskError(
                    message, task_id=task_id, status=status, refunded=task.get("refunded")
                )
            return task
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SoniloTaskError(
                f"Timed out after {timeout:.0f}s waiting for Sonilo task {task_id} "
                f"(last status: '{status}'). It may finish later; poll "
                "GET /v1/tasks/{task_id} again with this task_id.",
                task_id=task_id,
                status=status,
            )
        time.sleep(min(poll_interval, remaining))


def resolve_generation(
    api_key: str,
    path: str,
    fields: dict[str, Any],
    *,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    poll_timeout: float = DEFAULT_POLL_TIMEOUT,
) -> dict[str, Any]:
    """Submit a generation request and return the resolved (terminal) task
    body. Every endpoint this plugin calls always acks with
    ``{"task_id": ..., "status": "processing"}`` -- the SFX endpoints are
    unconditionally async, and this plugin always passes ``mode="async"``
    for the two music endpoints -- so this always polls to a terminal
    status.
    """
    ack = submit_generation(api_key, path, fields)
    task_id = ack.get("task_id")
    if not task_id:
        raise SoniloAPIError(f"Sonilo API did not return a task_id. Response: {ack!r}")
    return wait_for_task(
        api_key, task_id, poll_interval=poll_interval, timeout=poll_timeout
    )


def _media_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect every media-object dict found under the known result keys
    (``audio``/``sfx``/``music``/``music_processed``/``video``), each of
    which may be a single object or a list of objects."""
    candidates: list[dict[str, Any]] = []
    for key in _MEDIA_KEYS:
        value = payload.get(key)
        if isinstance(value, dict):
            candidates.append(value)
        elif isinstance(value, list):
            candidates.extend(item for item in value if isinstance(item, dict))
    return candidates


def extract_audio_media(payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Return the first media object (``{url, content_type, file_size,
    stream_index}``-shaped) found in a resolved (``succeeded``) task body.

    Falls back to a shallow generic scan for any dict carrying a ``url``
    string, since the exact set of populated fields can vary by endpoint
    and this should stay resilient to fields this plugin doesn't know
    about yet.
    """
    for media in _media_candidates(payload):
        if isinstance(media.get("url"), str) and media["url"]:
            return media
    for value in payload.values():
        if isinstance(value, dict) and isinstance(value.get("url"), str) and value["url"]:
            return value
    return None


def extract_audio_url(payload: dict[str, Any]) -> Optional[str]:
    media = extract_audio_media(payload)
    return media.get("url") if media else None


def download_bytes(url: str, *, timeout: float = 120.0) -> tuple[bytes, Optional[str]]:
    """Download the generated audio file. Returns ``(content, content_type)``.

    Raises :class:`SoniloAPIError` on failure; callers should treat this as
    non-fatal (the URL/metadata is still useful even if the download fails).
    """
    response = requests.get(url, timeout=timeout)
    if not response.ok:
        raise SoniloAPIError(f"Could not download generated audio (HTTP {response.status_code}).")
    return response.content, response.headers.get("Content-Type")
