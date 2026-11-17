# -*- coding: utf-8 -*-
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.runner import run_mcp_tool

SPEC = {
    "pageIndex": "int",
    "pageSize": "int"
}


class MonitorShopListTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        yield self.create_text_message(
            run_mcp_tool(
                tool="monitor_shop_list",
                envelope=None,
                spec=SPEC,
                tool_parameters=tool_parameters,
                credentials=self.runtime.credentials,
            )
        )
