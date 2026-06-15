import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html, get_geo_json


class GlMap3dChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "3D地图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            region = raw.get("region", "China")
            map_data = raw.get("data", [])
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 600))

            geo_json = get_geo_json(region)
            values = [d.get("value", 0) for d in map_data]
            max_val = max(values) if values else 100

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {},
                "visualMap": {
                    "max": max_val,
                    "inRange": {"color": ["#e0f0ff","#5ab1ef","#0098d9","#c12e34"]},
                    "calculable": True
                },
                "geo3D": {
                    "map": "geoMap",
                    "roam": True,
                    "shading": "realistic",
                    "label": {"show": True, "textStyle": {"fontSize": 10, "color": "#fff"}},
                    "realisticMaterial": {"roughness": 0.8, "metalness": 0},
                    "postEffect": {"enable": True},
                    "groundPlane": {"show": False},
                    "viewControl": {"distance": 80}
                },
                "series": [{
                    "type": "map3D",
                    "map": "geoMap",
                    "data": map_data,
                    "shading": "lambert",
                    "label": {"show": True, "textStyle": {"fontSize": 10}},
                    "itemStyle": {"opacity": 1, "borderWidth": 0.8, "borderColor": "rgba(255,255,255,0.5)"},
                    "emphasis": {"label": {"show": True}, "itemStyle": {"color": "#e6b600"}}
                }]
            }
            yield self.create_text_message(build_html(title, option, width, height, use_gl=True, geo_json=geo_json))
        except Exception as e:
            raise Exception(f"3D地图生成失败: {str(e)}")
