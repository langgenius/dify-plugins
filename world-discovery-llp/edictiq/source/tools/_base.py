from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.mcp_client import EdictIqMcpError, call_mcp


class EdictIqMcpTool(Tool):
    """Each Dify tool delegates unchanged parameters to its Edict IQ MCP peer."""

    mcp_tool_name: str = ""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        if self.mcp_tool_name == "create_target_monitor":
            if not tool_parameters.get("idempotency_key"):
                yield self.create_text_message("An explicit user-requested monitor and idempotency_key are required.")
                return
        try:
            payload = call_mcp(
                self.mcp_tool_name,
                tool_parameters,
                self.runtime.credentials.get("access_token", ""),
            )
            yield self.create_json_message(payload)
        except EdictIqMcpError as exc:
            yield self.create_text_message(str(exc))
