import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html, get_geo_json


class LinesChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "路径图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            coords = raw.get("coords", [])
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            geo_json = get_geo_json("China")

            lines_data = []
            effect_data = []
            for pair in coords:
                if len(pair) >= 2:
                    lines_data.append({"coords": [pair[0]["coord"], pair[1]["coord"]]})
                    effect_data.append({"name": pair[0].get("name", ""), "value": pair[0]["coord"] + [1]})
                    effect_data.append({"name": pair[1].get("name", ""), "value": pair[1]["coord"] + [1]})

            option = {
                "title": {"text": title, "left": "center", "textStyle": {"color": "#333"}},
                "tooltip": {"trigger": "item"},
                "geo": {
                    "map": "geoMap", "roam": True,
                    "label": {"show": False},
                    "itemStyle": {"areaColor": "#e0f0ff", "borderColor": "#008acd"},
                    "emphasis": {"itemStyle": {"areaColor": "#5ab1ef"}}
                },
                "series": [
                    {
                        "type": "lines", "coordinateSystem": "geo",
                        "data": lines_data,
                        "lineStyle": {"color": "#c12e34", "width": 1, "opacity": 0.6, "curveness": 0.2},
                        "effect": {"show": True, "period": 4, "trailLength": 0.4,
                                   "symbol": "arrow", "symbolSize": 6}
                    },
                    {
                        "type": "effectScatter", "coordinateSystem": "geo",
                        "data": effect_data,
                        "symbolSize": 6,
                        "itemStyle": {"color": "#e6b600"}
                    }
                ],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height, geo_json=geo_json))
        except Exception as e:
            raise Exception(f"路径图生成失败: {str(e)}")
