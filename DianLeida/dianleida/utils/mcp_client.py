# -*- coding: utf-8 -*-
"""Minimal MCP (Model Context Protocol) client over Streamable HTTP."""
import json
from typing import Any

import httpx

PROTOCOL_VERSION = "2025-06-18"


class McpError(Exception):
    """Raised when the MCP server or the upstream business API returns an error."""

    def __init__(self, message: str, kind: str = "general"):
        super().__init__(message)
        self.kind = kind


def _classify(message: str) -> str:
    text = (message or "").lower()
    credit_keys = ("点数", "余额", "配额", "额度", "credit", "quota", "balance", "insufficient")
    auth_keys = ("鉴权", "密钥", "token", "credential", "unauthorized", "auth", "失效", "expired", "forbidden")
    if any(k in text for k in credit_keys):
        return "credit"
    if any(k in text for k in auth_keys):
        return "auth"
    return "general"


class McpClient:
    def __init__(self, url: str, timeout: float = 120.0):
        self.url = (url or "").strip()
        self.timeout = timeout

    def _headers(self, session_id: str = "") -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if session_id:
            headers["Mcp-Session-Id"] = session_id
        return headers

    def _post(self, client: httpx.Client, payload: dict, session_id: str = ""):
        response = client.post(
            self.url,
            headers=self._headers(session_id),
            content=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        )
        new_session = response.headers.get("mcp-session-id") or session_id
        if response.status_code >= 400:
            raise McpError(
                "MCP server returned HTTP {}: {}".format(response.status_code, response.text[:300]),
                _classify(response.text),
            )
        if response.status_code == 202 or not response.content:
            return None, new_session
        content_type = response.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            matched = None
            for line in response.text.splitlines():
                line = line.strip()
                if not line.startswith("data:"):
                    continue
                chunk = line[len("data:"):].strip()
                try:
                    obj = json.loads(chunk)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict) and obj.get("id") == payload.get("id"):
                    matched = obj
            if matched is None:
                raise McpError("MCP server returned an empty event stream response.")
            return matched, new_session
        try:
            return response.json(), new_session
        except ValueError:
            raise McpError("MCP server returned a non-JSON response: {}".format(response.text[:300]))

    def _handshake(self, client: httpx.Client) -> str:
        init = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "dify-dianleida", "version": "1.1.0"},
            },
        }
        result, session_id = self._post(client, init)
        if isinstance(result, dict) and result.get("error"):
            raise McpError(json.dumps(result["error"], ensure_ascii=False), "general")
        self._post(client, {"jsonrpc": "2.0", "method": "notifications/initialized"}, session_id)
        return session_id

    def list_tools(self) -> list:
        if not self.url:
            raise McpError("The DianLeiDa MCP key URL is empty.", "auth")
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            session_id = self._handshake(client)
            payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
            result, _ = self._post(client, payload, session_id)
            if isinstance(result, dict) and result.get("error"):
                raise McpError(json.dumps(result["error"], ensure_ascii=False), "general")
            tools = ((result or {}).get("result") or {}).get("tools") or []
            return [item.get("name") for item in tools if isinstance(item, dict)]

    def call_tool(self, name: str, arguments: dict) -> Any:
        if not self.url:
            raise McpError("The DianLeiDa MCP key URL is empty.", "auth")
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            session_id = self._handshake(client)
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
            result, _ = self._post(client, payload, session_id)
            if result is None:
                raise McpError("MCP server returned an empty tools/call response.")
            if isinstance(result, dict) and result.get("error"):
                error = result["error"]
                message = error.get("message") if isinstance(error, dict) else str(error)
                raise McpError(message or "Unknown MCP error", _classify(message))
            return self._unwrap((result or {}).get("result") or {})

    @staticmethod
    def _unwrap(result: dict) -> Any:
        structured = result.get("structuredContent")
        if isinstance(structured, (dict, list)) and structured:
            return structured
        content = result.get("content") or []
        texts = []
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text" and item.get("text"):
                    texts.append(item["text"])
        if texts:
            joined = "\n".join(texts)
            try:
                return json.loads(joined)
            except ValueError:
                if result.get("isError"):
                    raise McpError(joined[:300], _classify(joined))
                return {"text": joined}
        if result.get("isError"):
            raise McpError("The MCP tool reported an error.", "general")
        return result
