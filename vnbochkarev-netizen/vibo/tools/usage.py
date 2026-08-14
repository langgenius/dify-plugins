from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import requests

API_BASE = "https://wwwvibo.com"


class UsageTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("vibo_key")
        if not api_key:
            yield self.create_text_message(
                "ViBo key is not configured. Set it in the plugin credentials."
            )
            return
        try:
            resp = requests.get(
                f"{API_BASE}/usage", params={"key": str(api_key)}, timeout=30
            )
            data = resp.json()
            if data.get("ok"):
                yield self.create_text_message(json_dumps(data))
            else:
                yield self.create_text_message(
                    f"Usage failed: {data.get('message', 'error')}"
                )
        except requests.RequestException as exc:
            yield self.create_text_message(f"ViBo API error: {exc}")


def json_dumps(d: dict) -> str:
    import json

    return json.dumps(d, ensure_ascii=False, indent=2)
