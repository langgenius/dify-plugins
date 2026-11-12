"""Fixed-destination HTTPS client. Never retry writes or expose response errors."""

import json
import re
from typing import Any

import httpx

BASE_URL = "https://api.sentfrom.ai"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
ALLOWED_ROUTES = {
    "GET": re.compile(r"/v1/(?:account|inboxes|messages(?:/[0-9a-f-]{36})?|drafts/[0-9a-f-]{36})\Z"),
    "POST": re.compile(r"/v1/(?:inboxes|messages(?:/[0-9a-f-]{36}/reply)?|drafts)\Z"),
}
SAFE_CODES = frozenset({
    "account_suspended", "account_expired", "account_unclaimed", "claim_required",
    "sending_paused", "sending_disabled", "owner_blocked", "owner_send_limit_reached",
    "daily_send_limit_reached", "hourly_send_limit_reached", "monthly_send_limit_reached",
    "send_limit_reached", "rate_limit_exceeded", "recipient_suppressed", "recipient_blocked",
    "too_many_recipients", "duplicate_blast_blocked", "abuse_content_blocked",
    "send_outcome_pending", "idempotency_conflict", "client_id_conflict",
    "inbox_limit_reached", "address_taken", "address_reserved", "draft_not_sendable",
    "shared_free_sending_limit_reached", "message_blocked", "abuse_similarity_unavailable",
    "invalid_client_id", "storage_limit_reached", "attachment_too_large",
    "rate_limited", "duplicate_content_blocked",
})


class SentFromAIError(ValueError):
    """Safe error: contains neither credentials nor upstream/user content."""


class SentFromAIClient:
    def __init__(self, api_key: str, *, transport: httpx.BaseTransport | None = None):
        if (not isinstance(api_key, str) or not api_key.strip() or not api_key.isascii()
                or any(ord(c) <= 32 or ord(c) == 127 for c in api_key.strip())):
            raise SentFromAIError("Enter a valid SentFromAI API key in the provider credentials.")
        self._api_key = api_key.strip()
        self._transport = transport

    def request(self, method: str, path: str, *, params: dict | None = None,
                body: dict | None = None) -> dict[str, Any]:
        if method not in ALLOWED_ROUTES or not ALLOWED_ROUTES[method].fullmatch(path):
            raise SentFromAIError("Unsupported SentFromAI operation.")
        write_note = (" This write may already have completed. Check its outcome before retrying; "
                      "for sends/replies keep the original client_id and identical payload.") if method == "POST" else ""
        try:
            with httpx.Client(
                base_url=BASE_URL, headers={"Authorization": f"Bearer {self._api_key}",
                    "Accept": "application/json", "User-Agent": "sentfromai-dify/0.1.0"},
                timeout=httpx.Timeout(30.0, connect=10.0), follow_redirects=False,
                trust_env=False, verify=True, transport=self._transport,
            ) as client:
                with client.stream(method, path, params=params, json=body) as response:
                    if 300 <= response.status_code < 400:
                        raise SentFromAIError("SentFromAI returned a redirect; it was not followed." + write_note)
                    chunks, size = [], 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > MAX_RESPONSE_BYTES:
                            raise SentFromAIError("SentFromAI response exceeds the plugin's 8 MiB limit." + write_note)
                        chunks.append(chunk)
                    try:
                        data = json.loads(b"".join(chunks))
                    except (ValueError, UnicodeError):
                        data = None
                    if response.status_code >= 400:
                        code = data.get("error") if isinstance(data, dict) else None
                        code = code if isinstance(code, str) and code in SAFE_CODES else None
                        detail = f" ({code})" if code else ""
                        status = response.status_code
                        if status == 401:
                            advice = "Check or replace the API key in provider credentials."
                        elif status in (402, 403, 410, 429):
                            advice = "Check account status, entitlements and sending controls in SentFromAI; do not bypass restrictions."
                        elif status == 409:
                            advice = "Inspect the existing operation before retrying; preserve the original client_id and payload for sends/replies."
                        else:
                            advice = "Check the operation inputs or contact support@sentfrom.ai."
                        if status == 429:
                            retry = response.headers.get("Retry-After", "")
                            if retry.isascii() and retry.isdigit() and len(retry) <= 6:
                                advice += f" Retry-After: {int(retry)} seconds."
                        if status >= 500:
                            advice += write_note
                        raise SentFromAIError(f"SentFromAI HTTP {status}{detail}. {advice}")
                    if not isinstance(data, dict):
                        raise SentFromAIError("SentFromAI returned an invalid JSON object." + write_note)
                    return data
        except httpx.HTTPError:
            raise SentFromAIError("SentFromAI network request failed." + write_note) from None
