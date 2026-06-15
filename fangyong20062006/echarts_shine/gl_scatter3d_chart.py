import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class GlScatter3dChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "3D散点图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            # data: {"series":[{"name":"A","data":[[x,y,z],...]},...]}
            series_list = raw.get("series", [])
            x_name = raw.get("x_name", "X")
            y_name = raw.get("y_name", "Y")
            z_name = raw.get("z_name", "Z")
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 600))

            series = [{
                "type": "scatter3D", "name": s.get("name", ""),
                "data": s.get("data", []),
                "symbolSize": s.get("symbolSize", 6),
                "emphasis": {"itemStyle": {"color": "#e6b600"}}
            } for s in series_list]

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {},
                "legend": {"data": [s["name"] for s in series_list]},
                "xAxis3D": {"name": x_name, "type": "value"},
                "yAxis3D": {"name": y_name, "type": "value"},
                "zAxis3D": {"name": z_name, "type": "value"},
                "grid3D": {
                    "viewControl": {"autoRotate": False},
                    "light": {"main": {"intensity": 1.2}, "ambient": {"intensity": 0.3}}
                },
                "series": series
            }
            yield self.create_text_message(build_html(title, option, width, height, use_gl=True))
        except Exception as e:
            raise Exception(f"3D散点图生成失败: {str(e)}")
