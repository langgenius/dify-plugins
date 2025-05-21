import json
import logging
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.mcp_client import McpClientsUtil


class McpCallTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        server_url = tool_parameters.get("server_url", "")
        if not server_url:
            raise ValueError("Please fill in the server_url")
        
        transport = tool_parameters.get("transport", "sse")
        if transport not in ["sse", "streamable_http"]:
            raise ValueError("Transport must be either 'sse' or 'streamable_http'")
        
        headers = None
        headers_json = tool_parameters.get("headers", "")
        if headers_json:
            try:
                headers = json.loads(headers_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Headers must be a valid JSON string: {e}")
        
        timeout = tool_parameters.get("timeout", 60)
        sse_read_timeout = tool_parameters.get("sse_read_timeout", 300)
        
        tool_name = tool_parameters.get("tool_name", "")
        if not tool_name:
            raise ValueError("Please fill in the tool_name")
            
        arguments_json = tool_parameters.get("arguments", "")
        if not arguments_json:
            arguments_json = "{}"
            
        try:
            arguments = json.loads(arguments_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Arguments must be a valid JSON string: {e}")

        try:
            result = McpClientsUtil.execute_tool(
                server_url=server_url,
                tool_name=tool_name,
                tool_args=arguments,
                transport=transport,
                headers=headers,
                timeout=timeout,
                sse_read_timeout=sse_read_timeout
            )
            yield self.create_text_message(json.dumps(result))
        except Exception as e:
            error_msg = f"Error calling MCP Server tool: {str(e)}"
            logging.error(error_msg)
            yield self.create_text_message(error_msg) 