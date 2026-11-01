from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._client import SoniloAPIError, SoniloTaskError, resolve_generation
from tools._payloads import build_sfx_video_fields
from tools._result import emit_success, emit_task_error

PATH = "/v1/video-to-sfx"
TOOL_LABEL = "Sonilo video-to-sound-effects"


class VideoToSfxTool(Tool):
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
        audio_format = (tool_parameters.get("audio_format") or "").strip() or None

        fields = build_sfx_video_fields(video_url=video_url, prompt=prompt, audio_format=audio_format)

        try:
            result = resolve_generation(api_key, PATH, fields)
        except SoniloTaskError as exc:
            yield from emit_task_error(self, exc)
            return
        except SoniloAPIError as exc:
            yield self.create_text_message(str(exc))
            return

        yield from emit_success(
            self,
            tool_label=TOOL_LABEL,
            result=result,
            output_format=audio_format,
            filename="sonilo_sfx_video",
        )
