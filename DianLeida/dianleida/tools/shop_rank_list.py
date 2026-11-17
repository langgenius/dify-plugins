# -*- coding: utf-8 -*-
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.runner import run_mcp_tool

SPEC = {
    "rankType": "str",
    "keyword": "str",
    "keywordType": "str",
    "shopKeyword": "str",
    "tradeMedalList": "list_int:,",
    "memberTypeList": "list:,",
    "beginTpYear": "int",
    "endTpYear": "int",
    "pageIndex": "int",
    "pageSize": "int",
    "__advanced__": "merge"
}


class ShopRankListTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        yield self.create_text_message(
            run_mcp_tool(
                tool="shop_rank_list",
                envelope="request",
                spec=SPEC,
                tool_parameters=tool_parameters,
                credentials=self.runtime.credentials,
            )
        )
