from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.echarts_util import get_echarts_config

class DifyEchartsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        csv_data = tool_parameters.get("data", '')
        chart_type = tool_parameters.get("chart_type", 'pie')
        chart_title = tool_parameters.get("chart_title", '图表展示')

        if not csv_data or csv_data == '':
            yield self.create_text_message(f"Error: No data found in credentials")
        elif not chart_title or chart_title == '':
            yield self.create_text_message(f"Error: No chart title found in credentials")
        elif not chart_type or chart_type == '':
            yield self.create_text_message(f"Error: No chart type found in credentials")
        else:
            echarts_config = get_echarts_config(csv_data, chart_type, chart_title)
            yield self.create_text_message(f"{echarts_config}")
            # yield self.create_json_message({
            #     "result": echarts_config
            # })
