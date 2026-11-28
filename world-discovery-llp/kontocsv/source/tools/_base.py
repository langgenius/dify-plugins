"""Shared implementation for the eight existing KontoCSV MCP tools."""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.mcp_client import KontoCsvMcpError, call_mcp


class KontoCsvTool(Tool):
    mcp_tool_name = ""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            # A model-generated truthy string must never authorize a paid action.
            if self.mcp_tool_name == "convert_bank_statement_for_accounting":
                if tool_parameters.get("confirmedByUser") is not True:
                    raise KontoCsvMcpError(
                        "Ask for the user's explicit confirmation of the prepared conversion and credits."
                    )
            result = call_mcp(
                self.mcp_tool_name,
                tool_parameters,
                self.runtime.credentials.get("access_token", ""),
            )
            yield self.create_json_message(result)
        except KontoCsvMcpError as exc:
            yield self.create_text_message(str(exc))
