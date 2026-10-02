from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.api import call_api


class QueryCreditsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            yield self.create_json_message(call_api(self.runtime.credentials, "/open/queryCredits", {}))
        except ValueError as exc:
            yield self.create_json_message({"code": -500, "message": str(exc)})
