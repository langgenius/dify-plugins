import json
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



def _loads_lenient(raw: str):
    """
    容错解析 JSON：先按严格 JSON 解析；失败则从首个 [ 或 { 截取到对应的末尾
    } / ] 再解析。用于兼容上游（如分页拉取）在 JSON 前面拼接了说明性摘要文字的情况。
    """
    import json as _json
    s = (raw or "").strip()
    try:
        return _json.loads(s)
    except Exception:
        pass
    # 定位第一个 [ 或 {
    starts = [i for i in (s.find("["), s.find("{")) if i != -1]
    if not starts:
        raise ValueError("输入中未找到 JSON 数组或对象。请确认输入包含合法 JSON。")
    start = min(starts)
    open_ch = s[start]
    close_ch = "]" if open_ch == "[" else "}"
    end = s.rfind(close_ch)
    if end == -1 or end < start:
        raise ValueError("输入中的 JSON 结构不完整。")
    snippet = s[start:end + 1]
    return _json.loads(snippet)

class SlimFieldsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        raw = tool_parameters.get("json_data", "").strip()
        keep_fields_str = tool_parameters.get("keep_fields", "").strip()
        max_records = int(tool_parameters.get("max_records") or 50)
        max_records = min(max_records, 200)
        data_path = tool_parameters.get("data_path", "").strip()

        try:
            parsed = _loads_lenient(raw)
        except Exception as e:
            raise Exception(f"JSON解析失败: {e}。请确认输入包含合法JSON（数组或对象）。")

        if data_path:
            parsed = _get_nested(parsed, data_path)
            if parsed is None:
                raise Exception(f"路径 '{data_path}' 不存在，请检查 data_path 参数。")

        if isinstance(parsed, dict):
            parsed = [parsed]

        if not isinstance(parsed, list):
            raise Exception(f"目标数据不是数组，而是 {type(parsed).__name__}。请用 data_path 指定数组所在路径。")

        total = len(parsed)
        records = parsed[:max_records]

        fields = [f.strip() for f in keep_fields_str.split(",") if f.strip()]
        if fields:
            slimmed = []
            for rec in records:
                if isinstance(rec, dict):
                    slimmed.append({k: rec[k] for k in fields if k in rec})
                else:
                    slimmed.append(rec)
        else:
            slimmed = records

        summary_lines = [
            f"共 {total} 条记录，返回前 {len(slimmed)} 条",
            f"保留字段：{', '.join(fields) if fields else '全部'}",
            "",
        ]
        result_str = "\n".join(summary_lines) + json.dumps(slimmed, ensure_ascii=False, indent=2)
        yield self.create_text_message(result_str)
