from collections.abc import Generator
from typing import Any

from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import AdanosTool


class CryptoSentimentTool(AdanosTool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield from self._invoke_client(
            lambda client: client.get_crypto_sentiment(
                tool_parameters.get("symbol"),
                from_date=tool_parameters.get("from_date"),
                to_date=tool_parameters.get("to_date"),
            )
        )
