import json
from collections import Counter
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


def _get_nested(obj: Any, path: str) -> Any:
    for key in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _to_float(val: Any) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None



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

class SmartSummaryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        raw = tool_parameters.get("json_data", "").strip()
        group_by = tool_parameters.get("group_by_field", "").strip()
        sum_fields_str = tool_parameters.get("sum_fields", "").strip()
        top_n_field = tool_parameters.get("top_n_field", "").strip()
        data_path = tool_parameters.get("data_path", "").strip()

        try:
            parsed = _loads_lenient(raw)
        except Exception as e:
            raise Exception(f"JSON解析失败: {e}")

        if data_path:
            parsed = _get_nested(parsed, data_path)
        if isinstance(parsed, dict):
            parsed = [parsed]
        if not isinstance(parsed, list):
            raise Exception(f"期望数组，实际是 {type(parsed).__name__}，请检查 data_path。")

        records = [r for r in parsed if isinstance(r, dict)]
        total = len(records)
        lines = [f"总记录数: {total} 条\n"]

        if group_by:
            counter = Counter(str(r.get(group_by, "NULL")) for r in records)
            lines.append(f"按 [{group_by}] 分组:")
            for val, cnt in sorted(counter.items(), key=lambda x: -x[1]):
                pct = cnt / total * 100 if total else 0
                lines.append(f"  {val}: {cnt} 条 ({pct:.1f}%)")
            lines.append("")

        sum_fields = [f.strip() for f in sum_fields_str.split(",") if f.strip()]
        if sum_fields:
            lines.append("数值汇总:")
            for field in sum_fields:
                values = [_to_float(r.get(field)) for r in records]
                values = [v for v in values if v is not None]
                if values:
                    total_sum = sum(values)
                    avg = total_sum / len(values)
                    lines.append(f"  {field}: 总计={total_sum:,.2f}, 均值={avg:,.2f}, 有效={len(values)}条")
                else:
                    lines.append(f"  {field}: 无有效数值")
            lines.append("")

        if top_n_field:
            sortable = [(r, _to_float(r.get(top_n_field))) for r in records]
            sortable = [(r, v) for r, v in sortable if v is not None]
            sortable.sort(key=lambda x: -x[1])
            top5 = sortable[:5]
            lines.append(f"Top5（按 {top_n_field} 降序）:")
            for r, v in top5:
                lines.append(f"  {v:,.2f} → {json.dumps(r, ensure_ascii=False)}")
            lines.append("")

        yield self.create_text_message("\n".join(lines))
