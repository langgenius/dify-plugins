from typing import Any, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://www.apocdata.com/api/blade-dataplatform/open/data"


class MacroTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        indicator = tool_parameters.get("indicator", "")
        if not indicator:
            yield self.create_text_message("Please provide an indicator type (CPI, GDP, PMI, M2, etc.)")
            return

        try:
            resp = requests.get(
                f"{BASE_URL}/macro-latest",
                params={"type": indicator},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("success"):
                result = data.get("data", {})
                text = f"Latest {indicator} Data:\n"
                for key, value in result.items():
                    text += f"{key}: {value}\n"
                yield self.create_text_message(text)
            else:
                yield self.create_text_message(f"Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            yield self.create_text_message(f"Request failed: {str(e)}")
