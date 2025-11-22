from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests
class MetaSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage,None]:
        keyword= tool_parameters.get("keyWord", "")
        # url = f"http://192.168.1.180:9003/list?keyword={keyword}"
        url = f"http://1.95.69.135:9008/list?keyword={keyword}"
        response = requests.get(url)
        content = response.json()
        yield self.create_json_message({
            "result": content
        })
