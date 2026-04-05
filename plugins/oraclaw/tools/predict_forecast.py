import json
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class PredictForecastTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("api_key", "")
        endpoint = self.runtime.credentials.get("api_endpoint", "https://oraclaw-api.onrender.com")

        data = json.loads(tool_parameters["data"]) if isinstance(tool_parameters["data"], str) else tool_parameters["data"]
        steps = int(tool_parameters.get("steps", 3))
        method = tool_parameters.get("method", "arima")

        response = requests.post(
            f"{endpoint}/api/v1/predict/forecast",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"data": data, "steps": steps, "method": method},
            timeout=15,
        )

        if response.status_code != 200:
            yield self.create_text_message(f"OraClaw API error {response.status_code}: {response.text}")
            return

        result = response.json()
        yield self.create_text_message(json.dumps(result, indent=2))
