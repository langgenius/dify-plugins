import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class TreemapChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "矩形树图")
            data = json.loads(tool_parameters.get("data", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {
                    "formatter": "function(info){var v=info.value;var t=info.treePathInfo;var tp=[];for(var i=1;i<t.length;i++){tp.push(t[i].name);}return '<div>'+tp.join('/')+'</div><div>'+echarts.format.addCommas(v)+'</div>';}"
                },
                "series": [{
                    "name": title,
                    "type": "treemap",
                    "visibleMin": 300,
                    "label": {"show": True, "formatter": "{b}"},
                    "upperLabel": {"show": True, "height": 30},
                    "itemStyle": {"borderColor": "#fff"},
                    "levels": [
                        {
                            "itemStyle": {"borderWidth": 0, "gapWidth": 5},
                            "upperLabel": {"show": False}
                        },
                        {
                            "itemStyle": {"gapWidth": 1},
                            "colorSaturation": [0.35, 0.5]
                        },
                        {
                            "colorSaturation": [0.35, 0.5],
                            "itemStyle": {"gapWidth": 1, "borderColorSaturation": 0.6}
                        }
                    ],
                    "data": data
                }],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"矩形树图生成失败: {str(e)}")
