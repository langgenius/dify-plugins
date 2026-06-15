import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class TreeChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "树图")
            tree_data = json.loads(tool_parameters.get("tree_data", '{"name":"Root"}'))
            layout = tool_parameters.get("layout", "orthogonal")
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            series_config = {
                "type": "tree",
                "data": [tree_data],
                "top": "5%",
                "left": "10%",
                "bottom": "5%",
                "right": "20%",
                "symbolSize": 10,
                "label": {
                    "position": "left",
                    "verticalAlign": "middle",
                    "align": "right",
                    "fontSize": 12
                },
                "leaves": {
                    "label": {
                        "position": "right",
                        "verticalAlign": "middle",
                        "align": "left"
                    }
                },
                "emphasis": {"focus": "descendant"},
                "expandAndCollapse": True,
                "animationDuration": 550,
                "animationDurationUpdate": 750
            }

            if layout == "radial":
                series_config["layout"] = "radial"
                series_config["top"] = "10%"
                series_config["left"] = "10%"
                series_config["bottom"] = "10%"
                series_config["right"] = "10%"
                series_config["label"]["position"] = "top"
                series_config["label"]["align"] = "center"
                series_config["leaves"]["label"]["position"] = "bottom"
                series_config["leaves"]["label"]["align"] = "center"

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
                "series": [series_config],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"树图生成失败: {str(e)}")
