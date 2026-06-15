import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class GaugeChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "仪表盘")
            data = json.loads(tool_parameters.get("data", '[{"name":"指标","value":75}]'))
            min_value = float(tool_parameters.get("min_value", 0))
            max_value = float(tool_parameters.get("max_value", 100))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"formatter": "{a} <br/>{b}: {c}"},
                "series": [{
                    "name": title,
                    "type": "gauge",
                    "min": min_value,
                    "max": max_value,
                    "radius": "75%",
                    "center": ["50%", "58%"],
                    "progress": {"show": True, "width": 18},
                    "axisLine": {"lineStyle": {"width": 18}},
                    "axisTick": {"show": False},
                    "splitLine": {"length": 15, "lineStyle": {"width": 2, "color": "#999"}},
                    "axisLabel": {"distance": 25, "color": "#999", "fontSize": 12},
                    "anchor": {"show": True, "showAbove": True, "size": 20, "itemStyle": {"borderWidth": 10}},
                    "title": {"show": True},
                    "detail": {
                        "valueAnimation": True,
                        "fontSize": 30,
                        "fontWeight": "bold",
                        "color": "inherit"
                    },
                    "data": data
                }],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"仪表盘生成失败: {str(e)}")
