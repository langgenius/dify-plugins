from typing import Any, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://www.apocdata.com/api/blade-dataplatform/open/data"


class LimitTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        trade_date = tool_parameters.get("trade_date", "")
        kind = tool_parameters.get("kind", "U")

        params = {"kind": kind}
        if trade_date:
            params["trade_date"] = trade_date

        try:
            resp = requests.get(
                f"{BASE_URL}/limit-list",
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("success"):
                result = data.get("data", [])
                limit_type = "Limit Up" if kind == "U" else "Limit Down"
                text = f"{limit_type} Stocks ({len(result)} total):\n"
                for item in result[:10]:  # Show first 10
                    text += f"- {item.get('name', 'N/A')} ({item.get('symbol', 'N/A')}): {item.get('close', 'N/A')}\n"
                if len(result) > 10:
                    text += f"... and {len(result) - 10} more\n"
                yield self.create_text_message(text)
            else:
                yield self.create_text_message(f"Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            yield self.create_text_message(f"Request failed: {str(e)}")
