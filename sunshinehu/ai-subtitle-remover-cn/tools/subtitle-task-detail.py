from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.api import call_api


class SubtitleTaskDetailTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        task_id = str(tool_parameters.get("taskId") or "").strip()
        if not task_id or len(task_id) > 128:
            yield self.create_json_message({"code": -200, "message": "A valid task ID is required."})
            return
        try:
            yield self.create_json_message(call_api(self.runtime.credentials, "/open/taskDetail", {"taskId": task_id}))
        except ValueError as exc:
            yield self.create_json_message({"code": -500, "message": str(exc)})
