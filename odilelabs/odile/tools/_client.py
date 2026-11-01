"""HTTP client for Odile Direct."""

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class OdileError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class OdileDirectClient:
    def __init__(self, base_url="https://odilelabs.com/mcp/direct", api_key=None, timeout=30, fetch=None):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.fetch = fetch or self._fetch

    def _fetch(self, request):
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return response.status, response.read()
        except HTTPError as error:
            return error.code, error.read()

    def call(self, tool, arguments):
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(self.base_url, data=json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        }).encode(), headers=headers, method="POST")
        status, body = self.fetch(request)
        try:
            response = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            if not 200 <= status < 300:
                raise OdileError(status, body.decode("utf-8", errors="replace"))
            raise
        if not 200 <= status < 300:
            error = response.get("error", response)
            message = error.get("message", str(error)) if isinstance(error, dict) else str(error)
            raise OdileError(status, message)
        if "error" in response:
            error = response["error"]
            raise OdileError(error.get("code"), error.get("message", ""))
        result = response["result"]
        if "structuredContent" in result:
            return result["structuredContent"]
        content = "\n".join(part["text"] for part in result.get("content", []) if part.get("type") == "text")
        try:
            return json.loads(content)
        except ValueError:
            return content
