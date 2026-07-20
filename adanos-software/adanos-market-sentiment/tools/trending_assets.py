from collections.abc import Generator
from typing import Any

from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import AdanosTool


class TrendingAssetsTool(AdanosTool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield from self._invoke_client(
            lambda client: client.get_trending(
                asset_type=tool_parameters.get("asset_type"),
                source=tool_parameters.get("source"),
                limit=tool_parameters.get("limit", 20),
                from_date=tool_parameters.get("from_date"),
                to_date=tool_parameters.get("to_date"),
            )
        )
