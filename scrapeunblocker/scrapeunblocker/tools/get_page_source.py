from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from scrapeunblocker_client import ScrapeUnblockerClient, ScrapeUnblockerError


class GetPageSourceTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        url = str(tool_parameters.get("url", "")).strip()
        if not url:
            yield self.create_json_message({"success": False, "error": "url is required"})
            return

        parsed_data = bool(tool_parameters.get("parsed_data", False))
        proxy_country = str(tool_parameters.get("proxy_country", "")).strip() or None

        try:
            client = ScrapeUnblockerClient.from_credentials(self.runtime.credentials)
            content = client.get_page_source(url, parsed_data=parsed_data, proxy_country=proxy_country)
        except ScrapeUnblockerError as exc:
            yield self.create_json_message({"success": False, "error": str(exc)})
            return

        yield self.create_text_message(content)
        yield self.create_json_message(
            {
                "success": True,
                "url": url,
                "parsed_data": parsed_data,
                "content_length": len(content),
            }
        )
