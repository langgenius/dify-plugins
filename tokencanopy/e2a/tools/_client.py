from __future__ import annotations

import re
from email.utils import parseaddr
from typing import Any, Iterable
from urllib.parse import quote

import requests


API_BASE_URL = "https://api.e2a.dev"
PLUGIN_VERSION = "0.0.1"
REQUEST_TIMEOUT = (5.0, 20.0)
MAX_LIST_LIMIT = 50
MAX_RECIPIENTS = 50
MAX_BODY_CHARS = 1_048_576

_SAFE_ERROR_CODE = re.compile(r"^[a-z][a-z0-9_]{0,79}$")
_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_SAFE_IDEMPOTENCY_KEY = re.compile(r"^[A-Za-z0-9._:-]{1,200}$")

_ERROR_MESSAGES = {
    "unauthorized": "E2A rejected the API key.",
    "forbidden": "The E2A API key is not allowed to perform this operation.",
    "not_found": "E2A could not find the requested resource.",
    "invalid_request": "E2A rejected the request parameters.",
    "invalid_recipient": "E2A rejected a recipient address.",
    "too_many_recipients": "The message has too many recipients.",
    "message_not_yet_delivered": "The source message is not ready for a threaded reply yet.",
    "limit_exceeded": "The E2A account quota has been reached.",
    "rate_limited": "The E2A API rate limit was reached. Retry after a short wait.",
    "payload_too_large": "The E2A request is too large.",
}


class E2AAPIError(RuntimeError):
    """A credential-safe E2A API or transport failure."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        request_id: str | None = None,
    ) -> None:
        self.code = code
        self.status_code = status_code
        self.request_id = request_id

        details: list[str] = []
        if code:
            details.append(code)
        if request_id:
            details.append(f"request_id={request_id}")
        suffix = f" ({', '.join(details)})" if details else ""
        super().__init__(f"{message}{suffix}")


class E2AClient:
    """Small fixed-host client for the five Dify E2A tools."""

    def __init__(self, credential: str, *, session: Any | None = None) -> None:
        self._credential = _required_header_value(credential, "E2A_API_KEY")
        self.session = session or requests.Session()

    def whoami(self) -> dict[str, Any]:
        account = self._request("GET", "/v1/account")
        self._agent_email_from_account(account)
        return account

    def list_messages(
        self,
        *,
        limit: Any = 20,
        direction: str = "inbound",
        read_status: str = "auto",
        cursor: str | None = None,
    ) -> dict[str, Any]:
        validated_limit = _bounded_int(limit, "limit", minimum=1, maximum=MAX_LIST_LIMIT)
        validated_direction = _choice(direction, "direction", {"inbound", "outbound", "all"})
        validated_read_status = _choice(
            read_status, "read_status", {"auto", "unread", "read", "all"}
        )
        resolved_read_status = (
            "unread"
            if validated_read_status == "auto" and validated_direction == "inbound"
            else "all"
            if validated_read_status == "auto"
            else validated_read_status
        )
        validated_cursor = _optional_string(cursor, "cursor", maximum=4096)

        agent_email = self._agent_email()
        params: dict[str, Any] = {
            "limit": validated_limit,
            "direction": validated_direction,
            "read_status": resolved_read_status,
        }
        if validated_cursor:
            params["cursor"] = validated_cursor

        return self._request(
            "GET",
            f"/v1/agents/{quote(agent_email, safe='')}/messages",
            params=params,
        )

    def get_message(self, message_id: str) -> dict[str, Any]:
        agent_email = self._agent_email()
        safe_message_id = quote(_resource_id(message_id), safe="")
        result = self._request(
            "GET",
            f"/v1/agents/{quote(agent_email, safe='')}/messages/{safe_message_id}",
        )

        bounded_result = dict(result)
        if "raw_message" in bounded_result:
            bounded_result.pop("raw_message")
            bounded_result["raw_message_omitted"] = True
        return bounded_result

    def send_message(
        self,
        *,
        to: Iterable[str],
        subject: str,
        text: str,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        recipients = _recipients(to)
        payload = {
            "to": recipients,
            "subject": _required_text(subject, "subject", maximum=2000, single_line=True),
            "text": _required_text(text, "text", maximum=MAX_BODY_CHARS),
        }
        return self._send(
            path=f"/v1/agents/{quote(self._agent_email(), safe='')}/messages",
            payload=payload,
            idempotency_key=idempotency_key,
        )

    def reply_to_message(
        self,
        message_id: str,
        *,
        text: str,
        reply_all: bool = False,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(reply_all, bool):
            raise ValueError("reply_all must be true or false.")
        payload = {
            "text": _required_text(text, "text", maximum=MAX_BODY_CHARS),
            "reply_all": reply_all,
        }
        return self._send(
            path=(
                f"/v1/agents/{quote(self._agent_email(), safe='')}/messages/"
                f"{quote(_resource_id(message_id), safe='')}/reply"
            ),
            payload=payload,
            idempotency_key=idempotency_key,
        )

    def _send(
        self,
        *,
        path: str,
        payload: dict[str, Any],
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        result = self._request(
            "POST",
            path,
            json_body=payload,
            idempotency_key=_idempotency_key(idempotency_key),
        )
        status = result.get("status")
        enriched = dict(result)
        enriched["held"] = status == "pending_review"
        enriched["successful"] = status != "failed"
        return enriched

    def _agent_email(self) -> str:
        return self._agent_email_from_account(self._request("GET", "/v1/account"))

    @staticmethod
    def _agent_email_from_account(account: dict[str, Any]) -> str:
        if account.get("scope") != "agent":
            raise E2AAPIError("This plugin requires an agent-scoped E2A_API_KEY.")
        agent_email = account.get("agent_email")
        if not isinstance(agent_email, str) or not agent_email.strip():
            raise E2AAPIError("The agent-scoped E2A_API_KEY has no agent mailbox identity.")
        return _required_text(agent_email, "agent_email", maximum=320, single_line=True)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._credential}",
            "User-Agent": f"e2a-dify-plugin/{PLUGIN_VERSION}",
        }
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        try:
            response = self.session.request(
                method=method,
                url=f"{API_BASE_URL}{path}",
                headers=headers,
                params=params,
                json=json_body,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise E2AAPIError("Could not reach the E2A API.") from exc

        payload = _json_object(response)
        if 200 <= response.status_code < 300:
            return payload

        error = payload.get("error") if isinstance(payload.get("error"), dict) else {}
        code = _safe_metadata(error.get("code"), _SAFE_ERROR_CODE)
        request_id = _safe_metadata(error.get("request_id"), _SAFE_REQUEST_ID)
        if request_id is None:
            request_id = _safe_metadata(response.headers.get("X-Request-Id"), _SAFE_REQUEST_ID)
        message = _ERROR_MESSAGES.get(code, f"E2A API request failed with HTTP {response.status_code}.")
        raise E2AAPIError(
            message,
            code=code,
            status_code=response.status_code,
            request_id=request_id,
        )


def _json_object(response: Any) -> dict[str, Any]:
    try:
        payload = response.json()
    except (TypeError, ValueError) as exc:
        raise E2AAPIError("The E2A API returned an invalid JSON response.") from exc
    if not isinstance(payload, dict):
        raise E2AAPIError("The E2A API returned an unexpected response shape.")
    return payload


def _safe_metadata(value: Any, pattern: re.Pattern[str]) -> str | None:
    if isinstance(value, str) and pattern.fullmatch(value):
        return value
    return None


def _required_header_value(value: Any, name: str) -> str:
    text = _required_text(value, name, maximum=4096, single_line=True)
    return text


def _required_text(value: Any, name: str, *, maximum: int, single_line: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string.")
    text = value.strip()
    if not text:
        raise ValueError(f"{name} is required.")
    if "\x00" in text or (single_line and ("\r" in text or "\n" in text)):
        raise ValueError(f"{name} contains unsupported control characters.")
    if len(text) > maximum:
        raise ValueError(f"{name} must be at most {maximum} characters.")
    return text


def _optional_string(value: Any, name: str, *, maximum: int) -> str | None:
    if value is None or value == "":
        return None
    return _required_text(value, name, maximum=maximum, single_line=True)


def _resource_id(value: Any) -> str:
    return _required_text(value, "message_id", maximum=512, single_line=True)


def _bounded_int(value: Any, name: str, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer from {minimum} to {maximum}.")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer from {minimum} to {maximum}.") from exc
    if isinstance(value, float) and not value.is_integer():
        raise ValueError(f"{name} must be an integer from {minimum} to {maximum}.")
    if not minimum <= number <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")
    return number


def _choice(value: Any, name: str, choices: set[str]) -> str:
    if not isinstance(value, str) or value not in choices:
        rendered = ", ".join(sorted(choices))
        raise ValueError(f"{name} must be one of: {rendered}.")
    return value


def _recipients(values: Iterable[str]) -> list[str]:
    if isinstance(values, (str, bytes)):
        candidates: list[Any] = [values]
    else:
        try:
            candidates = list(values)
        except TypeError as exc:
            raise ValueError("to must be a list of email addresses.") from exc
    if not candidates:
        raise ValueError("At least one recipient is required.")
    if len(candidates) > MAX_RECIPIENTS:
        raise ValueError(f"At most {MAX_RECIPIENTS} recipients are allowed.")

    recipients: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        text = _required_text(candidate, "recipient", maximum=320, single_line=True)
        _, address = parseaddr(text)
        if not address or address.count("@") != 1:
            raise ValueError("Each recipient must be a valid email address.")
        local, domain = address.rsplit("@", 1)
        if not local or not domain or "." not in domain:
            raise ValueError("Each recipient must be a valid email address.")
        if len(local.encode("utf-8")) > 64 or len(address.encode("utf-8")) > 254:
            raise ValueError("A recipient exceeds SMTP mailbox length limits.")
        normalized = address.casefold()
        if normalized not in seen:
            recipients.append(text)
            seen.add(normalized)
    return recipients


def _idempotency_key(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str) or not _SAFE_IDEMPOTENCY_KEY.fullmatch(value):
        raise ValueError(
            "idempotency_key must be 1-200 characters using letters, numbers, dot, underscore, colon, or hyphen."
        )
    return value
