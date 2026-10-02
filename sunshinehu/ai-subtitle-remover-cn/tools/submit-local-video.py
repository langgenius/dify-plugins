from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.api import call_api, call_upload, require_token


class SubmitLocalVideoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            key = require_token(tool_parameters.get("idempotencyKey"), "idempotencyKey")
            coords = [tool_parameters.get(name) for name in ("x1", "y1", "x2", "y2")]
            rectangle = None
            if any(value is not None for value in coords):
                if any(value is None for value in coords):
                    raise ValueError("Supply all four rectangle coordinates or none")
                if any(isinstance(value, bool) or not isinstance(value, (int, float)) or
                       not float(value).is_integer() for value in coords):
                    raise ValueError("Rectangle coordinates must be whole pixel numbers")
                rectangle = tuple(int(value) for value in coords)
            uploaded = call_upload(self.runtime.credentials, "/open/uploadVideo",
                                   tool_parameters.get("file"), timeout=180)
            if uploaded.get("code") != 200:
                yield self.create_json_message(uploaded)
                return
            required = ("videoUrl", "width", "height", "duration")
            if any(not uploaded.get(field) for field in required):
                raise ValueError("The upload did not return complete video metadata")
            params = {field: uploaded[field] for field in required}
            params.update({"x1": 0, "y1": 0, "x2": 0, "y2": 0, "idempotencyKey": key})
            if rectangle is not None:
                x1, y1, x2, y2 = rectangle
                if not (0 <= x1 < x2 <= int(uploaded["width"]) and
                        0 <= y1 < y2 <= int(uploaded["height"])):
                    raise ValueError("Rectangle must be inside the uploaded video")
                params.update({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
            if uploaded.get("coverUrl"):
                params["coverUrl"] = uploaded["coverUrl"]
            result = call_api(self.runtime.credentials, "/open/submitTask", params, timeout=60)
            yield self.create_json_message(result)
        except (TypeError, ValueError) as exc:
            yield self.create_json_message({"code": -200, "message": str(exc)})
