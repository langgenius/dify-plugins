import requests
from typing import Any, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class AnalyzeTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        analysis_type = tool_parameters.get("type")
        query = tool_parameters.get("query")

        if not analysis_type:
            yield self.create_text_message("Error: Platform type is required")
            return

        if not query:
            yield self.create_text_message("Error: Query is required")
            return

        try:
            response = requests.post(
                "https://api.dinq.me/api/v1/dinq/analyze",
                json={"type": analysis_type, "query": query},
                headers={"Content-Type": "application/json"},
                timeout=120,
            )

            data = response.json()

            if data.get("code") != 0:
                yield self.create_text_message(
                    f"Error: {data.get('message', 'Unknown error')}"
                )
                return

            result = data.get("data", {})
            yield self.create_json_message(result)

        except requests.Timeout:
            yield self.create_text_message(
                "Error: Request timeout. The analysis may take longer for complex profiles."
            )
        except requests.RequestException as e:
            yield self.create_text_message(f"Error: Request failed - {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
