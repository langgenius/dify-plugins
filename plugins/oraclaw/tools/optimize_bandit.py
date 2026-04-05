import json
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class OptimizeBanditTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("api_key", "")
        endpoint = self.runtime.credentials.get("api_endpoint", "https://oraclaw-api.onrender.com")

        arms = json.loads(tool_parameters["arms"]) if isinstance(tool_parameters["arms"], str) else tool_parameters["arms"]
        algorithm = tool_parameters.get("algorithm", "ucb1")

        response = requests.post(
            f"{endpoint}/api/v1/optimize/bandit",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"arms": arms, "algorithm": algorithm},
            timeout=15,
        )

        if response.status_code != 200:
            yield self.create_text_message(f"OraClaw API error {response.status_code}: {response.text}")
            return

        result = response.json()
        yield self.create_text_message(json.dumps(result, indent=2))
