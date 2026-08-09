from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._base import e2a_client


class ListMessagesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield self.create_json_message(
            e2a_client(self).list_messages(
                limit=tool_parameters.get("limit", 20),
                direction=tool_parameters.get("direction") or "inbound",
                read_status=tool_parameters.get("read_status") or "auto",
                cursor=tool_parameters.get("cursor"),
            )
        )
