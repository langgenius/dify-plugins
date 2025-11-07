from collections.abc import Generator
from typing import Any, Mapping

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class EchoTool(Tool):
    def _invoke(self, tool_parameters: Mapping[str, Any]) -> Generator[ToolInvokeMessage]:
        text = tool_parameters.get("text", "")
        yield self.create_json_message({"echo": text})
