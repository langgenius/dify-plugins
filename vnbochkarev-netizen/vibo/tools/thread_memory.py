from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import requests

API_BASE = "https://wwwvibo.com"


class ThreadMemoryTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("vibo_key")
        if not api_key:
            yield self.create_text_message(
                "ViBo key is not configured. Set it in the plugin credentials."
            )
            return
        action = tool_parameters.get("action") or "add"
        text = (tool_parameters.get("text") or "").strip()
        if not text:
            yield self.create_text_message("Text is required.")
            return

        try:
            if action == "context":
                resp = requests.post(
                    f"{API_BASE}/memory/thread",
                    json={"key": str(api_key), "action": "context"},
                    timeout=30,
                )
            else:
                resp = requests.post(
                    f"{API_BASE}/memory/thread",
                    json={
                        "key": str(api_key),
                        "action": "add",
                        "role": tool_parameters.get("role") or "user",
                        "text": text,
                    },
                    timeout=30,
                )
            data = resp.json()
            if data.get("ok"):
                msg = data.get("context") or data.get("message") or "Done"
                yield self.create_text_message(str(msg))
            else:
                yield self.create_text_message(
                    f"Thread memory failed: {data.get('message', 'error')}"
                )
        except requests.RequestException as exc:
            yield self.create_text_message(f"ViBo API error: {exc}")
