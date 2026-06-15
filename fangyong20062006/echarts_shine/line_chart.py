import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class LineChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "折线图")
            categories = json.loads(tool_parameters.get("categories", "[]"))
            series_data = json.loads(tool_parameters.get("series_data", "[]"))
            smooth = tool_parameters.get("smooth", "false") == "true"
            area = tool_parameters.get("area", "false") == "true"
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            series = []
            for s in series_data:
                item = {
                    "name": s.get("name", ""),
                    "type": "line",
                    "data": s.get("data", []),
                    "smooth": smooth,
                    "symbol": "circle",
                    "symbolSize": 6,
                }
                if area:
                    item["areaStyle"] = {"opacity": 0.3}
                series.append(item)

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "axis"},
                "legend": {"top": "8%"},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                "xAxis": {"type": "category", "boundaryGap": False, "data": categories},
                "yAxis": {"type": "value"},
                "series": series,
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}, "restore": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"折线图生成失败: {str(e)}")
