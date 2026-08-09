from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._base import e2a_client


class ReplyToMessageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield self.create_json_message(
            e2a_client(self).reply_to_message(
                tool_parameters.get("message_id", ""),
                text=tool_parameters.get("text", ""),
                reply_all=tool_parameters.get("reply_all", False),
                idempotency_key=tool_parameters.get("idempotency_key"),
            )
        )
