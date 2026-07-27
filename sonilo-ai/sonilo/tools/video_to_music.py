from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._client import (
    SoniloAPIError,
    SoniloTaskError,
    download_bytes,
    extract_audio_url,
    resolve_generation,
)
from tools._payloads import build_video_url_payload, guess_mime_type, result_summary

PATH = "/v1/video-to-music"
TOOL_LABEL = "Sonilo video-to-music"


class VideoToMusicTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("api_key")
        if not api_key:
            yield self.create_text_message(
                "Sonilo API Key is not configured. Set it in the plugin credentials."
            )
            return

        video_url = (tool_parameters.get("video_url") or "").strip()
        if not video_url:
            yield self.create_text_message(
                "A public or signed HTTPS video_url is required. This tool does not accept "
                "raw video file uploads -- host the video first, then pass its URL."
            )
            return

        prompt = (tool_parameters.get("prompt") or "").strip() or None
        mode = (tool_parameters.get("mode") or "").strip() or None
        output_format = (tool_parameters.get("output_format") or "").strip() or None

        payload = build_video_url_payload(
            video_url=video_url, prompt=prompt, mode=mode, output_format=output_format
        )

        try:
            result = resolve_generation(api_key, PATH, payload)
        except (SoniloAPIError, SoniloTaskError) as exc:
            yield self.create_text_message(str(exc))
            return

        audio_url = extract_audio_url(result)
        task_id = result.get("task_id") or result.get("id")
        status = result.get("status")

        json_payload = {
            "success": bool(audio_url),
            "audio_url": audio_url,
            "task_id": task_id,
            "status": status,
            "duration": result.get("duration") or result.get("duration_seconds"),
            "raw": result,
        }
        yield self.create_json_message(json_payload)
        yield self.create_text_message(
            result_summary(tool_label=TOOL_LABEL, audio_url=audio_url, task_id=task_id, status=status)
        )

        if audio_url:
            try:
                content, content_type = download_bytes(audio_url)
            except SoniloAPIError as exc:
                yield self.create_text_message(f"Generated soundtrack URL is ready, but downloading it failed: {exc}")
            else:
                mime = guess_mime_type(output_format, content_type)
                yield self.create_blob_message(blob=content, meta={"mime_type": mime, "filename": "sonilo_soundtrack"})
