from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import build_client
from ._errors import friendly_error_message


class IFlowImageSearchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("iflow_api_key")
        if not api_key:
            yield self.create_text_message(
                "iFlow API Key is not configured. Set it in the plugin credentials."
            )
            return

        query = (tool_parameters.get("query") or "").strip()
        if not query:
            yield self.create_text_message("Query is required.")
            return

        count = _coerce_count(tool_parameters.get("count"))

        try:
            with build_client(api_key=api_key) as client:
                response = client.image_search(query=query, count=count)
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return

        images = [
            {
                "image_url": img.image_url,
                "source_url": img.source_url,
                "title": img.title,
                "width": img.width,
                "height": img.height,
                "position": img.position,
            }
            for img in response.images
        ]
        payload = {
            "query": response.query or query,
            "count": len(images),
            "took_ms": response.took_ms,
            "images": images,
        }
        yield self.create_json_message(payload)
        yield self.create_text_message(_format_image_results(payload))


def _coerce_count(raw: Any) -> int | None:
    if raw is None or raw == "":
        return None
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return None
    if n < 1:
        return 1
    if n > 20:
        return 20
    return n


def _format_image_results(payload: dict[str, Any]) -> str:
    images = payload.get("images") or []
    if not images:
        return f"No iFlow image results for '{payload.get('query', '')}'."
    lines: list[str] = [f"# iFlow image search: {payload.get('query', '')}\n"]
    for idx, img in enumerate(images, 1):
        title = img.get("title") or "(no title)"
        image_url = img.get("image_url") or ""
        source_url = img.get("source_url") or ""
        lines.append(f"{idx}. {title}")
        if image_url:
            lines.append(f"   image: {image_url}")
        if source_url:
            lines.append(f"   source: {source_url}")
    return "\n".join(lines)
