import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class RadarChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "雷达图")
            indicators = json.loads(tool_parameters.get("indicators", "[]"))
            series_data = json.loads(tool_parameters.get("series_data", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            series_items = [{"value": s.get("value", []), "name": s.get("name", "")} for s in series_data]

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "item"},
                "legend": {"top": "8%", "data": [s.get("name", "") for s in series_data]},
                "radar": {
                    "indicator": indicators,
                    "center": ["50%", "57%"],
                    "radius": "65%"
                },
                "series": [{
                    "name": title,
                    "type": "radar",
                    "data": series_items,
                    "areaStyle": {"opacity": 0.2}
                }],
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"雷达图生成失败: {str(e)}")
