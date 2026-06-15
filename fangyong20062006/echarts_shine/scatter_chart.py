import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class ScatterChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "散点图")
            series_data = json.loads(tool_parameters.get("series_data", "[]"))
            x_name = tool_parameters.get("x_name", "")
            y_name = tool_parameters.get("y_name", "")
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            series = []
            for s in series_data:
                series.append({
                    "name": s.get("name", ""),
                    "type": "scatter",
                    "data": s.get("data", []),
                    "symbolSize": s.get("symbolSize", 10),
                })

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{a}: ({c})"},
                "legend": {"top": "8%"},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                "xAxis": {"type": "value", "name": x_name, "scale": True},
                "yAxis": {"type": "value", "name": y_name, "scale": True},
                "series": series,
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"散点图生成失败: {str(e)}")
