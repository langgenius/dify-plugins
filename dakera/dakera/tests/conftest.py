"""Pytest fixtures: a mock Dakera server + plugin path wiring.

These tests exercise the plugin's tools and provider against an in-process mock of
the Dakera REST API, so no live server is required. They are excluded from the
packaged `.difypkg` via `.difyignore`.
"""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import pytest

# Make the plugin root (parent of tests/) importable as `tools.*` / `provider.*`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_handler(received: list):
    class MockDakera(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, obj, code=200):
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(obj).encode())

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/health/live":
                self._send({"status": "ok"})
            elif parsed.path.startswith("/v1/memory/get/"):
                mid = parsed.path.rsplit("/", 1)[-1]
                received.append(("GET", parsed.path, {}, parse_qs(parsed.query)))
                self._send({"id": mid, "content": "Alice prefers Rust.", "importance": 0.9, "tags": ["pref"]})
            else:
                self._send({"error": "not found"}, 404)

        def do_PUT(self):
            parsed = urlparse(self.path)
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            received.append(("PUT", parsed.path, body, parse_qs(parsed.query)))
            self._send({"id": parsed.path.rsplit("/", 1)[-1], "content": body.get("content", "x"),
                        "importance": body.get("importance", 0.5)})

        def do_POST(self):
            parsed = urlparse(self.path)
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            received.append(("POST", parsed.path, body, dict(self.headers)))
            if parsed.path == "/v1/memory/store":
                self._send({"memory": {"id": "mem_abc123", "content": body["content"]}, "embedding_time_ms": 3})
            elif parsed.path == "/v1/memory/recall":
                self._send({"memories": [
                    {"memory": {"id": "mem_1", "content": "Alice prefers Rust for backend."}, "score": 0.91},
                    {"memory": {"id": "mem_2", "content": "Alice dislikes verbose configs."}, "score": 0.74},
                ], "query_embedding_time_ms": 5, "search_time_ms": 2})
            elif parsed.path == "/v1/memory/search":
                self._send({"memories": [
                    {"memory": {"id": "mem_1", "content": "Alice prefers Rust.", "importance": 0.9}, "score": 0.5},
                ], "total_count": 1})
            elif parsed.path == "/v1/memory/forget":
                self._send({"deleted_count": 2})
            else:
                self._send({}, 404)

    return MockDakera


@pytest.fixture()
def mock_server():
    received: list = []
    srv = HTTPServer(("127.0.0.1", 0), _make_handler(received))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        yield base, received
    finally:
        srv.shutdown()


@pytest.fixture()
def creds(mock_server):
    base, _ = mock_server
    return {"api_url": base, "api_key": "dk-test"}


def msgtext(msgs):
    return " ".join(str(getattr(m, "message", m)) for m in msgs)
