import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class SunburstChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "旭日图")
            data = json.loads(tool_parameters.get("data", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "sunburst",
                    "data": data,
                    "radius": ["15%", "80%"],
                    "center": ["50%", "55%"],
                    "sort": "asc",
                    "emphasis": {"focus": "ancestor"},
                    "levels": [
                        {},
                        {"r0": "15%", "r": "35%", "itemStyle": {"borderWidth": 2}, "label": {"rotate": "tangential"}},
                        {"r0": "35%", "r": "60%", "label": {"align": "right"}},
                        {"r0": "60%", "r": "62%", "label": {"position": "outside", "padding": 3, "silent": False}, "itemStyle": {"borderWidth": 3}}
                    ]
                }],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height))
        except Exception as e:
            raise Exception(f"旭日图生成失败: {str(e)}")
