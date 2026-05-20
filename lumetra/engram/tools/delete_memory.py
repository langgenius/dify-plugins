from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DeleteMemoryTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("engram_api_key")
        base_url = (self.runtime.credentials.get("engram_api_base") or "https://api.lumetra.io").rstrip("/")

        memory_id = (tool_parameters.get("memory_id") or "").strip()
        bucket = (tool_parameters.get("bucket") or "").strip()
        if not memory_id or not bucket:
            yield self.create_text_message("delete_memory requires both memory_id and bucket.")
            return

        try:
            response = requests.delete(
                f"{base_url}/v1/buckets/{bucket}/memories/{memory_id}",
                headers={"Authorization": f"Bearer {api_key}"},
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

        try:
            payload = response.json()
        except ValueError:
            payload = {"status": "deleted", "memory_id": memory_id, "bucket": bucket}

        yield self.create_json_message(payload)
        yield self.create_text_message(f"Deleted memory {memory_id} from bucket '{bucket}'.")
