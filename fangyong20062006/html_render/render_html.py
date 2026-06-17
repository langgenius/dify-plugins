from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# 检测 HTML 是否为完整文档的标记
_COMPLETE_MARKERS = ("<!doctype", "<html")


def _is_complete_html(content: str) -> bool:
    """判断是否已经是完整的 HTML 文档（含 DOCTYPE 或 <html> 标签）。"""
    stripped = content.strip().lower()
    return any(stripped.startswith(m) for m in _COMPLETE_MARKERS)


def _wrap_fragment(fragment: str, title: str) -> str:
    """将裸 HTML 片段包装为完整页面。"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #ffffff; font-family: 'Microsoft YaHei', Arial, sans-serif; }}
</style>
</head>
<body>
{fragment}
</body>
</html>"""


def _inject_title(html: str, title: str) -> str:
    """若完整文档缺少 <title>，注入一个。"""
    if "<title>" in html.lower():
        return html
    return html.replace(
        "<head>",
        f"<head>\n<title>{title}</title>",
        1,
    )


class RenderHtmlTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        html_content: str = tool_parameters.get("html_content", "").strip()
        title: str = tool_parameters.get("title", "图表预览") or "图表预览"

        if not html_content:
            raise Exception("html_content 不能为空")

        try:
            if _is_complete_html(html_content):
                final_html = _inject_title(html_content, title)
            else:
                final_html = _wrap_fragment(html_content, title)

            # --- 输出策略 ---
            # ECharts 内联 HTML 通常含完整 JS 库，体积约 900KB+。
            # Dify 工具节点 text 字段有长度上限，超限后 text 被清空（输出 {}）。
            # 解决方案：同时输出两种格式——
            #   1. blob：完整 HTML 文件，Dify 返回可访问的文件 URL，
            #      前端可用 <iframe src="..."> 或直接打开链接查看图表。
            #   2. text：文件大小说明 + 提示，供 End 节点 text 变量使用。
            #
            # workflow End 节点：
            #   - 引用 files 变量 → 得到 HTML 文件下载链接
            #   - 引用 text 变量  → 得到提示文字

            html_bytes = final_html.encode("utf-8")
            file_size_kb = len(html_bytes) // 1024

            # 输出1：blob 文件（主要输出，解决超限问题）
            yield self.create_blob_message(
                blob=html_bytes,
                meta={
                    "mime_type": "text/html",
                    "filename": f"{title}.html",
                },
            )

            # 输出2：text 说明（轻量，不超限）
            yield self.create_text_message(
                f"HTML 文件已生成：{title}.html（{file_size_kb} KB）\n"
                f"请点击上方文件链接在浏览器中打开以查看图表。"
            )

        except Exception as e:
            raise Exception(f"HTML 渲染失败: {str(e)}")
