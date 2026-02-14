from collections.abc import Generator
from typing import Any
import json
import ssl
from urllib.request import Request, urlopen

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class SeedreamGenerateTool(Tool):
    def _get_ssl_context(self, credentials: dict[str, Any]):
        ca_bundle_path = credentials.get("ca_bundle_path")
        ssl_verify = credentials.get("ssl_verify", True)
        if isinstance(ssl_verify, str):
            ssl_verify = ssl_verify.strip().lower() in {"true", "1", "yes", "y"}
        if ssl_verify is False:
            return ssl._create_unverified_context()
        if ca_bundle_path:
            return ssl.create_default_context(cafile=ca_bundle_path)
        return ssl.create_default_context()

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        credentials = self.runtime.credentials
        endpoint_url = credentials.get("endpoint_url", "").rstrip("/")
        if not endpoint_url:
            raise ValueError("API Endpoint Host is required.")

        headers = {
            "Content-Type": "application/json",
            "Accept-Charset": "utf-8",
        }
        api_key = credentials.get("api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload: dict[str, Any] = {
            "model": tool_parameters["model"],
            "prompt": tool_parameters["prompt"],
        }

        image = tool_parameters.get("image")
        if image:
            payload["image"] = image

        size = tool_parameters.get("size")
        if size:
            payload["size"] = size

        response_format = tool_parameters.get("response_format")
        if response_format:
            payload["response_format"] = response_format

        watermark = tool_parameters.get("watermark")
        if watermark is not None:
            payload["watermark"] = watermark

        request = Request(
            f"{endpoint_url}/images/generations",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        context = self._get_ssl_context(credentials)
        with urlopen(request, timeout=60, context=context) as response:
            status_code = response.getcode()
            response_text = response.read().decode("utf-8", errors="replace")
        if status_code != 200:
            raise ValueError(f"API request failed with status code {status_code}: {response_text}")
        yield self.create_json_message(json.loads(response_text))
