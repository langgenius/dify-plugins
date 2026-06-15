import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html, get_geo_json


class MapChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "地图")
            region = tool_parameters.get("region", "China") or "China"
            data = json.loads(tool_parameters.get("data", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            geo_json = get_geo_json(region)
            values = [item["value"] for item in data if "value" in item]
            min_val = min(values) if values else 0
            max_val = max(values) if values else 100

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
                "visualMap": {
                    "min": min_val, "max": max_val,
                    "left": "left", "top": "bottom",
                    "text": ["高", "低"],
                    "calculable": True,
                    "inRange": {"color": ["#e0f0ff", "#5ab1ef", "#0098d9", "#005eaa"]}
                },
                "series": [{
                    "name": title, "type": "map", "map": "geoMap",
                    "roam": True,
                    "label": {"show": True, "fontSize": 10},
                    "emphasis": {"label": {"show": True}},
                    "data": data
                }],
                "toolbox": {"feature": {"saveAsImage": {}, "restore": {}}}
            }

            html = build_html(title, option, width, height, geo_json=geo_json)
            yield self.create_text_message(html)
        except Exception as e:
            raise Exception(f"地图生成失败: {str(e)}")
