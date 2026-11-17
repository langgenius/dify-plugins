# -*- coding: utf-8 -*-
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.runner import run_mcp_tool

SPEC = {
    "date": "str",
    "pageType": "int",
    "keyWord": "str",
    "searchType": "int",
    "sortField": "str",
    "sortType": "str",
    "categoryIdList": "list:,",
    "pageIndex": "int",
    "pageSize": "int",
    "__advanced__": "merge"
}


class ProductBillboardListTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        yield self.create_text_message(
            run_mcp_tool(
                tool="product_billboard_list",
                envelope="req",
                spec=SPEC,
                tool_parameters=tool_parameters,
                credentials=self.runtime.credentials,
            )
        )
