import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class CalendarChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "日历热力图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            year = raw.get("year", 2024)
            data = raw.get("data", [])
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            values = [item[1] for item in data if len(item) >= 2]
            min_val = min(values) if values else 0
            max_val = max(values) if values else 10

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"formatter": "function(p){return p.data[0]+': '+p.data[1];}"},
                "visualMap": {
                    "min": min_val, "max": max_val,
                    "calculable": True, "orient": "horizontal",
                    "left": "center", "bottom": "3%",
                    "inRange": {"color": ["#e0f0ff", "#5ab1ef", "#0098d9", "#005eaa"]}
                },
                "calendar": {
                    "top": "15%", "left": "5%", "right": "5%",
                    "cellSize": ["auto", 16],
                    "range": str(year),
                    "itemStyle": {"borderWidth": 0.5},
                    "yearLabel": {"show": True}
                },
                "series": [{
                    "type": "heatmap",
                    "coordinateSystem": "calendar",
                    "data": data
                }],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height))
        except Exception as e:
            raise Exception(f"日历图生成失败: {str(e)}")
