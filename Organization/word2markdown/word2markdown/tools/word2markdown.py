from collections.abc import Generator
from typing import Any

import docx
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class word2markdownTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        query = tool_parameters.get('query')
        file = tool_parameters.get('file')

        response = requests.get(file.url)

        try:
            # 创建临时文件
            with open("document.docx", 'wb') as file:
                file.write(response.content)

            md = self.covert_word2markdown("document.docx", query)
            yield self.create_text_message(md)
        except Exception as e:
            yield self.create_text_message(f"error {str(e)} file_url:{file.url}")
            return

    # 辅助函数：转换标题
    def convert_heading(self, heading_text, level):
        return '#' * level + ' ' + heading_text

    def table_to_markdown(self, table):
        """Convert a docx table to Markdown format."""
        markdown = []
        # Get the number of columns
        num_columns = len(table.rows[0].cells)

        # Collect all rows
        rows = []
        for row in table.rows:
            cells = [cell.text.strip().replace('\n', ' ').replace('|', '\\|') for cell in row.cells]
            # Ensure each row has the correct number of columns
            while len(cells) < num_columns:
                cells.append('')
            rows.append(cells)

        # Create header row (use first row as header)
        header_row = rows[0]
        markdown.append('| ' + ' | '.join(header_row) + ' |')

        # Create separator row
        markdown.append('| ' + ' | '.join(['---'] * num_columns) + ' |')

        # Add remaining rows
        for row in rows[1:]:
            markdown.append('| ' + ' | '.join(row) + ' |')

        return '\n'.join(markdown) + '\n'

    def covert_word2markdown(self, file_path, title_prefix):
        doc = docx.Document(file_path)
        markdown_text = ''

        for element in doc.element.body:
            if (element.tag.endswith('p')):
                paragraph = docx.text.paragraph.Paragraph(element, doc)
                if (paragraph.text is None or paragraph.text.strip() == ''):
                    continue
                # 判断标题
                if paragraph.style.name.startswith(title_prefix):
                    level = int(paragraph.style.name.split()[-1])  # 获取标题级别
                    markdown_text += self.convert_heading(paragraph.text, level) + '\n\n'
                else:
                    # 处理段落
                    markdown_text += paragraph.text + '\n\n'

            elif element.tag.endswith('tbl'):
                table = docx.table.Table(element, doc)
                # 处理表格
                markdown_text += self.table_to_markdown(table) + '\n\n'
            else:
                pass
        return markdown_text
