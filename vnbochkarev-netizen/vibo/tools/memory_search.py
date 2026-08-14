from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import requests

API_BASE = "https://wwwvibo.com"


class MemorySearchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("vibo_key")
        if not api_key:
            yield self.create_text_message(
                "ViBo key is not configured. Set it in the plugin credentials."
            )
            return
        query = (tool_parameters.get("query") or "").strip()
        if not query:
            yield self.create_text_message("A query is required.")
            return
        limit = int(tool_parameters.get("limit") or 5)

        try:
            resp = requests.post(
                f"{API_BASE}/memory/search",
                json={"key": str(api_key), "query": query, "limit": limit},
                timeout=30,
            )
            data = resp.json()
            if not data.get("ok"):
                yield self.create_text_message(
                    f"ViBo search failed: {data.get('message', 'error')}"
                )
                return
            facts = data.get("facts") or data.get("results") or []
            if not facts:
                yield self.create_text_message("No relevant facts found in memory.")
                return
            text = "\n".join(
                f"- {f.get('label', f.get('content', ''))}: {f.get('content', '')}"
                for f in facts[:limit]
            )
            savings = data.get("saved_tokens")
            if savings:
                text += f"\n\n(saved {savings} tokens)"
            yield self.create_text_message(text)
        except requests.RequestException as exc:
            yield self.create_text_message(f"ViBo API error: {exc}")
