from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._base import e2a_client


class SendMessageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield self.create_json_message(
            e2a_client(self).send_message(
                to=tool_parameters.get("to") or [],
                subject=tool_parameters.get("subject", ""),
                text=tool_parameters.get("text", ""),
                idempotency_key=tool_parameters.get("idempotency_key"),
            )
        )
