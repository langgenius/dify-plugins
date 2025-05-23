# MCP 使用时配置工具 (MCP Config During Use)

这是一个Dify插件，用于通过HTTP with SSE传输或Streamable HTTP传输使用MCP协议来发现和调用工具，支持在每次使用时单独配置连接信息。

> 本项目基于 [arrenxxxxx/dify-plugin-tools-mcp_config_during_use](https://github.com/arrenxxxxx/dify-plugin-tools-mcp_config_during_use) 二次开发，增强了对streamable_http传输的支持。

[English](README.md) | [中文简体](#mcp-使用时配置工具-mcp-config-during-use)

## 功能特点

- 支持在每次调用时单独配置MCP服务器连接信息
- 提供列出MCP服务器上可用工具的功能
- 提供调用MCP服务器上工具的功能
- 支持配置HTTP请求头，实现授权等功能
- 支持配置不同的超时参数
- 支持SSE和Streamable HTTP两种传输方式

## 工具列表

插件提供两个主要工具：

1. **列出MCP工具 (mcp_list_tools)**
   - 用于列出MCP服务器上可用的工具

2. **调用MCP工具 (mcp_call_tool)**
   - 用于调用MCP服务器上的特定工具

## 使用方法

### 列出MCP工具

使用`mcp_list_tools`工具可以列出指定MCP服务器上的所有可用工具。

参数说明:
- `server_url` (必填): MCP服务器的端点URL
- `transport` (可选): 传输协议类型，可选值为 "sse"（默认）或 "streamable_http"
- `headers` (可选): HTTP请求头，JSON格式
- `timeout` (可选): HTTP请求超时时间（秒）
- `sse_read_timeout` (可选): SSE读取超时时间（秒）（仅在使用"sse"传输方式时适用）

使用SSE传输的示例:
```json
{
  "server_url": "http://127.0.0.1:8000/sse",
  "transport": "sse",
  "headers": "{\"Authorization\":\"Bearer your_token\"}",
  "timeout": 60,
  "sse_read_timeout": 300
}
```

使用Streamable HTTP传输的示例:
```json
{
  "server_url": "http://127.0.0.1:8000/mcp",
  "transport": "streamable_http",
  "headers": "{\"Authorization\":\"Bearer your_token\"}",
  "timeout": 60
}
```

### 调用MCP工具

使用`mcp_call_tool`工具可以调用MCP服务器上的特定工具。

参数说明:
- `server_url` (必填): MCP服务器的端点URL
- `transport` (可选): 传输协议类型，可选值为 "sse"（默认）或 "streamable_http"
- `headers` (可选): HTTP请求头，JSON格式
- `timeout` (可选): HTTP请求超时时间（秒）
- `sse_read_timeout` (可选): SSE读取超时时间（秒）（仅在使用"sse"传输方式时适用）
- `tool_name` (必填): 要调用的工具名称
- `arguments` (必填): 工具参数，JSON格式

使用SSE传输的示例:
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

使用Streamable HTTP传输的示例:
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

## 与预授权MCP工具的区别

与预授权的MCP工具相比，此插件的主要区别是：

1. **配置方式**: 本插件支持在每次调用时配置连接信息，而预授权MCP工具需要在provider级别预先配置
2. **灵活性**: 不同的工具调用可以连接不同的MCP服务器
3. **隔离性**: 每个应用可以使用自己的MCP服务器配置，不会互相影响
4. **权限管理**: 无需在provider级别进行全局授权，更灵活的权限控制

## 安装要求

- Python 3.12 或更高版本
- 依赖包:
  - httpx >= 0.27.0
  - httpx-sse >= 0.4.0
  - dify_plugin = 0.0.1b76

## 注意事项

- 确保提供的MCP服务器URL是有效的并且支持所选的传输协议
- 对于SSE传输方式，URL通常以"/sse"结尾
- 对于Streamable HTTP传输方式，URL通常以"/mcp"结尾
- 在`headers`和`arguments`参数中，需要将JSON对象转换为字符串，并正确转义双引号
- 根据需要调整超时参数，特别是对于长时间运行的工具调用 