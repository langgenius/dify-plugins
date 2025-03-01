from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.no_markdown import NoMarkdownTool


class NoMarkdownProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Test the tool with a markdown text containing links
            test_text = "# Test\nThis is a **test** with [link](https://example.com)."
            tool = NoMarkdownTool.from_credentials(credentials)
            
            # Test without link preservation
            for _ in tool.invoke(tool_parameters={"text": test_text, "preserve_links": False}):
                pass
                
            # Test with link preservation
            for _ in tool.invoke(tool_parameters={"text": test_text, "preserve_links": True}):
                pass
                
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Failed to validate tool: {str(e)}")
