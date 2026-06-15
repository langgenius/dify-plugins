import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class SankeyChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "桑基图")
            nodes = json.loads(tool_parameters.get("nodes", "[]"))
            links = json.loads(tool_parameters.get("links", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {
                    "trigger": "item",
                    "triggerOn": "mousemove"
                },
                "series": [{
                    "type": "sankey",
                    "layout": "none",
                    "emphasis": {"focus": "adjacency"},
                    "data": nodes,
                    "links": links,
                    "lineStyle": {"color": "gradient", "opacity": 0.4},
                    "label": {"color": "#333"}
                }],
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"桑基图生成失败: {str(e)}")
