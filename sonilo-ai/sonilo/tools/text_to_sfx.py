from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._client import SoniloAPIError, SoniloTaskError, resolve_generation
from tools._payloads import build_sfx_text_fields, coerce_duration
from tools._result import emit_success, emit_task_error

PATH = "/v1/text-to-sfx"
TOOL_LABEL = "Sonilo text-to-sound-effects"
MIN_DURATION_SECONDS = 1
MAX_DURATION_SECONDS = 180


class TextToSfxTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("api_key")
        if not api_key:
            yield self.create_text_message(
                "Sonilo API Key is not configured. Set it in the plugin credentials."
            )
            return

        prompt = (tool_parameters.get("prompt") or "").strip()
        if not prompt:
            yield self.create_text_message(
                "A sound-effect prompt is required (e.g. 'glass bottle shattering on concrete')."
            )
            return

        duration, duration_error = coerce_duration(
            tool_parameters.get("duration"),
            min_seconds=MIN_DURATION_SECONDS,
            max_seconds=MAX_DURATION_SECONDS,
        )
        if duration_error:
            yield self.create_text_message(f"Invalid duration: {duration_error}")
            return

        audio_format = (tool_parameters.get("audio_format") or "").strip() or None

        fields = build_sfx_text_fields(prompt=prompt, duration=duration, audio_format=audio_format)

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
            filename="sonilo_sfx",
        )
