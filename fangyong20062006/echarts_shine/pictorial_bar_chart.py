import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class PictorialBarChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "象形柱图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            categories = raw.get("categories", [])
            values = raw.get("values", [])
            symbol = raw.get("symbol", "circle")
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "xAxis": {"data": categories, "axisTick": {"show": False}, "axisLine": {"show": False}},
                "yAxis": {"splitLine": {"show": False}, "axisTick": {"show": False}, "axisLine": {"show": False}, "axisLabel": {"show": False}},
                "series": [{
                    "type": "pictorialBar",
                    "symbol": symbol,
                    "symbolRepeat": True,
                    "symbolSize": ["80%", "90%"],
                    "symbolMargin": "5%",
                    "label": {"show": True, "position": "top", "fontWeight": "bold"},
                    "data": values
                }],
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height))
        except Exception as e:
            raise Exception(f"象形柱图生成失败: {str(e)}")
