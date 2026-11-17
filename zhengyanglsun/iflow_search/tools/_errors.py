"""Map iFlow Search SDK exceptions to user-safe Dify messages.

Two principles:

* The user's API key value must never appear in any error text. The SDK
  itself does not echo keys (:mod:`iflow_search._redact` handles that), but
  this module belt-and-braces by only formatting ``exc.code`` /
  ``exc.message`` and never anything from credentials.
* Switch on the SDK's stable ``code`` strings (``api_unauthorized``,
  ``business_rate_limited``, etc.) — not on class identity — to keep the
  mapping resilient as the SDK refines its class hierarchy.
"""

from __future__ import annotations


def friendly_error_message(exc: BaseException, *, fallback: str = "iFlow request failed.") -> str:
    """Return a short, key-free string suitable for surfacing to Dify users.

    Falls back to ``fallback`` when ``exc`` is not an SDK exception or carries
    no recognizable ``code``.
    """
    code = getattr(exc, "code", None)
    message = getattr(exc, "message", None) or str(exc) or fallback
    if not code:
        return fallback

    if code in {"api_unauthorized", "business_invalid_api_key"}:
        return "iFlow rejected the API key (unauthorized). Re-enter a valid key in the plugin credentials."
    if code in {"api_rate_limited", "business_rate_limited"}:
        return "iFlow rate limit exceeded. Reduce request rate or upgrade your plan, then retry."
    if code == "business_insufficient_credits":
        return "iFlow account is out of credits. Top up the account before retrying."
    if code == "network_timeout":
        return "iFlow request timed out. Retry once; if it persists, check your network connectivity."
    if code == "network_error":
        return "Network error reaching iFlow. Verify outbound connectivity to api.iflow.cn."
    if code == "business_no_results":
        return "iFlow returned no results for the supplied query."
    if code == "business_web_fetch_parse_failed":
        return "iFlow could not parse the target URL. Try a different page or use a direct article URL."
    return f"iFlow error ({code}): {message}"
