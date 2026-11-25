"""Shared credential handling for Prompt Efficiently tools."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.pe_api import PEError, SessionExpired, check_session, verify_code  # noqa: E402


def _storage_get(storage, key):
    try:
        value = storage.get(key)
        if isinstance(value, (bytes, bytearray)):
            return bytes(value).decode("utf-8", "replace")
        if isinstance(value, str):
            return value
    except Exception:
        pass
    return ""


def ensure_token(tool, force_refresh=False):
    """Return a live PE session token for the saved credential email.

    The emailed six-digit code is exchanged for a token on first use and the
    token is cached in the plugin's persistent storage, keyed by email.
    """
    creds = tool.runtime.credentials or {}
    email = (creds.get("pe_email") or "").strip().lower()
    code = (creds.get("pe_code") or "").strip()
    if not email:
        raise PEError("Add your Prompt Efficiently account email in the plugin settings.")
    key = "pe_token:" + email
    storage = tool.session.storage
    token = "" if force_refresh else _storage_get(storage, key)
    if token and check_session(token):
        return token
    token = ""
    if not code:
        raise PEError(
            "No working PE session and no sign-in code saved. Open the plugin settings, clear the sign-in code field and save to get a fresh code emailed, then paste it and save again."
        )
    token = verify_code(email, code)
    try:
        storage.set(key, token.encode("utf-8"))
    except Exception:
        pass
    return token


def drop_token(tool):
    creds = tool.runtime.credentials or {}
    email = (creds.get("pe_email") or "").strip().lower()
    try:
        tool.session.storage.delete("pe_token:" + email)
    except Exception:
        pass
