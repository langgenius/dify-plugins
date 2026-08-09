from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, patch

import pytest
from dify_plugin.entities.tool import ToolRuntime
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import Tool

from provider.e2a import E2AProvider
from tools.get_message import GetMessageTool
from tools.list_messages import ListMessagesTool
from tools.reply_to_message import ReplyToMessageTool
from tools.send_message import SendMessageTool
from tools.whoami import WhoamiTool


API_KEY = "e2a_test_provider_key"
TOOL_MODULES = (
    "tools.whoami",
    "tools.list_messages",
    "tools.get_message",
    "tools.send_message",
    "tools.reply_to_message",
)


def _tool(tool_class: Any) -> Any:
    runtime = ToolRuntime(
        credentials={"e2a_api_key": API_KEY},
        user_id="user_example",
        session_id="session_example",
    )
    return tool_class(runtime=runtime, session=SimpleNamespace())


def _json_result(tool: Any, parameters: dict[str, Any]) -> dict[str, Any]:
    message = next(tool._invoke(parameters))
    assert message.type.value == "json"
    return message.message.json_object


def test_provider_validates_with_whoami() -> None:
    provider = E2AProvider()
    with patch("provider.e2a.E2AClient") as client_class:
        client_class.return_value.whoami.return_value = {
            "scope": "agent",
            "agent_email": "inbox@example.test",
        }

        provider._validate_credentials({"e2a_api_key": f"  {API_KEY}  "})

    client_class.assert_called_once_with(API_KEY)
    client_class.return_value.whoami.assert_called_once_with()


def test_provider_wraps_failures_without_echoing_the_key() -> None:
    provider = E2AProvider()
    with patch("provider.e2a.E2AClient", side_effect=ValueError(f"bad {API_KEY}")):
        with pytest.raises(ToolProviderCredentialValidationError) as caught:
            provider._validate_credentials({"e2a_api_key": API_KEY})

    assert API_KEY not in str(caught.value)


@pytest.mark.parametrize("module_name", TOOL_MODULES)
def test_each_tool_module_exposes_exactly_one_tool_subclass(module_name: str) -> None:
    module = importlib.import_module(module_name)
    subclasses = {
        value
        for value in vars(module).values()
        if isinstance(value, type) and value is not Tool and issubclass(value, Tool)
    }

    assert len(subclasses) == 1


@pytest.mark.parametrize(
    ("tool_class", "parameters", "method", "expected_call"),
    [
        (WhoamiTool, {}, "whoami", {}),
        (
            ListMessagesTool,
            {"limit": 12, "direction": "all", "read_status": "all", "cursor": "next_1"},
            "list_messages",
            {"limit": 12, "direction": "all", "read_status": "all", "cursor": "next_1"},
        ),
        (
            GetMessageTool,
            {"message_id": "msg_example"},
            "get_message",
            {"message_id": "msg_example"},
        ),
        (
            SendMessageTool,
            {
                "to": ["recipient@example.test"],
                "subject": "Synthetic subject",
                "text": "Synthetic body",
                "idempotency_key": "dify_send_example",
            },
            "send_message",
            {
                "to": ["recipient@example.test"],
                "subject": "Synthetic subject",
                "text": "Synthetic body",
                "idempotency_key": "dify_send_example",
            },
        ),
        (
            ReplyToMessageTool,
            {
                "message_id": "msg_example",
                "text": "Synthetic reply",
                "reply_all": True,
                "idempotency_key": "dify_reply_example",
            },
            "reply_to_message",
            {
                "message_id": "msg_example",
                "text": "Synthetic reply",
                "reply_all": True,
                "idempotency_key": "dify_reply_example",
            },
        ),
    ],
)
def test_tools_map_dify_inputs_to_the_client(
    tool_class: Any,
    parameters: dict[str, Any],
    method: str,
    expected_call: dict[str, Any],
) -> None:
    result = {"operation": method, "successful": True}
    with patch("tools._base.E2AClient") as client_class:
        client = client_class.return_value
        getattr(client, method).return_value = result

        assert _json_result(_tool(tool_class), parameters) == result

    client_class.assert_called_once_with(API_KEY)
    mocked_method: Mock = getattr(client, method)
    if method == "whoami":
        mocked_method.assert_called_once_with()
    elif method in {"get_message", "reply_to_message"}:
        message_id = expected_call.pop("message_id")
        mocked_method.assert_called_once_with(message_id, **expected_call)
    else:
        mocked_method.assert_called_once_with(**expected_call)
