"""Shared HTTP client for all four Sonilo generation tools.

Built directly against Sonilo's published OpenAPI spec
(https://sonilo.com/openapi.json), not against a third-party SDK, so this
intentionally does not import the ``sonilo`` PyPI package. Every request
carries the user's own API key as a Bearer token; the key is never logged
or included in any error message or return value.

Async handling
---------------
``POST /v1/text-to-music``, ``/v1/video-to-music``, ``/v1/text-to-sfx``, and
``/v1/video-to-sfx`` all share one response envelope: either a resolved
``GenerationResponse`` (the job finished before the request returned) or a
``TaskCreatedResponse`` acknowledging an async job that must be polled via
``GET /v1/tasks/{task_id}``. :func:`resolve_generation` submits the request
and transparently polls when needed, so tool implementations never have to
branch on that themselves.

Per the OpenAPI spec, a task's ``status`` is one of:
``queued | running | completed | failed | canceled`` -- ``completed`` is the
only success terminal state. (Note: this differs from the status naming used
internally by some Sonilo client SDKs, which is why polling here is written
directly against the documented wire contract rather than ported from any
SDK's task-waiting code.)
"""

from __future__ import annotations

import time
from typing import Any, Optional

import requests

API_BASE_URL = "https://api.sonilo.com"
DEFAULT_REQUEST_TIMEOUT = 60.0
DEFAULT_POLL_INTERVAL = 3.0
DEFAULT_POLL_TIMEOUT = 600.0

# Per GET /v1/tasks/{task_id} in the Sonilo OpenAPI spec.
_TERMINAL_STATUSES = {"completed", "failed", "canceled"}


class SoniloAPIError(Exception):
    """Raised for a non-2xx HTTP response from the Sonilo API."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class SoniloTaskError(Exception):
    """Raised when an async Sonilo task ends in ``failed``/``canceled``, or
    when polling gives up before a terminal status is reached."""

    def __init__(self, message: str, *, task_id: str, status: str):
        super().__init__(message)
        self.task_id = task_id
        self.status = status


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
    consume generation credits.
    """
    response = requests.get(
        f"{API_BASE_URL}/v1/account/usage", headers=_headers(api_key), timeout=timeout
    )
    _raise_for_status(response)


def submit_generation(
    api_key: str,
    path: str,
    payload: dict[str, Any],
    *,
    timeout: float = DEFAULT_REQUEST_TIMEOUT,
) -> dict[str, Any]:
    """POST a generation request to one of the four Sonilo generation
    endpoints and return the raw JSON body (a ``GenerationResponse`` or a
    ``TaskCreatedResponse``)."""
    response = requests.post(
        f"{API_BASE_URL}{path}",
        headers={**_headers(api_key), "Content-Type": "application/json"},
        json=payload,
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

    Returns the task body on ``completed``. Raises :class:`SoniloTaskError`
    on ``failed``/``canceled`` or if ``timeout`` elapses first (the task may
    still complete later server-side; the caller can resume polling with the
    same ``task_id``).
    """
    deadline = time.monotonic() + timeout
    status = "unknown"
    while True:
        task = get_task(api_key, task_id, timeout=15.0)
        status = task.get("status", status)
        if status in _TERMINAL_STATUSES:
            if status != "completed":
                error = task.get("error")
                message = None
                if isinstance(error, dict):
                    message = error.get("message")
                message = message or f"Sonilo task {task_id} ended with status '{status}'."
                raise SoniloTaskError(message, task_id=task_id, status=status)
            return task
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SoniloTaskError(
                f"Timed out after {timeout:.0f}s waiting for Sonilo task {task_id} "
                f"(last status: '{status}'). It may finish later; check "
                "GET /v1/tasks/{task_id} again with this task_id.",
                task_id=task_id,
                status=status,
            )
        time.sleep(min(poll_interval, remaining))


def _has_audio_reference(body: dict[str, Any]) -> bool:
    return bool(body.get("audio_url") or body.get("download_url"))


def resolve_generation(
    api_key: str,
    path: str,
    payload: dict[str, Any],
    *,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    poll_timeout: float = DEFAULT_POLL_TIMEOUT,
) -> dict[str, Any]:
    """Submit a generation request and return the resolved result body,
    transparently polling ``GET /v1/tasks/{task_id}`` if the API answered
    with an async task instead of a finished result."""
    body = submit_generation(api_key, path, payload)
    if "task_id" in body and not _has_audio_reference(body):
        return wait_for_task(
            api_key, body["task_id"], poll_interval=poll_interval, timeout=poll_timeout
        )
    return body


def extract_audio_url(payload: dict[str, Any], *, _depth: int = 0) -> Optional[str]:
    """Best-effort extraction of a playable/downloadable audio URL.

    The OpenAPI spec leaves both ``GenerationResponse`` and (especially)
    ``Task.result`` as open objects (``additionalProperties: true``), so
    this checks the documented field names first and then falls back to a
    shallow scan for any nested ``url``-shaped field, rather than assuming
    one fixed response shape.
    """
    if _depth > 3 or not isinstance(payload, dict):
        return None
    for key in ("audio_url", "download_url", "url"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    for key in ("result", "audio", "output"):
        nested = payload.get(key)
        if isinstance(nested, dict):
            found = extract_audio_url(nested, _depth=_depth + 1)
            if found:
                return found
        elif isinstance(nested, list):
            for item in nested:
                if isinstance(item, dict):
                    found = extract_audio_url(item, _depth=_depth + 1)
                    if found:
                        return found
    return None


def download_bytes(url: str, *, timeout: float = 120.0) -> tuple[bytes, Optional[str]]:
    """Download the generated audio file. Returns ``(content, content_type)``.

    Raises :class:`SoniloAPIError` on failure; callers should treat this as
    non-fatal (the URL/metadata is still useful even if the download fails).
    """
    response = requests.get(url, timeout=timeout)
    if not response.ok:
        raise SoniloAPIError(f"Could not download generated audio (HTTP {response.status_code}).")
    return response.content, response.headers.get("Content-Type")
