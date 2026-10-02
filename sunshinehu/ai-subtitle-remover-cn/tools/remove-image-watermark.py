from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.api import call_upload, require_token


class RemoveImageWatermarkTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            operation_id = require_token(tool_parameters.get("operationId"), "operationId")
            if len(operation_id) > 64:
                raise ValueError("operationId must be at most 64 characters")
            result = call_upload(self.runtime.credentials, "/open/removeImageWatermark",
                                 tool_parameters.get("file"),
                                 {"operationId": operation_id, "sync": "true"})
            yield self.create_json_message(result)
        except ValueError as exc:
            yield self.create_json_message({"code": -200, "message": str(exc)})
