import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class BarChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "柱状图")
            categories = json.loads(tool_parameters.get("categories", "[]"))
            series_data = json.loads(tool_parameters.get("series_data", "[]"))
            direction = tool_parameters.get("direction", "vertical")
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            is_horizontal = direction == "horizontal"

            series = []
            for s in series_data:
                series.append({
                    "name": s.get("name", ""),
                    "type": "bar",
                    "data": s.get("data", []),
                    "label": {"show": True, "position": "top" if not is_horizontal else "right"}
                })

            if is_horizontal:
                x_axis = {"type": "value"}
                y_axis = {"type": "category", "data": categories}
            else:
                x_axis = {"type": "category", "data": categories}
                y_axis = {"type": "value"}

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"top": "8%"},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                "xAxis": x_axis,
                "yAxis": y_axis,
                "series": series,
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}, "restore": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"柱状图生成失败: {str(e)}")
