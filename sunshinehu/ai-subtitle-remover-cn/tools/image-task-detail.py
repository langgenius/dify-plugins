from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.api import call_api, require_token


class ImageTaskDetailTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            task_id = require_token(tool_parameters.get("taskId"), "taskId")
            yield self.create_json_message(call_api(self.runtime.credentials,
                                                    "/open/imageWatermarkTaskDetail", {"taskId": task_id}))
        except ValueError as exc:
            yield self.create_json_message({"code": -200, "message": str(exc)})
