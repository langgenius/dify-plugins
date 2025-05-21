# 使用时配置的MCP工具使用指南

本指南将帮助你理解和使用"使用时配置的MCP工具"插件，这是一个允许你在每次使用时配置MCP服务器连接的Dify插件。

## 概述

MCP (Model Context Protocol) 是一种协议，允许大型语言模型(LLM)应用与外部工具交互。本插件通过HTTP with SSE传输使用MCP协议，支持在每次使用时单独配置连接信息，无需预先在provider级别进行授权。

## 安装步骤

1. 在Dify平台上，导航至"插件"部分
2. 找到并安装"使用时配置的MCP工具"插件
3. 插件安装后即可使用，无需全局配置

## 使用场景

本插件适用于以下场景：

1. 需要在不同应用中连接不同MCP服务器
2. 需要在同一应用内使用多个不同的MCP服务
3. 对不同环境（如开发、测试、生产）使用不同的MCP服务配置
4. 需要更灵活的权限控制

## 详细使用说明

### 列出MCP工具

`mcp_list_tools`工具用于列出MCP服务器上所有可用的工具。

#### 参数详解

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| server_url | 字符串 | 是 | MCP服务器的SSE端点URL |
| headers | 字符串 | 否 | HTTP请求头，JSON格式 |
| timeout | 数字 | 否 | HTTP请求超时时间（秒），默认60秒 |
| sse_read_timeout | 数字 | 否 | SSE读取超时时间（秒），默认300秒 |

#### 示例调用

```json
{
  "server_url": "http://127.0.0.1:8000/sse",
  "headers": "{\"Authorization\":\"Bearer your_token\"}",
  "timeout": 60,
  "sse_read_timeout": 300
}
```

#### 返回结果

工具将返回服务器上可用工具的列表，格式如下：

```
- tool_name_1: Tool description 1
- tool_name_2: Tool description 2
...
```

### 调用MCP工具

`mcp_call_tool`工具用于调用MCP服务器上的特定工具。

#### 参数详解

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| server_url | 字符串 | 是 | MCP服务器的SSE端点URL |
| headers | 字符串 | 否 | HTTP请求头，JSON格式 |
| timeout | 数字 | 否 | HTTP请求超时时间（秒），默认60秒 |
| sse_read_timeout | 数字 | 否 | SSE读取超时时间（秒），默认300秒 |
| tool_name | 字符串 | 是 | 要调用的工具名称 |
| arguments | 字符串 | 否 | 工具参数，JSON格式。不传默认{} |

#### 示例调用

```json
{
  "server_url": "http://127.0.0.1:8000/sse",
  "headers": "{\"Authorization\":\"Bearer your_token\"}",
  "timeout": 60,
  "sse_read_timeout": 300,
  "tool_name": "example_tool",
  "arguments": "{\"param1\":\"value1\",\"param2\":123}"
}
```

#### 返回结果

工具将返回调用结果，格式如下：

```
<结果内容>
```

## 实际应用示例

### 示例1：获取支持的数据库

假设MCP服务器上有一个`mcp_db_support`工具，用于获取所有支持的数据库：

```json
{
  "server_url": "http://your-mcp-server.com/sse",
  "tool_name": "mcp_db_support",
  "arguments": "{}"
}
```

### 示例2：执行数据库SQL查询

假设MCP服务器上有一个`mcp_db_exec`工具，用于执行数据库SQL查询：

```json
{
  "server_url": "http://your-mcp-server.com/sse",
  "tool_name": "mcp_db_exec",
  "arguments": "{\"env\":\"sit\",\"sql\":\"select * from table\"}"
}
```

### 示例3：添加或更新数据库配置

假设MCP服务器上有一个`mcp_linux_lcs_jk_dbadd_db_config`工具，用于添加或更新数据库配置：

```json
{
  "server_url": "http://your-mcp-server.com/sse",
  "tool_name": "mcp_linux_lcs_jk_dbadd_db_config",
  "arguments": "{\"random_string\":\"dummy\"}"
}
```

## 故障排除

如果遇到使用问题，请检查以下几点：

1. **连接错误**：确保MCP服务器URL正确并且可访问
2. **授权错误**：检查提供的headers是否包含正确的授权信息
3. **超时错误**：考虑增加timeout和sse_read_timeout值
4. **工具不存在**：使用`mcp_list_tools`确认服务器上是否有该工具
5. **参数格式错误**：确保JSON格式正确，特别是在转义双引号时

## 最佳实践

1. 先使用`mcp_list_tools`确认可用工具，再使用`mcp_call_tool`调用
2. 对于需要授权的MCP服务器，确保在headers中提供正确的凭据
3. 根据网络条件和工具执行时间调整超时参数
4. 对于安全敏感的应用，使用HTTPS连接
5. 保存常用的配置，以便快速重用 