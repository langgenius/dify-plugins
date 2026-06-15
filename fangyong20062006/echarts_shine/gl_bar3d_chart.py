import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class GlBar3dChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "3D柱状图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            # data format: {"x":["A","B","C"],"y":["X","Y"],"values":[[x_idx,y_idx,value],...]}
            x_data = raw.get("x", [])
            y_data = raw.get("y", [])
            values = raw.get("values", [])
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 600))

            max_val = max(v[2] for v in values) if values else 10

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {},
                "visualMap": {
                    "max": max_val, "inRange": {"color": ["#e0f0ff","#5ab1ef","#0098d9","#c12e34"]},
                    "calculable": True
                },
                "xAxis3D": {"type": "category", "data": x_data},
                "yAxis3D": {"type": "category", "data": y_data},
                "zAxis3D": {"type": "value"},
                "grid3D": {
                    "boxWidth": 200, "boxDepth": 80,
                    "viewControl": {"projection": "orthographic"},
                    "light": {"main": {"intensity": 1.2}, "ambient": {"intensity": 0.3}}
                },
                "series": [{
                    "type": "bar3D",
                    "data": values,
                    "shading": "lambert",
                    "label": {"show": False},
                    "emphasis": {"label": {"show": True, "textStyle": {"fontSize": 12, "fontWeight": "bold"}},
                                 "itemStyle": {"color": "#e6b600"}}
                }]
            }
            yield self.create_text_message(build_html(title, option, width, height, use_gl=True))
        except Exception as e:
            raise Exception(f"3D柱状图生成失败: {str(e)}")
