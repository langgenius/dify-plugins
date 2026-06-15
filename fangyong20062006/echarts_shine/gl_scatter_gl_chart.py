import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class GlScatterGlChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "GL散点图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            # {"series":[{"name":"A","data":[[x,y],...]},...]}
            series_list = raw.get("series", [])
            x_name = raw.get("x_name", "X")
            y_name = raw.get("y_name", "Y")
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 600))

            series = [{
                "type": "scatterGL", "name": s.get("name", ""),
                "data": s.get("data", []),
                "symbolSize": s.get("symbolSize", 3),
                "itemStyle": {"opacity": 0.7}
            } for s in series_list]

            option = {
                "title": {"text": title, "left": "center"},
                "legend": {"data": [s.get("name","") for s in series_list]},
                "tooltip": {"trigger": "item"},
                "xAxis": {"name": x_name, "type": "value", "scale": True},
                "yAxis": {"name": y_name, "type": "value", "scale": True},
                "series": series,
                "toolbox": {"feature": {"saveAsImage": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height, use_gl=True))
        except Exception as e:
            raise Exception(f"GL散点图生成失败: {str(e)}")
