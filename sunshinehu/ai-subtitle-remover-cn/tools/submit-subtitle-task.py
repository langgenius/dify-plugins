from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.api import call_api, require_token, require_url


class SubmitSubtitleTaskTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            width = int(tool_parameters.get("width"))
            height = int(tool_parameters.get("height"))
            duration = float(tool_parameters.get("duration"))
            if min(width, height) < 1 or max(width, height) > 1920 or min(width, height) > 1080:
                raise ValueError("Video dimensions exceed the supported range (maximum 1920×1080).")
            if not 1 <= duration <= 600:
                raise ValueError("Video duration must be 1–600 seconds.")
            params = {
                "videoUrl": require_url(tool_parameters.get("videoUrl")),
                "width": width, "height": height, "duration": duration,
                "x1": 0, "y1": 0, "x2": 0, "y2": 0,
            }
            if tool_parameters.get("idempotencyKey"):
                params["idempotencyKey"] = require_token(tool_parameters["idempotencyKey"], "idempotencyKey")
            result = call_api(self.runtime.credentials, "/open/submitTask", params, timeout=60)
            if result.get("code") == 200 and not params.get("idempotencyKey"):
                result["notice"] = "Repeating this submission without an idempotency key may create another billable task."
            yield self.create_json_message(result)
        except (TypeError, ValueError) as exc:
            yield self.create_json_message({"code": -200, "message": str(exc)})
