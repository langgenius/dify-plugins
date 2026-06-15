import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class PieChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "饼图")
            data = json.loads(tool_parameters.get("data", "[]"))
            donut = tool_parameters.get("donut", "false") == "true"
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            radius = ["40%", "70%"] if donut else "60%"

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b}: {c} ({d}%)"},
                "legend": {"orient": "vertical", "left": "left"},
                "series": [{
                    "name": title,
                    "type": "pie",
                    "radius": radius,
                    "center": ["50%", "55%"],
                    "data": data,
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0,0,0,0.5)"
                        }
                    },
                    "label": {"formatter": "{b}: {d}%"}
                }],
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"饼图生成失败: {str(e)}")
