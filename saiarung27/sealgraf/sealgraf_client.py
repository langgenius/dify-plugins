"""Shared Sealgraf REST client for the Sealgraf Dify tool plugin.

The contract implemented here is taken from the production service code
(signed-evidence-engine, origin/main):

- Auth: an agent-scope API key in the ``X-API-Key`` header
  (``see/api.py`` ``caller()``; a bad or missing key is a 401 with
  ``{"detail": "invalid or missing API key"}``).
- ``POST /v1/preauthorize`` (201) takes ``CheckIn`` and answers with the
  ``_preauth_out`` shape; a decision token is present in that answer ONLY
  when the check itself minted one (an immediate ``allow``).
- ``POST /v1/preauthorize/{id}/decision-token`` claims the token an owner
  approval minted; refusals are 409 ``{"detail": ..., "code": ...}``.
- ``POST /v1/preauthorize/{id}/complete`` takes ``CompleteIn``
  (``decision_token``, ``completion_nonce``, ``evidence``) and returns the
  sealed receipt dict.
- ``GET /v1/preauthorize/{id}`` and ``GET /v1/receipts/{id}`` /
  ``GET /v1/receipts`` are the reads.

FAIL CLOSED: every transport error, timeout, non-2xx response, or
malformed body raises :class:`SealgrafError` (or its ``SealgrafApiError``
subclass). Nothing in this module ever fabricates a permission-shaped
result.
"""

from __future__ import annotations

import re
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://sealgraf.com"

# Explicit timeouts: a hung connection must become an error, never a
# silent wait and never a permission.
_TIMEOUT = httpx.Timeout(connect=5.0, read=20.0, write=10.0, pool=5.0)

# The canonical category ids (production: see/notify.py _CATEGORY_LABELS,
# mirrored by docs/AGENT_SETUP.md's canonical table). Closed list — the
# ids are sealed into history and must never be renamed.
CATEGORIES: tuple[str, ...] = (
    "groceries",
    "household",
    "dining",
    "travel",
    "software",
    "office_supplies",
    "shopping",
    "transport",
    "entertainment",
    "health",
    "supplies",
    "materials",
    "equipment",
    "fuel",
)

# Decision outcomes (production: see/models.py DecisionOutcome).
DECISION_OUTCOMES = frozenset({"allow", "deny", "needs_human_approval"})

# Completion-evidence payment vocabularies (production: see/service.py
# _PAYMENT_RAILS, _RAIL_REF_KINDS, _PAYMENT_PROVENANCES). Closed lists.
PAYMENT_RAILS = frozenset(
    {"link_stripe", "paypal", "stripe_api", "card_on_merchant", "other"}
)
RAIL_REF_KINDS = frozenset(
    {"charge", "payment_intent", "paypal_transaction", "other"}
)
PAYMENT_PROVENANCES = frozenset(
    {"browser_checkout", "rail_api", "merchant_confirmation"}
)

_LAST4 = re.compile(r"[0-9]{4}")
_CURRENCY = re.compile(r"[A-Za-z]{3}")


class SealgrafError(Exception):
    """Any failure talking to Sealgraf.

    Tools let this propagate: Dify marks the tool call failed, which is
    the only safe rendering of "we do not know" in a spend loop.
    """


class SealgrafApiError(SealgrafError):
    """The service answered with a non-2xx status."""

    def __init__(self, status_code: int, detail: str, code: str | None = None):
        self.status_code = status_code
        self.detail = detail
        self.code = code
        message = f"Sealgraf API error (HTTP {status_code}): {detail}"
        if code:
            message += f" [code: {code}]"
        super().__init__(message)


def normalize_base_url(raw: str | None) -> str:
    url = (raw or "").strip() or DEFAULT_BASE_URL
    url = url.rstrip("/")
    if not (url.startswith("https://") or url.startswith("http://")):
        raise SealgrafError(
            f"Sealgraf base URL must start with https:// or http://, got: {url!r}"
        )
    return url


class SealgrafClient:
    """One thin REST client over httpx, built from provider credentials."""

    def __init__(
        self,
        base_url: str | None,
        api_key: str | None,
        *,
        transport: httpx.BaseTransport | None = None,
    ):
        key = (api_key or "").strip()
        if not key:
            raise SealgrafError(
                "Sealgraf API key is missing. Set the agent-scope API key "
                "in the Sealgraf provider credentials."
            )
        self.base_url = normalize_base_url(base_url)
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={
                "X-API-Key": key,
                "Content-Type": "application/json",
                "User-Agent": "sealgraf-dify-plugin/0.1.0",
            },
            timeout=_TIMEOUT,
            transport=transport,
        )

    # -- transport ------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict | None = None,
        params: dict | None = None,
        expected: tuple[int, ...] = (200, 201),
    ) -> dict:
        try:
            response = self._http.request(
                method, path, json=json_body, params=params
            )
        except httpx.TimeoutException as exc:
            raise SealgrafError(
                f"Sealgraf request timed out ({method} {path}). "
                "Failing closed: no permission was granted."
            ) from exc
        except httpx.HTTPError as exc:
            raise SealgrafError(
                f"Sealgraf request failed ({method} {path}): {exc}. "
                "Failing closed: no permission was granted."
            ) from exc
        if response.status_code not in expected:
            detail = ""
            code = None
            try:
                payload = response.json()
            except ValueError:
                payload = None
            if isinstance(payload, dict):
                raw_detail = payload.get("detail")
                if isinstance(raw_detail, str):
                    detail = raw_detail
                elif raw_detail is not None:
                    detail = str(raw_detail)
                if isinstance(payload.get("code"), str):
                    code = payload["code"]
            if not detail:
                detail = response.text.strip()[:300] or "no detail provided"
            raise SealgrafApiError(response.status_code, detail, code)
        try:
            data = response.json()
        except ValueError as exc:
            raise SealgrafError(
                f"Malformed response from Sealgraf ({method} {path}): "
                "body is not valid JSON. Failing closed."
            ) from exc
        if not isinstance(data, dict):
            raise SealgrafError(
                f"Malformed response from Sealgraf ({method} {path}): "
                "expected a JSON object. Failing closed."
            )
        return data

    # -- endpoints --------------------------------------------------------

    def validate_key(self) -> None:
        """The lightest authenticated read an agent key may make:
        ``GET /v1/receipts?limit=1`` (production: see/api.py
        ``list_receipts`` — no scope restriction, unlike
        ``GET /v1/mandates``, which refuses agent-scope keys)."""
        data = self._request("GET", "/v1/receipts", params={"limit": 1},
                             expected=(200,))
        if not isinstance(data.get("items"), list):
            raise SealgrafError(
                "Malformed response from Sealgraf (GET /v1/receipts): "
                "expected an object with an 'items' list."
            )

    def check_permission(
        self,
        *,
        category: str,
        amount_minor: int,
        currency: str | None = None,
        counterparty: str | None = None,
        description: str | None = None,
        agent_id: str | None = None,
        mandate_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict:
        """POST /v1/preauthorize — body is production's ``CheckIn``."""
        action: dict[str, Any] = {
            "category": category,
            "amount_minor": amount_minor,
        }
        if agent_id:
            action["agent_id"] = agent_id
        if currency:
            action["currency"] = currency
        if counterparty:
            action["counterparty"] = counterparty
        if description:
            action["description"] = description
        body: dict[str, Any] = {"action": action}
        if mandate_id:
            body["mandate_id"] = mandate_id
        if idempotency_key:
            body["idempotency_key"] = idempotency_key
        return self._request("POST", "/v1/preauthorize", json_body=body,
                             expected=(200, 201))

    def claim_decision_token(self, preauth_id: str) -> dict:
        """POST /v1/preauthorize/{id}/decision-token (empty JSON body)."""
        return self._request(
            "POST", f"/v1/preauthorize/{preauth_id}/decision-token",
            json_body={}, expected=(200,),
        )

    def complete_purchase(
        self,
        preauth_id: str,
        *,
        decision_token: str,
        completion_nonce: str,
        evidence: dict,
    ) -> dict:
        """POST /v1/preauthorize/{id}/complete — body is ``CompleteIn``."""
        body = {
            "decision_token": decision_token,
            "completion_nonce": completion_nonce,
            "evidence": evidence,
        }
        return self._request(
            "POST", f"/v1/preauthorize/{preauth_id}/complete",
            json_body=body, expected=(200, 201),
        )

    def get_preauth(self, preauth_id: str) -> dict:
        """GET /v1/preauthorize/{id} — the ``_preauth_out`` shape."""
        return self._request("GET", f"/v1/preauthorize/{preauth_id}",
                             expected=(200,))

    def get_receipt(self, receipt_id: str) -> dict:
        """GET /v1/receipts/{id} — receipt row + completion summary."""
        return self._request("GET", f"/v1/receipts/{receipt_id}",
                             expected=(200,))


def client_from_credentials(
    credentials: dict | None,
    *,
    transport: httpx.BaseTransport | None = None,
) -> SealgrafClient:
    creds = credentials or {}
    return SealgrafClient(
        creds.get("sealgraf_base_url"),
        creds.get("sealgraf_api_key"),
        transport=transport,
    )


# -- response shaping -----------------------------------------------------
# Each parser validates the production response shape before a tool may
# present it. Anything unexpected raises SealgrafError: a response the
# plugin cannot understand is never rendered as a permission.


def _require_str(data: dict, field: str, context: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value:
        raise SealgrafError(
            f"Malformed response from Sealgraf ({context}): "
            f"'{field}' is missing or not a string. Failing closed."
        )
    return value


def parse_check_result(data: dict) -> dict:
    """Normalize a ``POST /v1/preauthorize`` answer (``_preauth_out``)."""
    preauth_id = _require_str(data, "preauth_id", "check_permission")
    decision = data.get("decision")
    if not isinstance(decision, dict):
        raise SealgrafError(
            "Malformed response from Sealgraf (check_permission): "
            "'decision' is missing or not an object. Failing closed."
        )
    outcome = decision.get("outcome")
    if outcome not in DECISION_OUTCOMES:
        raise SealgrafError(
            "Malformed response from Sealgraf (check_permission): "
            f"unknown decision outcome {outcome!r}. Failing closed."
        )
    state = data.get("state")
    if not isinstance(state, str) or not state:
        raise SealgrafError(
            "Malformed response from Sealgraf (check_permission): "
            "'state' is missing. Failing closed."
        )
    result: dict[str, Any] = {
        "preauth_id": preauth_id,
        "state": state,
        "outcome": outcome,
        "reason_code": decision.get("reason_code"),
        "mandate_id": data.get("mandate_id"),
        "mandate_version": data.get("mandate_version"),
        "receipt_id": data.get("receipt_id"),
        "token_expires_at": data.get("token_expires_at"),
        "ask_expires_at": data.get("ask_expires_at"),
        "replayed": bool(data.get("replayed", False)),
    }
    action = data.get("action")
    if isinstance(action, dict):
        result["amount_minor"] = action.get("amount_minor")
        result["currency"] = action.get("currency")
        result["category"] = action.get("category")
    if outcome == "allow":
        # An allow is only usable with the single-use decision token the
        # check minted. Production includes it in exactly this case; its
        # absence on a FRESH answer means the answer cannot be trusted —
        # fail closed. One documented exception (see/api.py, A5): an
        # idempotent replay (HTTP 200, "replayed": true) returns the
        # original record and deliberately does NOT re-serve the token
        # (only its hash is stored). That shape is surfaced honestly,
        # flagged, and never presented as a fresh permission.
        token = data.get("decision_token")
        if isinstance(token, str) and token:
            result["decision_token"] = token
        elif result["replayed"]:
            result["decision_token_redelivered"] = False
        else:
            raise SealgrafError(
                "Malformed response from Sealgraf (check_permission): "
                "outcome is 'allow' but no decision_token was returned. "
                "Failing closed: do not buy."
            )
    return result


def parse_claim_result(data: dict, preauth_id: str) -> dict:
    token = data.get("decision_token")
    if not isinstance(token, str) or not token:
        raise SealgrafError(
            "Malformed response from Sealgraf (claim_decision_token): "
            "no decision_token in the response. Failing closed."
        )
    return {
        "preauth_id": preauth_id,
        "claimed": True,
        "decision_token": token,
        "token_expires_at": data.get("token_expires_at"),
    }


def parse_complete_result(data: dict) -> dict:
    receipt_id = _require_str(data, "receipt_id", "complete_purchase")
    return {
        "sealed": True,
        "receipt_id": receipt_id,
        "preauth_id": data.get("preauth_id"),
        "entry_seq": data.get("entry_seq"),
        "amount_minor": data.get("amount_minor"),
        "currency": data.get("currency"),
        "mandate_id": data.get("mandate_id"),
        "created_at": data.get("created_at"),
    }


def parse_preauth_result(data: dict) -> dict:
    preauth_id = _require_str(data, "preauth_id", "get_receipt")
    decision = data.get("decision") if isinstance(data.get("decision"), dict) else {}
    action = data.get("action") if isinstance(data.get("action"), dict) else {}
    return {
        "found_via": "preauth",
        "preauth_id": preauth_id,
        "state": data.get("state"),
        "outcome": decision.get("outcome"),
        "reason_code": decision.get("reason_code"),
        "receipt_id": data.get("receipt_id"),
        "mandate_id": data.get("mandate_id"),
        "mandate_version": data.get("mandate_version"),
        "amount_minor": action.get("amount_minor"),
        "currency": action.get("currency"),
        "category": action.get("category"),
        "counterparty": action.get("counterparty"),
        "was_allowed": data.get("was_allowed"),
        "approved_at": data.get("approved_at"),
        "token_expires_at": data.get("token_expires_at"),
        "ask_expires_at": data.get("ask_expires_at"),
        "created_at": data.get("created_at"),
    }


def parse_receipt_result(data: dict) -> dict:
    receipt_id = _require_str(data, "receipt_id", "get_receipt")
    return {
        "found_via": "receipt",
        "receipt_id": receipt_id,
        "preauth_id": data.get("preauth_id"),
        "entry_seq": data.get("entry_seq"),
        "amount_minor": data.get("amount_minor"),
        "currency": data.get("currency"),
        "mandate_id": data.get("mandate_id"),
        "created_at": data.get("created_at"),
        "completion": data.get("completion"),
        "payment_flag": data.get("payment_flag"),
    }


# -- parameter validation ---------------------------------------------------
# Shared by the tools; runs BEFORE any HTTP call so bad input fails with
# a clear local message and never reaches the service.


def require_amount_minor(value: Any, field: str) -> int:
    if isinstance(value, bool) or value is None:
        raise SealgrafError(f"{field} is required and must be a positive integer (minor units).")
    if isinstance(value, float):
        if not value.is_integer():
            raise SealgrafError(f"{field} must be a whole number of minor units, got {value}.")
        value = int(value)
    if not isinstance(value, int):
        raise SealgrafError(f"{field} must be an integer (minor units), got {value!r}.")
    if value <= 0:
        raise SealgrafError(f"{field} must be greater than 0, got {value}.")
    return value


def optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def require_str(value: Any, field: str) -> str:
    text = optional_str(value)
    if text is None:
        raise SealgrafError(f"{field} is required.")
    return text


def validate_currency(value: Any) -> str | None:
    text = optional_str(value)
    if text is None:
        return None
    if _CURRENCY.fullmatch(text) is None:
        raise SealgrafError(f"currency must be a three-letter code, got {text!r}.")
    return text.upper()


def validate_last4(value: Any, field: str) -> str | None:
    text = optional_str(value)
    if text is None:
        return None
    if _LAST4.fullmatch(text) is None:
        raise SealgrafError(f"{field} must be exactly four digits, as a string.")
    return text
