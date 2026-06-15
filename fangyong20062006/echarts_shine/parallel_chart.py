import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class ParallelChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "平行坐标系")
            raw = json.loads(tool_parameters.get("data", "{}"))
            dimensions = raw.get("dimensions", [])
            data = raw.get("data", [])
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            parallel_axis = [{"dim": i, "name": d} for i, d in enumerate(dimensions)]

            option = {
                "title": {"text": title, "left": "center"},
                "parallelAxis": parallel_axis,
                "parallel": {"left": "5%", "right": "10%", "bottom": "10%", "top": "15%"},
                "tooltip": {"trigger": "item"},
                "series": [{
                    "type": "parallel",
                    "lineStyle": {"width": 1, "opacity": 0.5},
                    "data": data
                }],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height))
        except Exception as e:
            raise Exception(f"平行坐标系生成失败: {str(e)}")
