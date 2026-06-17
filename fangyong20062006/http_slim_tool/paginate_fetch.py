import json
import ssl
import certifi
import urllib.request
import urllib.parse
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


def _get_nested(obj: Any, path: str) -> Any:
    for key in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
        if obj is None:
            return None
    return obj


def _http_get(url: str, params: dict) -> Any:
    full_url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(full_url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; DifyPlugin/1.0; +http_slim_tool)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


class PaginateFetchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        base_url = tool_parameters.get("base_url", "").strip()
        mode = tool_parameters.get("pagination_mode", "page")
        page_size = int(tool_parameters.get("page_size") or 20)
        max_pages = min(int(tool_parameters.get("max_pages") or 5), 20)
        data_path = tool_parameters.get("data_path", "").strip()
        cursor_path = tool_parameters.get("next_cursor_path", "").strip()
        keep_fields_str = tool_parameters.get("keep_fields", "").strip()

        extra_params = {}
        extra_raw = (tool_parameters.get("extra_params") or "").strip()
        if extra_raw:
            try:
                extra_params = json.loads(extra_raw)
            except Exception:
                raise Exception(f"extra_params 不是合法JSON: {extra_raw}")

        fields = [f.strip() for f in keep_fields_str.split(",") if f.strip()]
        all_records = []
        cursor = None
        fetched_pages = 0
        stop_reason = "达到最大页数"

        for page_idx in range(max_pages):
            params = dict(extra_params)
            if mode == "offset":
                params["offset"] = page_idx * page_size
                params["limit"] = page_size
            elif mode == "page":
                params["page"] = page_idx + 1
                params["pageSize"] = page_size
            elif mode == "cursor":
                params["pageSize"] = page_size
                if cursor:
                    params["cursor"] = cursor

            try:
                resp = _http_get(base_url, params)
            except Exception as e:
                raise Exception(f"第 {page_idx + 1} 页请求失败: {e}")

            records = _get_nested(resp, data_path) if data_path else resp

            if not isinstance(records, list):
                raise Exception(
                    f"第 {page_idx + 1} 页：期望数组，实际是 {type(records).__name__}。"
                    f"请检查 data_path 参数（当前: '{data_path}'）。"
                )

            fetched_pages += 1

            if fields:
                records = [{k: r[k] for k in fields if k in r} for r in records if isinstance(r, dict)]

            all_records.extend(records)

            if len(records) < page_size:
                stop_reason = "数据已取完"
                break

            if mode == "cursor":
                if not cursor_path:
                    stop_reason = "游标路径未配置，停止"
                    break
                next_cursor = _get_nested(resp, cursor_path)
                if not next_cursor:
                    stop_reason = "无下一页游标"
                    break
                cursor = next_cursor

        summary = (
            f"分页拉取完成\n"
            f"模式: {mode} | 每页: {page_size} 条 | 共拉取: {fetched_pages} 页\n"
            f"合并记录数: {len(all_records)} 条 | 停止原因: {stop_reason}\n"
        )
        if fields:
            summary += f"保留字段: {', '.join(fields)}\n"

        result = summary + "\n" + json.dumps(all_records, ensure_ascii=False, indent=2)
        yield self.create_text_message(result)
