from collections.abc import Generator
from typing import Any

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://api.anakin.io/v1"


class SearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("api_key")

        prompt = tool_parameters.get("prompt")
        if not prompt:
            yield self.create_text_message("Error: Search query is required")
            return

        limit = tool_parameters.get("limit", 5)

        payload = {
            "prompt": prompt,
            "limit": int(limit)
        }

        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    f"{BASE_URL}/search",
                    headers={
                        "X-API-Key": api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

                if response.status_code == 401:
                    yield self.create_text_message("Error: Invalid API Key")
                    return
                elif response.status_code == 402:
                    yield self.create_text_message("Error: Plan upgrade required")
                    return
                elif response.status_code != 200:
                    yield self.create_text_message(f"Error: {response.text}")
                    return

                result = response.json()
                yield self.create_json_message(result)

        except httpx.TimeoutException:
            yield self.create_text_message("Error: Request timeout")
        except httpx.RequestError as e:
            yield self.create_text_message(f"Error: {str(e)}")
