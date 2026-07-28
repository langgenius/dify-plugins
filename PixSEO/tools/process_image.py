from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from _config import (
    API_BASE,
    DEFAULT_TIMEOUT,
    safe_api_call,
    validate_image_input,
    validate_url_input,
    yield_error,
)


class ProcessImageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials["pixseo_api_key"]
        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

        # Local privacy acceptance check
        if tool_parameters.get("privacy_accepted", False) is not True:
            yield from yield_error(
                self, "请先阅读隐私声明并设置 privacy_accepted=true"
            )
            return

        image_base64 = tool_parameters.get("image_base64", "")
        file_url = tool_parameters.get("file_url", "")

        if not image_base64 and not file_url:
            yield from yield_error(
                self, "请提供 image_base64 或 file_url 中的一个"
            )
            return

        if image_base64:
            err = validate_image_input(image_base64)
            if err:
                yield from yield_error(self, err)
                return

        if file_url:
            err = validate_url_input(file_url)
            if err:
                yield from yield_error(self, err)
                return

        payload: dict[str, Any] = {
            "remove_bg": tool_parameters.get("remove_bg", True),
            "compress": tool_parameters.get("compress", True),
            "return_image": tool_parameters.get("return_image", True),
            "privacy_accepted": True,
        }
        if image_base64:
            payload["image_base64"] = image_base64
        if file_url:
            payload["file_url"] = file_url

        try:
            resp = safe_api_call(
                self,
                "POST",
                f"{API_BASE}/api/v1/process/json",
                json=payload,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
            )
        except ValueError as e:
            yield from yield_error(self, str(e))
            return

        data = resp.json()
        steps = data.get("steps", {})

        user_tip = data.get("user_tip")
        status = "success" if steps.get("background_removal") != "failed" else "warning"
        result = {
            "status": status,
            "processed_image_base64": data.get("processed_image_base64", ""),
            "reduction_percent": data.get("reduction_percent", 0),
            "original_size_kb": data.get("original_size_kb", 0),
            "processed_size_kb": data.get("processed_size_kb", 0),
            "elapsed_ms": data.get("elapsed_ms", 0),
            "privacy_notice": data.get("privacy_notice", ""),
            "steps": steps,
        }
        if user_tip:
            result["user_tip"] = user_tip

        yield self.create_json_message(result)
        text_msg = (
            f"图片处理完成（{status}）。"
            f"体积减少：{result['reduction_percent']}%，"
            f"耗时：{result['elapsed_ms']}ms。"
        )
        if user_tip:
            text_msg += f"{user_tip} "
        text_msg += "Alt 文本应由 Dify LLM 节点生成。"
        yield self.create_text_message(text_msg)
