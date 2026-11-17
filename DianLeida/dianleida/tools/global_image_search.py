# -*- coding: utf-8 -*-
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.runner import run_mcp_tool

SPEC = {
    "platform": "str",
    "imgUrl": "str",
    "imgBase64": "str",
    "amazonSite": "nest:amazon.site",
    "tiktokCountryCode": "nest:tiktok.countryCode",
    "tiktokSort": "nest_int:tiktok.sort",
    "tiktokContinuation": "nest_json:tiktok.continuation",
    "__advanced__": "merge"
}


class GlobalImageSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        yield self.create_text_message(
            run_mcp_tool(
                tool="global_image_search",
                envelope="req",
                spec=SPEC,
                tool_parameters=tool_parameters,
                credentials=self.runtime.credentials,
            )
        )
