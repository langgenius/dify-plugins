from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ListMemoriesTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("engram_api_key")
        base_url = (self.runtime.credentials.get("engram_api_base") or "https://api.lumetra.io").rstrip("/")

        bucket = (tool_parameters.get("bucket") or "default").strip() or "default"
        limit_raw = tool_parameters.get("limit")
        try:
            limit = int(limit_raw) if limit_raw is not None else 20
        except (TypeError, ValueError):
            limit = 20
        limit = max(1, min(limit, 200))

        try:
            response = requests.get(
                f"{base_url}/v1/buckets/{bucket}/memories",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"limit": limit},
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
        memories = payload.get("memories") or []
        yield self.create_text_message(
            f"{len(memories)} memory(ies) in bucket '{bucket}' (total: {payload.get('total', len(memories))})."
        )
