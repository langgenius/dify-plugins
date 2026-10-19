"""Map DeepSeek Tools API errors to user-safe Dify messages.

Two principles:

* The user's API key value must never appear in any error text. Error strings
  are built from HTTP status codes and server messages only.
* Switch on the HTTP status code rather than exception identity, so the
  mapping stays stable as the API evolves.
"""

from __future__ import annotations

from ._client import DeepSeekToolsError


def friendly_error_message(exc: BaseException, *, fallback: str = "DeepSeek request failed.") -> str:
    """Return a short, key-free string suitable for surfacing to Dify users."""
    if not isinstance(exc, DeepSeekToolsError):
        return fallback

    status = exc.status_code
    if status == 401:
        return (
            "DeepSeek rejected the API key (unauthorized). "
            "Re-enter a valid key in the plugin credentials."
        )
    if status == 403:
        return (
            "DeepSeek denied access to the Tools API for this account. "
            "Confirm your account has Search/Fetch enabled."
        )
    if status == 422:
        return f"DeepSeek rejected the request parameters. {exc}"
    if status == 429:
        return (
            "DeepSeek rate limit exceeded (Search and Fetch each allow 5 requests "
            "per second per account). Slow down and retry."
        )
    if 500 <= (status or 0) <= 599:
        return "DeepSeek server error. Retry once; if it persists, check the DeepSeek status page."
    return str(exc) or fallback
