from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ListBucketsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("engram_api_key")
        base_url = (self.runtime.credentials.get("engram_api_base") or "https://api.lumetra.io").rstrip("/")

        try:
            limit = int(tool_parameters.get("limit")) if tool_parameters.get("limit") is not None else 50
        except (TypeError, ValueError):
            limit = 50
        try:
            offset = int(tool_parameters.get("offset")) if tool_parameters.get("offset") is not None else 0
        except (TypeError, ValueError):
            offset = 0
        limit = max(1, min(limit, 500))
        offset = max(0, offset)

        try:
            response = requests.get(
                f"{base_url}/v1/buckets",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"limit": limit, "offset": offset},
                timeout=30,
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
        buckets = payload.get("buckets") or []
        yield self.create_text_message(f"{len(buckets)} bucket(s) returned.")
