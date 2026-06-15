import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class GlGraphGlChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "GL关系图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            nodes = raw.get("nodes", [])
            links = raw.get("links", [])
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 600))

            for n in nodes:
                if "symbolSize" not in n:
                    n["symbolSize"] = max(5, n.get("value", 5))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {},
                "series": [{
                    "type": "graphGL",
                    "nodes": nodes,
                    "edges": links,
                    "modularity": {"resolution": 2, "sort": True},
                    "lineStyle": {"color": "rgba(0,0,0,0.1)", "width": 1},
                    "itemStyle": {"opacity": 0.9},
                    "label": {"show": True, "position": "right", "formatter": "{b}"},
                    "emphasis": {"focus": "adjacency"}
                }]
            }
            yield self.create_text_message(build_html(title, option, width, height, use_gl=True))
        except Exception as e:
            raise Exception(f"GL关系图生成失败: {str(e)}")
