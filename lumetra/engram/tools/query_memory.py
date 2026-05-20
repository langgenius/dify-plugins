from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class QueryMemoryTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("engram_api_key")
        base_url = (self.runtime.credentials.get("engram_api_base") or "https://api.lumetra.io").rstrip("/")

        question = (tool_parameters.get("question") or "").strip()
        if not question:
            yield self.create_text_message("query_memory requires a non-empty question.")
            return

        bucket = (tool_parameters.get("bucket") or "default").strip() or "default"

        try:
            response = requests.post(
                f"{base_url}/v1/query",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"query": question, "bucket": bucket},
                timeout=60,
            )
        except requests.RequestException as exc:
            yield self.create_text_message(f"Engram request failed: {exc}")
            return

        if response.status_code >= 400:
            yield self.create_text_message(
                f"Engram returned HTTP {response.status_code}: {response.text[:300]}"
            )
            return

        payload = response.json()
        yield self.create_json_message(payload)
        answer = payload.get("answer")
        if answer:
            yield self.create_text_message(str(answer))
