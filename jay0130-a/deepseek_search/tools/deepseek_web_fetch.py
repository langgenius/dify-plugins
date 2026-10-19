from __future__ import annotations

from typing import Any, Generator
from urllib.parse import urlsplit

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import DeepSeekToolsClient, MAX_URL_CHARS
from ._errors import friendly_error_message


class DeepSeekWebFetchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("deepseek_api_key")
        if not api_key:
            yield self.create_text_message(
                "DeepSeek API Key is not configured. Set it in the plugin credentials."
            )
            return

        raw_url = (tool_parameters.get("url") or "").strip()
        error = _validate_url(raw_url)
        if error:
            yield self.create_text_message(error)
            return

        try:
            with DeepSeekToolsClient(api_key=str(api_key)) as client:
                payload = client.fetch(url=raw_url)
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return

        title = str(payload.get("title") or "")
        content = str(payload.get("content") or "")
        yield self.create_json_message({"url": raw_url, "title": title, "content": content})
        yield self.create_text_message(_format_page(raw_url, title, content))


def _validate_url(raw_url: str) -> str | None:
    if not raw_url:
        return "URL is required."
    if len(raw_url) > MAX_URL_CHARS:
        return f"URL must be at most {MAX_URL_CHARS} characters (got {len(raw_url)})."
    try:
        parts = urlsplit(raw_url)
    except ValueError:
        return "URL could not be parsed."
    if parts.scheme not in ("http", "https"):
        return "URL must start with http:// or https://."
    if not parts.netloc:
        return "URL must include a host."
    if parts.username or parts.password or "@" in parts.netloc:
        return "URL must not contain a username or password."
    return None


def _format_page(url: str, title: str, content: str) -> str:
    if not content:
        return f"The page at {url} returned no extractable content."
    heading = title or url
    return f"# {heading}\n\nSource: {url}\n\n{content}"
