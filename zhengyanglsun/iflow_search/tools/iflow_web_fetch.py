from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import build_client
from ._errors import friendly_error_message


class IFlowWebFetchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("iflow_api_key")
        if not api_key:
            yield self.create_text_message(
                "iFlow API Key is not configured. Set it in the plugin credentials."
            )
            return

        url = (tool_parameters.get("url") or "").strip()
        if not url:
            yield self.create_text_message("URL is required.")
            return
        if not (url.startswith("http://") or url.startswith("https://")):
            yield self.create_text_message("URL must start with http:// or https://.")
            return

        try:
            with build_client(api_key=api_key) as client:
                response = client.web_fetch(url=url)
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return

        payload = {
            "url": response.url or url,
            "title": response.title,
            "content": response.content,
            "from_cache": response.from_cache,
            "took_ms": response.took_ms,
        }
        yield self.create_json_message(payload)
        yield self.create_text_message(_format_fetch_result(payload))


def _format_fetch_result(payload: dict[str, Any]) -> str:
    title = payload.get("title") or "(no title)"
    url = payload.get("url") or ""
    content = payload.get("content") or ""
    if not content:
        return f"# {title}\n{url}\n\n(iFlow returned an empty content body.)"
    return f"# {title}\n{url}\n\n{content}"
