import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class ChordChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "和弦图")
            nodes = json.loads(tool_parameters.get("nodes", "[]"))
            links = json.loads(tool_parameters.get("links", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            for n in nodes:
                n["symbolSize"] = max(15, n.get("value", 10) * 2)
                n["label"] = {"show": True}

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {},
                "animationDurationUpdate": 1500,
                "animationEasingUpdate": "quinticInOut",
                "series": [{
                    "type": "graph",
                    "layout": "circular",
                    "circular": {"rotateLabel": True},
                    "data": nodes,
                    "links": links,
                    "roam": True,
                    "label": {"position": "right", "formatter": "{b}"},
                    "lineStyle": {"color": "source", "curveness": 0.3, "opacity": 0.7},
                    "emphasis": {"focus": "adjacency", "lineStyle": {"width": 4}}
                }],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height))
        except Exception as e:
            raise Exception(f"和弦图生成失败: {str(e)}")
