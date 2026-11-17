# -*- coding: utf-8 -*-
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.runner import run_mcp_tool

SPEC = {
    "keyWord": "str",
    "searchType": "int",
    "cycle": "str",
    "sortField": "str",
    "sortType": "str",
    "beginPrice": "float",
    "endPrice": "float",
    "beginConsignPrice": "float",
    "endConsignPrice": "float",
    "beginStartQuantity": "int",
    "endStartQuantity": "int",
    "beginOrderCount": "int",
    "endOrderCount": "int",
    "offerType": "int",
    "companyType": "int",
    "sendTime": "list_int:,",
    "categoryIdList": "list:,",
    "pageIndex": "int",
    "pageSize": "int",
    "__advanced__": "merge"
}


class CrossBorderProductSearchListTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        yield self.create_text_message(
            run_mcp_tool(
                tool="cross_border_product_search_list",
                envelope="req",
                spec=SPEC,
                tool_parameters=tool_parameters,
                credentials=self.runtime.credentials,
            )
        )
