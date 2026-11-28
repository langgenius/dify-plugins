"""Fixed-endpoint, schema-bounded JSON-RPC MCP transport for KontoCSV."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import requests

MCP_ENDPOINT = "https://www.kontocsv.de/api/mcp/claude"
CONTRACT = json.loads((Path(__file__).parent / "contract.json").read_text(encoding="utf-8"))
TOOLS = {tool["name"]: tool for tool in CONTRACT}
MAX_RESPONSE_BYTES = 1024 * 1024


class KontoCsvMcpError(Exception):
    """A sanitized failure safe to surface to an end user."""


def validate_arguments(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name not in TOOLS:
        raise KontoCsvMcpError("Unknown KontoCSV tool.")
    if not isinstance(arguments, dict):
        raise KontoCsvMcpError("Tool arguments must be an object.")
    schema = TOOLS[name]["inputSchema"]
    properties = schema["properties"]
    if set(arguments) - set(properties):
        raise KontoCsvMcpError("Unknown tool parameter.")
    cleaned = {key: value for key, value in arguments.items() if value is not None}
    for required in schema.get("required", []):
        if required not in cleaned:
            raise KontoCsvMcpError(f"Missing parameter: {required}.")
    for key, value in cleaned.items():
        field = properties[key]
        kind = field.get("type")
        if kind == "string":
            if not isinstance(value, str):
                raise KontoCsvMcpError(f"{key} must be text.")
            if not field.get("minLength", 0) <= len(value) <= field.get("maxLength", 4096):
                raise KontoCsvMcpError(f"{key} has an invalid length.")
            if field.get("pattern") and not re.fullmatch(field["pattern"], value):
                raise KontoCsvMcpError(f"{key} does not match its expected format.")
            if "enum" in field and value not in field["enum"]:
                raise KontoCsvMcpError(f"{key} is not a supported option.")
        elif kind == "boolean":
            if not isinstance(value, bool):
                raise KontoCsvMcpError(f"{key} must be a boolean.")
            if "const" in field and value != field["const"]:
                raise KontoCsvMcpError(f"{key} must be explicitly confirmed.")
        elif kind in ("integer", "number"):
            if isinstance(value, bool) or not isinstance(value, (float, int)):
                raise KontoCsvMcpError(f"{key} must be a number.")
            if kind == "integer" and not isinstance(value, int):
                raise KontoCsvMcpError(f"{key} must be an integer.")
        else:
            raise KontoCsvMcpError(f"{key} uses an unsupported parameter type.")
    if name == "convert_bank_statement_for_accounting" and cleaned.get("confirmedByUser") is not True:
        raise KontoCsvMcpError("Explicit user confirmation is required before reserving credits.")
    return cleaned


def _parse_mcp_reply(raw: bytes, media_type: str) -> dict[str, Any]:
    if "text/event-stream" in media_type.lower():
        events: list[dict[str, Any]] = []
        for event in raw.decode("utf-8").replace("\r\n", "\n").split("\n\n"):
            data_lines = [line[5:].lstrip() for line in event.splitlines() if line.startswith("data:")]
            if not data_lines:
                continue
            try:
                parsed = json.loads("\n".join(data_lines))
            except ValueError as exc:
                raise KontoCsvMcpError("KontoCSV returned an invalid MCP event.") from exc
            if isinstance(parsed, dict) and parsed.get("id") == 1:
                events.append(parsed)
        if len(events) != 1:
            raise KontoCsvMcpError("KontoCSV returned an ambiguous MCP response.")
        return events[0]
    try:
        parsed = json.loads(raw)
    except ValueError as exc:
        raise KontoCsvMcpError("KontoCSV returned an invalid MCP response.") from exc
    if not isinstance(parsed, dict):
        raise KontoCsvMcpError("KontoCSV returned an invalid MCP payload.")
    return parsed


def call_mcp(name: str, arguments: dict[str, Any], access_token: str, *, http=requests) -> dict[str, Any]:
    if not isinstance(access_token, str) or not access_token:
        raise KontoCsvMcpError("Connect a KontoCSV account through OAuth first.")
    args = validate_arguments(name, arguments)
    message = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
               "params": {"name": name, "arguments": args}}
    try:
        response = http.post(
            MCP_ENDPOINT,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
                "MCP-Protocol-Version": "2025-06-18",
            },
            json=message, timeout=(5, 45), allow_redirects=False, stream=True,
        )
    except requests.RequestException as exc:
        raise KontoCsvMcpError("The KontoCSV service is temporarily unreachable.") from exc
    try:
        if response.status_code in (401, 403):
            raise KontoCsvMcpError("KontoCSV access expired or was not authorized. Reconnect your account.")
        if response.status_code == 429:
            raise KontoCsvMcpError("The KontoCSV request limit was reached.")
        if response.status_code != 200:
            raise KontoCsvMcpError("KontoCSV could not complete the tool request.")
        chunks: list[bytes] = []
        size = 0
        for part in response.iter_content(chunk_size=8192):
            size += len(part)
            if size > MAX_RESPONSE_BYTES:
                raise KontoCsvMcpError("KontoCSV returned more data than the plugin permits.")
            chunks.append(part)
        reply = _parse_mcp_reply(b"".join(chunks), response.headers.get("Content-Type", ""))
    except requests.RequestException as exc:
        raise KontoCsvMcpError("KontoCSV response could not be read.") from exc
    finally:
        response.close()
    if reply.get("jsonrpc") != "2.0" or reply.get("id") != 1 or "error" in reply:
        raise KontoCsvMcpError("KontoCSV rejected the tool request.")
    result = reply.get("result")
    if not isinstance(result, dict) or result.get("isError"):
        raise KontoCsvMcpError("KontoCSV could not complete that operation.")
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured
    for item in result.get("content", []):
        if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
            try:
                obj = json.loads(item["text"])
            except ValueError as exc:
                raise KontoCsvMcpError("KontoCSV returned an invalid tool result.") from exc
            if isinstance(obj, dict):
                return obj
    raise KontoCsvMcpError("KontoCSV returned an unexpected tool result.")
