import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class CandlestickChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "K线图")
            dates = json.loads(tool_parameters.get("dates", "[]"))
            ohlc_data = json.loads(tool_parameters.get("ohlc_data", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "cross"},
                    "formatter": "function(params){var p=params[0];return p.name+'<br/>开盘: '+p.data[0]+'<br/>收盘: '+p.data[1]+'<br/>最低: '+p.data[2]+'<br/>最高: '+p.data[3];}"
                },
                "grid": {"left": "3%", "right": "4%", "bottom": "15%", "containLabel": True},
                "xAxis": {
                    "type": "category",
                    "data": dates,
                    "scale": True,
                    "boundaryGap": False,
                    "axisLine": {"onZero": False},
                    "splitLine": {"show": False},
                    "splitNumber": 20
                },
                "yAxis": {
                    "scale": True,
                    "splitArea": {"show": True}
                },
                "dataZoom": [
                    {"type": "inside", "start": 50, "end": 100},
                    {"show": True, "type": "slider", "bottom": "3%", "start": 50, "end": 100}
                ],
                "series": [{
                    "name": title,
                    "type": "candlestick",
                    "data": ohlc_data,
                    "itemStyle": {
                        "color": "#c12e34",
                        "color0": "#2b821d",
                        "borderColor": "#c12e34",
                        "borderColor0": "#2b821d"
                    }
                }],
                "toolbox": {"feature": {"saveAsImage": {}, "dataView": {}}}
            }

            html = build_html(title, option, width, height)
            yield self.create_text_message(html)

        except Exception as e:
            raise Exception(f"K线图生成失败: {str(e)}")
