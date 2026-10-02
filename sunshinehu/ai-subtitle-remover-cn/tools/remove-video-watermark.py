from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.api import call_api, require_token, require_url


class RemoveVideoWatermarkTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            params = {"videoUrl": require_url(tool_parameters.get("videoUrl"))}
            if tool_parameters.get("operationId"):
                operation_id = require_token(tool_parameters["operationId"], "operationId")
                if len(operation_id) > 64:
                    raise ValueError("operationId must be at most 64 characters.")
                params["operationId"] = operation_id
            yield self.create_json_message(call_api(self.runtime.credentials, "/open/removeVideoWatermark", params, timeout=90))
        except ValueError as exc:
            yield self.create_json_message({"code": -200, "message": str(exc)})
