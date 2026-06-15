import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class GlSurfaceChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "3D曲面图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            # data: {"data":[[x,y,z],...]} or {"formula":"sin(x)*cos(y)","range":[-3,3,0.1]}
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 600))

            if "formula" in raw:
                # 公式模式：生成 JavaScript 表达式
                formula = raw.get("formula", "Math.sin(x)*Math.cos(y)")
                x_range = raw.get("x_range", [-3, 3, 0.2])
                y_range = raw.get("y_range", [-3, 3, 0.2])
                data_js = f"""
(function(){{
  var data=[];
  for(var x={x_range[0]};x<={x_range[1]};x+={x_range[2] if len(x_range)>2 else 0.2}){{
    for(var y={y_range[0]};y<={y_range[1]};y+={y_range[2] if len(y_range)>2 else 0.2}){{
      data.push([x,y,{formula}]);
    }}
  }}
  return data;
}})()"""
                series_data = {"type": "surface", "dataShape": [50, 50],
                               "wireframe": {"show": True},
                               "itemStyle": {"opacity": 0.7}}
                # 使用 JS 函数模式
                option = {
                    "title": {"text": title, "left": "center"},
                    "tooltip": {},
                    "visualMap": {"calculable": True, "min": -1, "max": 1,
                                  "inRange": {"color": ["#e0f0ff","#5ab1ef","#c12e34"]}},
                    "xAxis3D": {"type": "value"},
                    "yAxis3D": {"type": "value"},
                    "zAxis3D": {"type": "value"},
                    "grid3D": {"viewControl": {"autoRotate": False}},
                    "series": [{"type": "surface", "equation": {
                        "x": {"step": x_range[2] if len(x_range)>2 else 0.1,
                              "min": x_range[0], "max": x_range[1]},
                        "y": {"step": y_range[2] if len(y_range)>2 else 0.1,
                              "min": y_range[0], "max": y_range[1]},
                        "z": formula
                    }}]
                }
            else:
                pts = raw.get("data", [])
                z_vals = [p[2] for p in pts if len(p)>=3]
                option = {
                    "title": {"text": title, "left": "center"},
                    "tooltip": {},
                    "visualMap": {"calculable": True,
                                  "min": min(z_vals) if z_vals else 0,
                                  "max": max(z_vals) if z_vals else 1,
                                  "inRange": {"color": ["#e0f0ff","#5ab1ef","#c12e34"]}},
                    "xAxis3D": {"type": "value"},
                    "yAxis3D": {"type": "value"},
                    "zAxis3D": {"type": "value"},
                    "grid3D": {"viewControl": {"autoRotate": False}},
                    "series": [{"type": "surface", "data": pts,
                                "wireframe": {"show": True}, "itemStyle": {"opacity": 0.7}}]
                }
            yield self.create_text_message(build_html(title, option, width, height, use_gl=True))
        except Exception as e:
            raise Exception(f"3D曲面图生成失败: {str(e)}")
