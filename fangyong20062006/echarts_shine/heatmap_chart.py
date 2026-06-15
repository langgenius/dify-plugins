import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class HeatmapChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "热力图")
            x_categories = json.loads(tool_parameters.get("x_categories", "[]"))
            y_categories = json.loads(tool_parameters.get("y_categories", "[]"))
            data = json.loads(tool_parameters.get("data", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            values = [item[2] for item in data if len(item) >= 3]
            min_val = min(values) if values else 0
            max_val = max(values) if values else 10

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"position": "top"},
                "grid": {"left": "3%", "right": "10%", "bottom": "15%", "containLabel": True},
                "xAxis": {"type": "category", "data": x_categories, "splitArea": {"show": True}},
                "yAxis": {"type": "category", "data": y_categories, "splitArea": {"show": True}},
                "visualMap": {
                    "min": min_val,
                    "max": max_val,
                    "calculable": True,
                    "orient": "horizontal",
                    "left": "center",
                    "bottom": "2%",
                    "inRange": {"color": ["#e0f0ff", "#5ab1ef", "#0098d9", "#005eaa"]}
                },
                "series": [{
                    "name": title,
                    "type": "heatmap",
                    "data": data,
                    "label": {"show": True},
                    "emphasis": {
                        "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.5)"}
                    }
                }],
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"热力图生成失败: {str(e)}")
