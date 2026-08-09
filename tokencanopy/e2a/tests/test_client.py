from __future__ import annotations

from collections import deque
from typing import Any

import pytest
import requests

from tools._client import E2AAPIError, E2AClient


AGENT_EMAIL = "inbox+triage@example.test"
API_KEY = "e2a_test_secret_value"


class FakeResponse:
    def __init__(
        self,
        status_code: int,
        payload: Any,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}

    def json(self) -> Any:
        if isinstance(self._payload, BaseException):
            raise self._payload
        return self._payload


class FakeSession:
    def __init__(self, *responses: FakeResponse | BaseException) -> None:
        self.responses = deque(responses)
        self.calls: list[dict[str, Any]] = []

    def request(self, **kwargs: Any) -> FakeResponse:
        self.calls.append(kwargs)
        response = self.responses.popleft()
        if isinstance(response, BaseException):
            raise response
        return response


def account_payload(*, scope: str = "agent", agent_email: str | None = AGENT_EMAIL) -> dict[str, Any]:
    return {
        "scope": scope,
        "agent_email": agent_email,
        "plan_code": "free",
        "user": {"email": "owner@example.test"},
        "usage": {"messages_month": 2},
        "limits": {"max_messages_month": 100},
        "upgrade_url": "https://e2a.dev/pricing",
    }


def test_whoami_requires_an_agent_scoped_key() -> None:
    session = FakeSession(FakeResponse(200, account_payload(scope="account", agent_email=None)))

    with pytest.raises(E2AAPIError, match="agent-scoped"):
        E2AClient(API_KEY, session=session).whoami()


def test_list_messages_is_bounded_and_encodes_the_agent_path() -> None:
    page = {"items": [{"id": "msg_example", "subject": "Synthetic notice"}], "next_cursor": "next_1"}
    session = FakeSession(FakeResponse(200, account_payload()), FakeResponse(200, page))

    result = E2AClient(API_KEY, session=session).list_messages(
        limit=25,
        direction="all",
        read_status="all",
        cursor="cursor_1",
    )

    assert result == page
    assert session.calls[1]["url"] == (
        "https://api.e2a.dev/v1/agents/inbox%2Btriage%40example.test/messages"
    )
    assert session.calls[1]["params"] == {
        "limit": 25,
        "direction": "all",
        "read_status": "all",
        "cursor": "cursor_1",
    }
    assert session.calls[1]["headers"]["Authorization"] == f"Bearer {API_KEY}"
    assert session.calls[1]["timeout"] == (5.0, 20.0)


def test_list_messages_auto_read_status_avoids_outbound_filter_conflict() -> None:
    session = FakeSession(
        FakeResponse(200, account_payload()),
        FakeResponse(200, {"items": [], "next_cursor": None}),
    )

    E2AClient(API_KEY, session=session).list_messages(direction="outbound", read_status="auto")

    assert session.calls[1]["params"]["read_status"] == "all"


@pytest.mark.parametrize("limit", [0, 51, "many"])
def test_list_messages_rejects_unbounded_or_invalid_limits(limit: Any) -> None:
    with pytest.raises(ValueError, match="limit"):
        E2AClient(API_KEY, session=FakeSession()).list_messages(limit=limit)


def test_get_message_encodes_the_id_and_omits_raw_mime() -> None:
    payload = {
        "id": "msg_example",
        "subject": "Synthetic notice",
        "body": {"text": "Safe synthetic body"},
        "raw_message": "base64-raw-mime",
    }
    session = FakeSession(FakeResponse(200, account_payload()), FakeResponse(200, payload))

    result = E2AClient(API_KEY, session=session).get_message("msg_example/part?")

    assert result == {
        "id": "msg_example",
        "subject": "Synthetic notice",
        "body": {"text": "Safe synthetic body"},
        "raw_message_omitted": True,
    }
    assert session.calls[1]["url"].endswith("/messages/msg_example%2Fpart%3F")


def test_send_message_validates_and_marks_pending_review_as_successful_hold() -> None:
    held = {
        "message_id": "msg_held_example",
        "status": "pending_review",
        "approval_expires_at": "2026-08-09T12:00:00Z",
    }
    session = FakeSession(FakeResponse(200, account_payload()), FakeResponse(202, held))

    result = E2AClient(API_KEY, session=session).send_message(
        to=["reviewer@example.test"],
        subject="Synthetic review request",
        text="Please review this synthetic example.",
        idempotency_key="dify_example_send_1",
    )

    assert result == {**held, "held": True, "successful": True}
    assert session.calls[1]["method"] == "POST"
    assert session.calls[1]["json"] == {
        "to": ["reviewer@example.test"],
        "subject": "Synthetic review request",
        "text": "Please review this synthetic example.",
    }
    assert session.calls[1]["headers"]["Idempotency-Key"] == "dify_example_send_1"


@pytest.mark.parametrize(
    ("to", "subject", "text"),
    [
        ([], "Subject", "Body"),
        (["not-an-email"], "Subject", "Body"),
        (["safe@example.test\r\nBcc: hidden@example.test"], "Subject", "Body"),
        (["safe@example.test"], "", "Body"),
        (["safe@example.test"], "Subject", ""),
    ],
)
def test_send_message_rejects_invalid_inputs(to: list[str], subject: str, text: str) -> None:
    with pytest.raises(ValueError):
        E2AClient(API_KEY, session=FakeSession()).send_message(to=to, subject=subject, text=text)


def test_reply_uses_the_message_subresource_to_preserve_threading() -> None:
    sent = {"message_id": "msg_reply_example", "status": "accepted"}
    session = FakeSession(FakeResponse(200, account_payload()), FakeResponse(202, sent))

    result = E2AClient(API_KEY, session=session).reply_to_message(
        "msg_source_example",
        text="A synthetic threaded reply.",
        reply_all=True,
        idempotency_key="dify_example_reply_1",
    )

    assert result == {**sent, "held": False, "successful": True}
    assert session.calls[1]["url"].endswith("/messages/msg_source_example/reply")
    assert session.calls[1]["json"] == {
        "text": "A synthetic threaded reply.",
        "reply_all": True,
    }


@pytest.mark.parametrize(
    ("status", "successful"),
    [
        ("sent", True),
        ("scheduled", True),
        ("review_approved", True),
        ("failed", False),
        ("future_status", None),
        (None, None),
        ({"unexpected": "shape"}, None),
    ],
)
def test_send_result_does_not_guess_unknown_open_set_statuses(
    status: Any, successful: bool | None
) -> None:
    payload = {"message_id": "msg_result_example"}
    if status is not None:
        payload["status"] = status
    session = FakeSession(FakeResponse(200, account_payload()), FakeResponse(202, payload))

    result = E2AClient(API_KEY, session=session).send_message(
        to=["reviewer@example.test"],
        subject="Synthetic status check",
        text="Exercise the open status contract.",
        idempotency_key="dify_example_status_1",
    )

    assert result["successful"] is successful


def test_api_errors_never_echo_server_content_or_credentials() -> None:
    response = FakeResponse(
        400,
        {
            "error": {
                "code": "invalid_request",
                "message": f"bad body contained {API_KEY} and private content",
                "request_id": "req_example",
            }
        },
    )

    with pytest.raises(E2AAPIError) as caught:
        E2AClient(API_KEY, session=FakeSession(response)).whoami()

    rendered = str(caught.value)
    assert API_KEY not in rendered
    assert "private content" not in rendered
    assert "invalid_request" in rendered
    assert "req_example" in rendered


def test_connection_errors_are_redacted() -> None:
    session = FakeSession(requests.Timeout(f"timeout with {API_KEY}"))

    with pytest.raises(E2AAPIError) as caught:
        E2AClient(API_KEY, session=session).whoami()

    assert str(caught.value) == "Could not reach the E2A API."
    assert API_KEY not in str(caught.value)
