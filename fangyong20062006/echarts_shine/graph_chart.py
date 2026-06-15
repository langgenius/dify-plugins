import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chart_renderer import build_html


class GraphChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            title = tool_parameters.get("title", "关系图")
            raw = json.loads(tool_parameters.get("data", "{}"))
            nodes = raw.get("nodes", [])
            links = raw.get("links", [])
            width = int(tool_parameters.get("width", 900))
            height = int(tool_parameters.get("height", 500))

            # 统计分类
            categories = list({n.get("category", "default") for n in nodes})
            cat_list = [{"name": c} for c in categories]
            for n in nodes:
                if "category" not in n:
                    n["category"] = "default"
                if "symbolSize" not in n:
                    n["symbolSize"] = max(10, n.get("value", 10) * 2) if n.get("value") else 20
                n["label"] = {"show": True}

            option = {
                "title": {"text": title, "left": "center"},
                "tooltip": {"formatter": "function(p){return p.dataType==='node'?p.data.name+': '+(p.data.value||''):p.data.source+' → '+p.data.target;}"},
                "legend": [{"data": [c["name"] for c in cat_list]}],
                "series": [{
                    "name": title, "type": "graph", "layout": "force",
                    "data": nodes, "links": links, "categories": cat_list,
                    "roam": True, "draggable": True,
                    "force": {"repulsion": 100, "edgeLength": 80},
                    "emphasis": {"focus": "adjacency", "lineStyle": {"width": 4}},
                    "lineStyle": {"color": "source", "curveness": 0.3},
                    "edgeLabel": {"show": False}
                }],
                "toolbox": {"feature": {"saveAsImage": {}}}
            }
            yield self.create_text_message(build_html(title, option, width, height))
        except Exception as e:
            raise Exception(f"关系图生成失败: {str(e)}")
