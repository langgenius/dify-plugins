from typing import Any, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


BASE_URL = "https://www.apocdata.com/api/blade-dataplatform/open/data"


class StockTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        symbol = tool_parameters.get("symbol", "")
        if not symbol:
            yield self.create_text_message("Please provide a stock symbol")
            return

        try:
            resp = requests.get(
                f"{BASE_URL}/stock",
                params={"symbol": symbol},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("success"):
                result = data.get("data", {})
                text = f"Stock: {result.get('name', 'N/A')} ({symbol})\n"
                text += f"Industry: {result.get('industry', 'N/A')}\n"
                text += f"PE Ratio: {result.get('pe_ratio', 'N/A')}\n"
                text += f"PB Ratio: {result.get('pb_ratio', 'N/A')}\n"
                text += f"Total Market Cap: {result.get('total_mv', 'N/A')}\n"
                text += f"Circulating Market Cap: {result.get('circ_mv', 'N/A')}\n"
                yield self.create_text_message(text)
            else:
                yield self.create_text_message(f"Error: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            yield self.create_text_message(f"Request failed: {str(e)}")
