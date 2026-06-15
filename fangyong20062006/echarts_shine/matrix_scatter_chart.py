import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class MatrixScatterChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "矩阵坐标系")
            dimensions = json.loads(tool_parameters.get("dimensions", "[]"))
            data = json.loads(tool_parameters.get("data", "[]"))
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 700))

            n = len(dimensions)
            if n < 2:
                raise ValueError("至少需要 2 个维度")

            cell = min(int((min(width, height) - 60) / n), 180)
            grid_size = cell - 10

            grids, x_axes, y_axes, series = [], [], [], []
            for row in range(n):
                for col in range(n):
                    idx = row * n + col
                    grids.append({
                        "left": f"{5 + col * (100/n):.1f}%",
                        "top": f"{5 + row * (100/n):.1f}%",
                        "width": f"{90/n - 2:.1f}%",
                        "height": f"{90/n - 2:.1f}%"
                    })
                    x_axes.append({"gridIndex": idx, "name": dimensions[col] if row == n-1 else "", "nameLocation": "middle", "nameGap": 20, "scale": True, "splitLine": {"show": False}})
                    y_axes.append({"gridIndex": idx, "name": dimensions[row] if col == 0 else "", "nameLocation": "middle", "nameGap": 30, "scale": True, "splitLine": {"show": False}})
                    series.append({
                        "type": "scatter",
                        "xAxisIndex": idx, "yAxisIndex": idx,
                        "symbolSize": 4,
                        "data": [[row_data[col], row_data[row]] for row_data in data if len(row_data) > max(row, col)]
                    })

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"formatter": "function(p){return dimensions[p.seriesIndex % "+str(n)+"]+'='+p.data[0]+'<br/>'+dimensions[Math.floor(p.seriesIndex/"+str(n)+")]+'='+p.data[1];}"},
                "grid": grids,
                "xAxis": x_axes,
                "yAxis": y_axes,
                "series": series,
                "toolbox": {"feature": {"saveAsImage": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height))
        except Exception as e:
            raise Exception(f"矩阵坐标系生成失败: {str(e)}")
