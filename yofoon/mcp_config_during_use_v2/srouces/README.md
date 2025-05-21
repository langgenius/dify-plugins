# MCP Config During Use

A Dify plugin that allows configuring MCP (Model Context Protocol) connections during use. It enables discovering and calling tools via MCP protocol through HTTP with SSE transport or Streamable HTTP transport, with configuration done at runtime.

> This project is based on [arrenxxxxx/dify-plugin-tools-mcp_config_during_use](https://github.com/arrenxxxxx/dify-plugin-tools-mcp_config_during_use) with enhancements to support streamable_http transport.

[English](#mcp-config-during-use) | [中文简体](README_zh.md)

## Features

- Configure MCP server connection information for each call separately
- List available tools on MCP servers
- Call specific tools on MCP servers
- Support HTTP headers configuration for authorization and other features
- Configure different timeout parameters
- Support both SSE and Streamable HTTP transport methods

## Tool List

The plugin provides two main tools:

1. **List MCP Tools (mcp_list_tools)**
   - Used to list all available tools on an MCP server

2. **Call MCP Tool (mcp_call_tool)**
   - Used to call a specific tool on an MCP server

## Usage

### List MCP Tools

Use the `mcp_list_tools` tool to list all available tools on a specified MCP server.

Parameters:
- `server_url` (required): The endpoint URL of the MCP Server
- `transport` (optional): Transport protocol to use, either "sse" (default) or "streamable_http"
- `headers` (optional): HTTP headers in JSON format
- `timeout` (optional): HTTP request timeout in seconds
- `sse_read_timeout` (optional): SSE read timeout in seconds (only used with "sse" transport)

Example with SSE transport:
```json
{
  "server_url": "http://127.0.0.1:8000/sse",
  "transport": "sse",
  "headers": "{\"Authorization\":\"Bearer your_token\"}",
  "timeout": 60,
  "sse_read_timeout": 300
}
```

Example with Streamable HTTP transport:
```json
{
  "server_url": "http://127.0.0.1:8000/mcp",
  "transport": "streamable_http",
  "headers": "{\"Authorization\":\"Bearer your_token\"}",
  "timeout": 60
}
```

### Call MCP Tool

Use the `mcp_call_tool` tool to call a specific tool on an MCP server.

Parameters:
- `server_url` (required): The endpoint URL of the MCP Server
- `transport` (optional): Transport protocol to use, either "sse" (default) or "streamable_http"
- `headers` (optional): HTTP headers in JSON format
- `timeout` (optional): HTTP request timeout in seconds
- `sse_read_timeout` (optional): SSE read timeout in seconds (only used with "sse" transport)
- `tool_name` (required): Name of the tool to execute
- `arguments` (required): Tool arguments in JSON format

Example with SSE transport:
```json
{
  "server_url": "http://127.0.0.1:8000/sse",
  "transport": "sse",
  "headers": "{\"Authorization\":\"Bearer your_token\"}",
  "timeout": 60,
  "sse_read_timeout": 300,
  "tool_name": "example_tool",
  "arguments": "{\"param1\":\"value1\",\"param2\":123}"
}
```

Example with Streamable HTTP transport:
```json
{
  "server_url": "http://127.0.0.1:8000/mcp",
  "transport": "streamable_http",
  "headers": "{\"Authorization\":\"Bearer your_token\"}",
  "timeout": 60,
  "tool_name": "example_tool",
  "arguments": "{\"param1\":\"value1\",\"param2\":123}"
}
```

## Differences from Pre-authorized MCP Tools

Compared to pre-authorized MCP tools, the main differences of this plugin are:

1. **Configuration Method**: This plugin allows configuring connection information at call time, while pre-authorized MCP tools require configuration at the provider level
2. **Flexibility**: Different tool calls can connect to different MCP servers
3. **Isolation**: Each application can use its own MCP server configuration without affecting others
4. **Permission Management**: No need for global authorization at the provider level, providing more flexible permission control

## Requirements

- Python 3.12 or higher
- Dependencies:
  - httpx >= 0.27.0
  - httpx-sse >= 0.4.0
  - dify_plugin = 0.0.1b76

## Notes

- Ensure the provided MCP server URL is valid and supports the selected transport protocol
- For SSE transport, the URL typically ends with "/sse"
- For Streamable HTTP transport, the URL typically ends with "/mcp"
- In the `headers` and `arguments` parameters, JSON objects need to be converted to strings with properly escaped double quotes
- Adjust timeout parameters as needed, especially for long-running tool calls 