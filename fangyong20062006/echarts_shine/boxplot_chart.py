import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class BoxplotChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "盒须图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            categories = raw.get("categories", [])
            data = raw.get("data", [])
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "item", "axisPointer": {"type": "shadow"},
                            "formatter": "function(p){var v=p.data;return p.name+'<br/>最大值: '+v[4]+'<br/>Q3: '+v[3]+'<br/>中位数: '+v[2]+'<br/>Q1: '+v[1]+'<br/>最小值: '+v[0];}"},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                "xAxis": {"type": "category", "data": categories, "boundaryGap": True,
                          "nameGap": 30, "splitArea": {"show": False}, "splitLine": {"show": False}},
                "yAxis": {"type": "value", "splitArea": {"show": True}},
                "series": [{
                    "name": title, "type": "boxplot", "data": data,
                    "tooltip": {"formatter": "function(p){var v=p.data;return p.name+'<br/>最大值: '+v[4]+'<br/>Q3: '+v[3]+'<br/>中位数: '+v[2]+'<br/>Q1: '+v[1]+'<br/>最小值: '+v[0];}"}
                }],
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height))
        except Exception as e:
            raise Exception(f"盒须图生成失败: {str(e)}")
