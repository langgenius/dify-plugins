from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.common import markdown, search


class SerpKiteSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        payload = search(self.runtime.credentials, tool_parameters, "search")
        yield self.create_json_message(payload)
        yield self.create_text_message(markdown(payload))
