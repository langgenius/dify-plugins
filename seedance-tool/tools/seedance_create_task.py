from collections.abc import Generator
from typing import Any
import json
import ssl
from urllib.request import Request, urlopen

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class SeedanceCreateTaskTool(Tool):
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

        content: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": tool_parameters["prompt"],
            }
        ]

        first_frame_url = tool_parameters.get("first_frame_url")
        if first_frame_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": first_frame_url},
                    "role": "first_frame",
                }
            )

        last_frame_url = tool_parameters.get("last_frame_url")
        if last_frame_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": last_frame_url},
                    "role": "last_frame",
                }
            )

        reference_images = tool_parameters.get("reference_images")
        if reference_images:
            for url in [item.strip() for item in reference_images.split(",") if item.strip()]:
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": url},
                        "role": "reference_image",
                    }
                )

        payload: dict[str, Any] = {
            "model": tool_parameters["model"],
            "content": content,
        }

        ratio = tool_parameters.get("ratio")
        if ratio:
            payload["ratio"] = ratio

        duration = tool_parameters.get("duration")
        if duration is not None:
            payload["duration"] = duration

        resolution = tool_parameters.get("resolution")
        if resolution:
            payload["resolution"] = resolution

        seed = tool_parameters.get("seed")
        if seed is not None:
            payload["seed"] = seed

        camera_fixed = tool_parameters.get("camera_fixed")
        if camera_fixed is not None:
            payload["camera_fixed"] = camera_fixed

        generate_audio = tool_parameters.get("generate_audio")
        if generate_audio is not None:
            payload["generate_audio"] = generate_audio

        watermark = tool_parameters.get("watermark")
        if watermark is not None:
            payload["watermark"] = watermark

        request = Request(
            f"{endpoint_url}/contents/generations/tasks",
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
