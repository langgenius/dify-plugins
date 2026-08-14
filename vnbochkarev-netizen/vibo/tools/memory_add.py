from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import requests

API_BASE = "https://wwwvibo.com"


class MemoryAddTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("vibo_key")
        if not api_key:
            yield self.create_text_message(
                "ViBo key is not configured. Set it in the plugin credentials."
            )
            return
        label = (tool_parameters.get("label") or "").strip()
        content = (tool_parameters.get("content") or "").strip()
        if not label or not content:
            yield self.create_text_message("Label and content are required.")
            return
        level = tool_parameters.get("level") or "L1"

        try:
            resp = requests.post(
                f"{API_BASE}/memory/add",
                json={"key": str(api_key), "label": label, "content": content, "level": level},
                timeout=30,
            )
            data = resp.json()
            if data.get("ok"):
                yield self.create_text_message(
                    f"Saved to memory: {label} ({level})"
                )
            else:
                yield self.create_text_message(
                    f"Save failed: {data.get('message', 'error')}"
                )
        except requests.RequestException as exc:
            yield self.create_text_message(f"ViBo API error: {exc}")
