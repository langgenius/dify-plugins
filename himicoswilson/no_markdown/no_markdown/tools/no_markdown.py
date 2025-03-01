from collections.abc import Generator
from typing import Any
import re
import markdown2
from bs4 import BeautifulSoup

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class NoMarkdownTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            text = tool_parameters.get("text", "")
            preserve_links = tool_parameters.get("preserve_links", True)
            
            # Convert markdown to HTML
            html = markdown2.markdown(text)
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Handle links based on preserve_links parameter
            if preserve_links:
                # Replace <a> tags with text (text) [url]
                for link in soup.find_all('a'):
                    url = link.get('href', '')
                    if url:
                        link.replace_with(f"{link.get_text()} [{url}]")
            else:
                # Replace <a> tags with just their text content
                for link in soup.find_all('a'):
                    link.replace_with(link.get_text())
            
            # Get text content, removing only HTML tags while preserving whitespace
            text = soup.get_text(separator='\n')
            
            # Remove language identifier at the start of code blocks if present
            text = re.sub(r'^[a-zA-Z]+\n', '', text)
            
            yield self.create_text_message(text)
            
        except Exception as e:
            yield self.create_error_message(f"Error processing markdown: {str(e)}")
