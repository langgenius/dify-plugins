import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class ThemeRiverChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "主题河流图")
            data = json.loads(tool_parameters.get("data", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            themes = list(dict.fromkeys(row[2] for row in data if len(row) >= 3))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "line", "lineStyle": {"color": "rgba(0,0,0,0.2)", "width": 1}}},
                "legend": {"data": themes, "top": "8%"},
                "singleAxis": {"top": "20%", "bottom": "5%", "axisTick": {}, "axisLabel": {}, "type": "time", "axisPointer": {"animation": True, "label": {"show": True}}},
                "series": [{
                    "type": "themeRiver",
                    "emphasis": {"itemStyle": {"shadowBlur": 20, "shadowColor": "rgba(0,0,0,0.8)"}},
                    "data": data
                }],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height))
        except Exception as e:
            raise Exception(f"主题河流图生成失败: {str(e)}")
