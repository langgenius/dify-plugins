from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from lib.client import SentFromAIClient
from lib.operations import execute


class ReplyToMessageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        result = execute("reply_to_message", tool_parameters, SentFromAIClient(self.runtime.credentials.get("api_key")))
        yield self.create_json_message(result)
        yield self.create_variable_message("result", result)
