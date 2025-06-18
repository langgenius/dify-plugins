import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from openpyxl import Workbook
from io import BytesIO

class ArrayToExcelTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
                将传入的 JSON 格式的二维数组数据转换成 Excel 文件，并支持设置列宽和合并单元格。

                参数：
                - tool_parameters: 包含 "data_json" 字段的字典，"data_json" 是一个 JSON 字符串，
                  该字符串包含以下字段：
                    * data: 二维数组，Excel 中的表格数据
                    * col_widths: dict，列号（字符串）到列宽的映射，可选
                    * merges: list，合并单元格的范围列表，每个元素包含
                        start_row, start_col, end_row, end_col 四个字段，表示合并区域

                返回：
                - 生成器，yield ToolInvokeMessage 对象，成功时返回 Excel 文件的二进制数据
                  失败时返回文本错误信息
                """
        data_json = tool_parameters.get("data_json", "")

        if not data_json:
            yield self.create_text_message("参数错误：缺少 'data_json'")
            return

        try:
            if isinstance(data_json, str):
                # 连续解析两次，防止多层字符串转义
                params = json.loads(data_json)
                if isinstance(params, str):
                    params = json.loads(params)
            else:
                params = data_json
        except Exception as e:
            yield self.create_text_message(f"参数解析失败: {e}")
            return

        data = params.get("data")
        col_widths = params.get("col_widths", {})
        merges = params.get("merges", [])

        if not data or not isinstance(data, list):
            yield self.create_text_message("参数错误：'data' 应为二维数组")
            return

        wb = Workbook()
        ws = wb.active

        # 写入数据
        for r, row in enumerate(data, start=1):
            if not isinstance(row, list):
                yield self.create_text_message(f"参数错误：第 {r} 行不是数组")
                return
            for c, val in enumerate(row, start=1):
                ws.cell(row=r, column=c, value=val)

        # 设置列宽
        try:
            for col_str, width in col_widths.items():
                col_idx = int(col_str)
                ws.column_dimensions[chr(64 + col_idx)].width = float(width)
        except Exception as e:
            yield self.create_text_message(f"设置列宽失败: {e}")
            return

        # 处理合并单元格
        try:
            for merge in merges:
                start_row = merge["start_row"]
                start_col = merge["start_col"]
                end_row = merge["end_row"]
                end_col = merge["end_col"]
                start_cell = ws.cell(row=start_row, column=start_col).coordinate
                end_cell = ws.cell(row=end_row, column=end_col).coordinate
                ws.merge_cells(f"{start_cell}:{end_cell}")
        except Exception as e:
            yield self.create_text_message(f"合并单元格失败: {e}")
            return

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        yield self.create_blob_message(
            blob=output.getvalue(),
            meta={
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "output_filename": "output.xlsx",
            },
        )

