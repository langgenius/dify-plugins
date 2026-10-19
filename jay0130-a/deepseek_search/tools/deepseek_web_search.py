from __future__ import annotations

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ._client import DeepSeekToolsClient, MAX_COUNT, MAX_QUERY_CHARS
from ._errors import friendly_error_message


class DeepSeekWebSearchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials.get("deepseek_api_key")
        if not api_key:
            yield self.create_text_message(
                "DeepSeek API Key is not configured. Set it in the plugin credentials."
            )
            return

        query = (tool_parameters.get("query") or "").strip()
        if not query:
            yield self.create_text_message("Query is required.")
            return
        if len(query) > MAX_QUERY_CHARS:
            yield self.create_text_message(
                f"Query must be at most {MAX_QUERY_CHARS} characters (got {len(query)})."
            )
            return

        ori_question = _clean_optional(tool_parameters.get("ori_question"))
        if ori_question and len(ori_question) > MAX_QUERY_CHARS:
            ori_question = ori_question[:MAX_QUERY_CHARS]
        count = _coerce_count(tool_parameters.get("count"))
        need_content = bool(tool_parameters.get("need_content") or False)

        try:
            with DeepSeekToolsClient(api_key=str(api_key)) as client:
                payload = client.search(
                    query=query,
                    count=count,
                    ori_question=ori_question,
                    need_content=need_content,
                )
        except Exception as exc:
            yield self.create_text_message(friendly_error_message(exc))
            return

        results = payload.get("results") or []
        normalized = [_normalize_result(r, need_content) for r in results]
        output = {
            "query": query,
            "count": len(normalized),
            "results": normalized,
        }
        yield self.create_json_message(output)
        yield self.create_text_message(_format_results(output))


def _clean_optional(raw: Any) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _coerce_count(raw: Any) -> int | None:
    if raw is None or raw == "":
        return None
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return None
    return max(1, min(MAX_COUNT, n))


def _normalize_result(raw: Any, include_content: bool) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {"title": str(raw)}
    result = {
        "title": raw.get("title") or "",
        "url": raw.get("url") or "",
        "snippet": raw.get("snippet") or "",
        "summary": raw.get("summary") or "",
        "site_name": raw.get("site_name") or "",
        "date": raw.get("date") or "",
        "rerank_score": raw.get("rerank_score"),
        "authority": raw.get("authority"),
    }
    if include_content:
        result["content"] = raw.get("content") or ""
    return result


def _format_results(payload: dict[str, Any]) -> str:
    results = payload.get("results") or []
    if not results:
        return f"No DeepSeek results for '{payload.get('query', '')}'."
    lines: list[str] = [f"# DeepSeek web search: {payload.get('query', '')}\n"]
    for idx, r in enumerate(results, 1):
        title = r.get("title") or "(no title)"
        url = r.get("url") or ""
        lines.append(f"{idx}. [{title}]({url})")
        meta: list[str] = []
        if r.get("site_name"):
            meta.append(str(r["site_name"]))
        if r.get("date"):
            meta.append(str(r["date"]))
        score = r.get("rerank_score")
        if isinstance(score, (int, float)):
            meta.append(f"relevance {score:g}")
        if meta:
            lines.append(f"   ({' · '.join(meta)})")
        summary = r.get("summary") or r.get("snippet") or ""
        if summary:
            lines.append(f"   {summary}")
    return "\n".join(lines)
