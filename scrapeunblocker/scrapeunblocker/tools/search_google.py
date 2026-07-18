from __future__ import annotations

import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from scrapeunblocker_client import ScrapeUnblockerClient, ScrapeUnblockerError


class SearchGoogleTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        keyword = str(tool_parameters.get("keyword", "")).strip()
        if not keyword:
            yield self.create_json_message({"success": False, "error": "keyword is required"})
            return

        pages_raw = tool_parameters.get("pages_to_check")
        try:
            pages_to_check = int(pages_raw) if pages_raw else None
        except (TypeError, ValueError):
            pages_to_check = None
        proxy_country = str(tool_parameters.get("proxy_country", "")).strip() or None

        try:
            client = ScrapeUnblockerClient.from_credentials(self.runtime.credentials)
            payload = client.search_google(keyword, pages_to_check=pages_to_check, proxy_country=proxy_country)
        except ScrapeUnblockerError as exc:
            yield self.create_json_message({"success": False, "error": str(exc)})
            return

        organic = payload.get("organic") if isinstance(payload, dict) else None
        results = organic if isinstance(organic, list) else []

        yield self.create_text_message(json.dumps(results, ensure_ascii=False))
        yield self.create_json_message(
            {
                "success": True,
                "keyword": keyword,
                "results": results,
                "count": len(results),
            }
        )
