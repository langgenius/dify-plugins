# -*- coding: utf-8 -*-
"""Shared request builder and error mapping for every tool in this plugin."""
import json
from typing import Any

from dify_plugin.errors.tool import ToolInvokeError

from utils.mcp_client import McpClient, McpError

CREDIT_HINT = (
    "当前您的MCP点数不足，无法使用此服务。请及时充值后重试，"
    "充值请点击：https://www.dianleida.net/mcp/buy/"
)
AUTH_HINT = (
    "店雷达 MCP 密钥已失效或鉴权失败。请到 https://www.dianleida.net/mcp 重新获取密钥，"
    "并在插件「授权」处更新该 MCP 密钥 URL 后重试。"
)
GENERAL_HINT = "店雷达接口调用失败。"


def _assign(target: dict, path: str, value: Any) -> None:
    keys = path.split(".")
    node = target
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = value


def _parse_json(raw: Any, field: str) -> Any:
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(str(raw))
    except ValueError:
        raise ToolInvokeError("参数 {} 不是合法 JSON：{}".format(field, str(raw)[:120]))


def build_arguments(spec: dict, tool_parameters: dict) -> dict:
    arguments: dict = {}
    for field, kind in spec.items():
        if field == "__advanced__":
            raw = tool_parameters.get("advanced_filters")
            if raw not in (None, "", {}):
                extra = _parse_json(raw, "advanced_filters")
                if not isinstance(extra, dict):
                    raise ToolInvokeError("参数 advanced_filters 必须是 JSON 对象。")
                arguments.update(extra)
            continue
        value = tool_parameters.get(field)
        if value is None or value == "" or value == []:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if kind == "str":
            arguments[field] = str(value)
        elif kind == "int":
            arguments[field] = int(float(value))
        elif kind == "float":
            arguments[field] = float(value)
        elif kind.startswith("list_int:"):
            sep = kind.split(":", 1)[1]
            arguments[field] = [int(float(item.strip())) for item in str(value).split(sep) if item.strip()]
        elif kind.startswith("list1:"):
            arguments[kind.split(":", 1)[1]] = [str(value)]
        elif kind.startswith("list:"):
            sep = kind.split(":", 1)[1]
            arguments[field] = [item.strip() for item in str(value).split(sep) if item.strip()]
        elif kind == "json":
            arguments[field] = _parse_json(value, field)
        elif kind.startswith("nest_json:"):
            _assign(arguments, kind.split(":", 1)[1], _parse_json(value, field))
        elif kind.startswith("nest_int:"):
            _assign(arguments, kind.split(":", 1)[1], int(float(value)))
        elif kind.startswith("nest:"):
            _assign(arguments, kind.split(":", 1)[1], str(value))
        else:
            arguments[field] = value
    return arguments


def _business_check(payload: Any) -> None:
    if not isinstance(payload, dict):
        return
    code = payload.get("code")
    if code in (None, 200, "200"):
        return
    message = str(payload.get("msg") or "unknown error")
    kind = "general"
    if any(k in message for k in ("点数", "余额", "配额", "额度")):
        kind = "credit"
    elif any(k in message.lower() for k in ("鉴权", "密钥", "token", "失效", "auth", "credential")):
        kind = "auth"
    raise McpError(message, kind)


def run_mcp_tool(tool: str, envelope: str, spec: dict, tool_parameters: dict, credentials: dict) -> str:
    credentials = credentials or {}
    url = str(credentials.get("api_key") or "").strip()
    if not url:
        raise ToolInvokeError("未配置店雷达 MCP 密钥 URL，请在插件「授权」中填写后重试。")
    arguments = build_arguments(spec, tool_parameters or {})
    payload = {envelope: arguments} if envelope else arguments
    client = McpClient(url)
    try:
        result = client.call_tool(tool, payload)
        _business_check(result)
    except McpError as error:
        hint = {"credit": CREDIT_HINT, "auth": AUTH_HINT}.get(error.kind, GENERAL_HINT)
        raise ToolInvokeError("{} {}".format(hint, str(error)))
    except ToolInvokeError:
        raise
    except Exception as error:
        raise ToolInvokeError("{} {}".format(GENERAL_HINT, error))
    return json.dumps(result, ensure_ascii=False)
