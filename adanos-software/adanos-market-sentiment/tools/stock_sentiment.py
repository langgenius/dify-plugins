from collections.abc import Generator
from typing import Any

from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import AdanosTool


class StockSentimentTool(AdanosTool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield from self._invoke_client(
            lambda client: client.get_stock_sentiment(
                tool_parameters.get("ticker"),
                source=tool_parameters.get("source"),
                from_date=tool_parameters.get("from_date"),
                to_date=tool_parameters.get("to_date"),
            )
        )
