import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class FunnelChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "漏斗图")
            data = json.loads(tool_parameters.get("data", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b}: {c} ({d}%)"},
                "legend": {
                    "orient": "horizontal",
                    "top": "8%",
                    "data": [d["name"] for d in data]
                },
                "series": [{
                    "name": title,
                    "type": "funnel",
                    "left": "10%",
                    "top": "20%",
                    "bottom": "5%",
                    "width": "80%",
                    "min": 0,
                    "max": 100,
                    "minSize": "0%",
                    "maxSize": "100%",
                    "sort": "descending",
                    "gap": 2,
                    "label": {"show": True, "position": "inside", "formatter": "{b}\n{c}"},
                    "labelLine": {"length": 10, "lineStyle": {"width": 1, "type": "solid"}},
                    "itemStyle": {"borderColor": "#fff", "borderWidth": 1},
                    "emphasis": {"label": {"fontSize": 14}},
                    "data": data
                }],
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"漏斗图生成失败: {str(e)}")
