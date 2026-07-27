from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from _config import (
    API_BASE,
    MAX_BATCH,
    DEFAULT_TIMEOUT,
    MAX_WORKERS,
    safe_api_call,
    validate_image_input,
    validate_url_input,
)


def _process_single_image(
    input_data: dict[str, str],
    payload_common: dict[str, Any],
    api_key: str,
) -> dict[str, Any]:
    """Process a single image (URL or base64)."""
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    payload = {**payload_common, **input_data, "return_image": True}

    resp = safe_api_call(
        None,
        "POST",
        f"{API_BASE}/api/v1/process/json",
        json=payload,
        headers=headers,
        timeout=DEFAULT_TIMEOUT,
    )
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
    }
    if user_tip:
        result["user_tip"] = user_tip
    return result


class BatchProcessImagesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials["pixseo_api_key"]

        # Collect image inputs from URLs (comma-separated) and/or base64 (JSON array)
        url_raw = tool_parameters.get("image_urls", "")
        b64_raw = tool_parameters.get("image_base64s", "")

        urls = [u.strip() for u in url_raw.split(",") if u.strip()]
        base64s = []
        if b64_raw:
            b64_raw = b64_raw.strip()
            # 支持 JSON 数组格式，避免 Data URI 中的逗号导致错误拆分
            if b64_raw.startswith("["):
                try:
                    base64s = json.loads(b64_raw)
                    if not isinstance(base64s, list):
                        raise ValueError("image_base64s must be a JSON array")
                except json.JSONDecodeError:
                    raise ValueError("image_base64s must be a valid JSON array")
            else:
                # 兼容旧格式：换行符分隔
                base64s = [b.strip() for b in b64_raw.split("\n") if b.strip()]

        # Validate inputs
        for url in urls:
            err = validate_url_input(url)
            if err:
                yield self.create_text_message(f"Error: {err}")
                return

        for b64 in base64s:
            err = validate_image_input(b64)
            if err:
                yield self.create_text_message(f"Error: {err}")
                return

        # Build input list: (index, input_type, input_data)
        inputs = []
        for i, url in enumerate(urls):
            inputs.append((i, "url", url))
        offset = len(urls)
        for i, b64 in enumerate(base64s):
            inputs.append((offset + i, "base64", b64))

        inputs = inputs[:MAX_BATCH]

        if not inputs:
            yield self.create_text_message(
                "Error: provide at least one image via image_urls or image_base64s"
            )
            return

        payload_common = {
            "remove_bg": tool_parameters.get("remove_bg", True),
            "compress": tool_parameters.get("compress", True),
            "privacy_accepted": tool_parameters.get("privacy_accepted", False),
        }
        results = [None] * len(inputs)
        success_count = 0

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_map = {}
            for idx, input_type, data in inputs:
                if input_type == "url":
                    future = executor.submit(
                        _process_single_image,
                        {"file_url": data},
                        payload_common,
                        api_key,
                    )
                else:
                    future = executor.submit(
                        _process_single_image,
                        {"image_base64": data},
                        payload_common,
                        api_key,
                    )
                future_map[future] = idx

            for future in as_completed(future_map):
                idx = future_map[future]
                url_count = len(urls)
                source = (
                    urls[idx]
                    if idx < url_count
                    else f"base64_input_{idx - url_count + 1}"
                )
                try:
                    result_entry = future.result()
                    result_entry["index"] = idx + 1
                    result_entry["url"] = source
                    results[idx] = result_entry
                    if result_entry.get("status") == "success":
                        success_count += 1
                except Exception as e:
                    results[idx] = {
                        "index": idx + 1,
                        "url": source,
                        "status": "failed",
                        "error": str(e),
                    }

        yield self.create_json_message(
            {"total": len(inputs), "success": success_count, "results": results}
        )
        yield self.create_text_message(
            f"Batch complete: {success_count}/{len(inputs)} images processed successfully. "
            "Alt text should be generated by Dify LLM node."
        )
