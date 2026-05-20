from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ClearMemoriesTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("engram_api_key")
        base_url = (self.runtime.credentials.get("engram_api_base") or "https://api.lumetra.io").rstrip("/")

        bucket = (tool_parameters.get("bucket") or "").strip()
        if not bucket:
            yield self.create_text_message("clear_memories requires a bucket name.")
            return

        try:
            response = requests.delete(
                f"{base_url}/v1/buckets/{bucket}/memories",
                headers={"Authorization": f"Bearer {api_key}"},
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

        try:
            payload = response.json()
        except ValueError:
            payload = {"status": "cleared", "bucket": bucket}

        yield self.create_json_message(payload)
        cleared = payload.get("cleared_count")
        yield self.create_text_message(
            f"Cleared bucket '{bucket}'"
            + (f" ({cleared} memories removed)." if cleared is not None else ".")
        )
