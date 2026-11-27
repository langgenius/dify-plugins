"""Bounded fixed-endpoint transport for the existing Edict IQ MCP server."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import requests

MCP_ENDPOINT = "https://edictiq.com/api/mcp"
CONTRACT = json.loads((Path(__file__).parent / "contract.json").read_text(encoding="utf-8"))
TOOLS = {item["name"]: item for item in CONTRACT}
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)


class EdictIqMcpError(Exception):
    """A sanitized error suitable for disclosure to a Dify user."""


def validate_arguments(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name not in TOOLS:
        raise EdictIqMcpError("Unrecognized Edict IQ tool.")
    if not isinstance(arguments, dict):
        raise EdictIqMcpError("Tool arguments must be an object.")
    schema = TOOLS[name]["inputSchema"]
    properties = schema["properties"]
    if set(arguments) - set(properties):
        raise EdictIqMcpError("Unknown tool parameter.")
    for required in schema.get("required", []):
        if required not in arguments or arguments[required] is None:
            raise EdictIqMcpError(f"Required parameter missing: {required}.")
    cleaned = {}
    for key, value in arguments.items():
        if value is None:
            continue
        field = properties[key]
        kind = field["type"]
        if kind == "string":
            if not isinstance(value, str):
                raise EdictIqMcpError(f"{key} must be text.")
            if len(value) > field.get("maxLength", 10000) or len(value) < field.get("minLength", 0):
                raise EdictIqMcpError(f"{key} has an invalid length.")
            if field.get("format") == "uuid" and not UUID_RE.fullmatch(value):
                raise EdictIqMcpError(f"{key} must be a UUID.")
            if "enum" in field and value not in field["enum"]:
                raise EdictIqMcpError(f"{key} must use a supported value.")
        elif kind == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise EdictIqMcpError(f"{key} must be an integer.")
            if not field.get("minimum", -(2**63)) <= value <= field.get("maximum", 2**63 - 1):
                raise EdictIqMcpError(f"{key} is outside the allowed range.")
        elif kind == "array":
            if not isinstance(value, list) or len(value) > field.get("maxItems", 20):
                raise EdictIqMcpError(f"{key} must be a bounded list.")
            item = field["items"]
            if item.get("type") == "string":
                if any(not isinstance(v, str) or len(v) > item.get("maxLength", 10000) for v in value):
                    raise EdictIqMcpError(f"{key} has an invalid entry.")
            else:
                raise EdictIqMcpError(f"{key} has an unsupported element type.")
        else:
            raise EdictIqMcpError(f"{key} uses an unsupported parameter type.")
        cleaned[key] = value
    return cleaned


def call_mcp(name: str, parameters: dict[str, Any], access_token: str, *, http=requests) -> dict[str, Any]:
    if not isinstance(access_token, str) or not access_token.strip():
        raise EdictIqMcpError("Connect an Edict IQ account using OAuth first.")
    arguments = validate_arguments(name, parameters)
    request = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
               "params": {"name": name, "arguments": arguments}}
    try:
        response = http.post(
            MCP_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json",
                     "Accept": "application/json, text/event-stream"},
            json=request, timeout=(5, 25), allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise EdictIqMcpError("Edict IQ is temporarily unreachable.") from exc
    if response.status_code in (401, 403):
        raise EdictIqMcpError("Edict IQ authorization expired or lacks permission. Reconnect your account.")
    if response.status_code == 429:
        raise EdictIqMcpError("Edict IQ rate limit reached.")
    if response.status_code != 200:
        raise EdictIqMcpError("Edict IQ could not process this request.")
    if len(response.content) > 1024 * 1024:
        raise EdictIqMcpError("Edict IQ returned a response larger than the tool limit.")
    try:
        data = response.json()
    except ValueError as exc:
        raise EdictIqMcpError("Edict IQ returned an invalid tool response.") from exc
    if not isinstance(data, dict) or data.get("jsonrpc") != "2.0" or data.get("id") != 1:
        raise EdictIqMcpError("Edict IQ returned an unexpected tool response.")
    if "error" in data:
        raise EdictIqMcpError("Edict IQ rejected the tool request.")
    result = data.get("result")
    if not isinstance(result, dict):
        raise EdictIqMcpError("Edict IQ returned an unexpected result.")
    if result.get("isError"):
        raise EdictIqMcpError("The Edict IQ tool could not complete the requested operation.")
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured
    if isinstance(structured, list):
        return {"items": structured}
    content = result.get("content")
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                try:
                    parsed = json.loads(item["text"])
                except ValueError:
                    return {"text": item["text"][:4096]}
                if isinstance(parsed, dict):
                    return parsed
                return {"value": parsed}
    return {"result": result}
