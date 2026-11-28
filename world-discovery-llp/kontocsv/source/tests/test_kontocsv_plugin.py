"""Focused no-credentials/no-billing regression tests for the Dify adapter."""
from __future__ import annotations

import base64
import hashlib
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import yaml

from tools.mcp_client import (
    CONTRACT, MCP_ENDPOINT, TOOLS,
    KontoCsvMcpError, _parse_mcp_reply, call_mcp, validate_arguments,
)


class FakeResponse:
    def __init__(self, data: bytes, content_type="application/json", status=200):
        self.content = data
        self.status_code = status
        self.headers = {"Content-Type": content_type}
        self.closed = False
    def iter_content(self, chunk_size=8192):
        yield self.content
    def close(self):
        self.closed = True


class ContractTests(unittest.TestCase):
    def test_exact_tools_and_parameter_parity(self):
        expected = [
            "create_browser_upload_session", "complete_browser_upload",
            "inspect_bank_statement", "prepare_bank_statement_conversion",
            "get_credit_balance", "convert_bank_statement_for_accounting",
            "get_conversion_status", "download_accounting_export",
        ]
        self.assertEqual([t["name"] for t in CONTRACT], expected)
        for tool in CONTRACT:
            name = tool["name"]
            yaml_path = Path(__file__).resolve().parents[1] / "src" / "tools" / (name + ".yaml")
            data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            yaml_fields = [param["name"] for param in data["parameters"]]
            self.assertEqual(yaml_fields, list(tool["inputSchema"]["properties"]))
            expected_required = tool["inputSchema"].get("required", [])
            self.assertEqual([p["name"] for p in data["parameters"] if p["required"]], expected_required)
            self.assertEqual(data["extra"]["python"]["source"], f"tools/{name}.py")

    def test_all_server_ids_preserved_without_guessing(self):
        self.assertEqual(validate_arguments("complete_browser_upload", {"uploadSessionId": "12345678:abc"}),
                         {"uploadSessionId": "12345678:abc"})
        with self.assertRaises(KontoCsvMcpError):
            validate_arguments("complete_browser_upload", {"uploadSessionId": "bad"})
        with self.assertRaises(KontoCsvMcpError):
            validate_arguments("complete_browser_upload", {"uploadSessionId": "12345678", "secret": "x"})

    def test_conversion_requires_literal_true(self):
        for value in (None, "", 1, False, "true", "yes", "True"):
            with self.subTest(value=value):
                with self.assertRaises(KontoCsvMcpError):
                    validate_arguments("convert_bank_statement_for_accounting",
                                       {"quoteId": "12345678", "confirmedByUser": value})
        self.assertEqual(
            validate_arguments("convert_bank_statement_for_accounting",
                               {"quoteId": "12345678", "confirmedByUser": True}),
            {"quoteId": "12345678", "confirmedByUser": True},
        )

    def test_enum_and_string_bounds(self):
        with self.assertRaises(KontoCsvMcpError):
            validate_arguments("create_browser_upload_session", {"mediaType": "text/html"})
        self.assertEqual(
            validate_arguments("create_browser_upload_session", {"mediaType": "application/pdf", "locale": "en"}),
            {"mediaType": "application/pdf", "locale": "en"},
        )
        with self.assertRaises(KontoCsvMcpError):
            validate_arguments("inspect_bank_statement", {"sourceId": "x" * 4097})

    def test_sse_and_json_transport(self):
        answer = {"jsonrpc": "2.0", "id": 1, "result": {"structuredContent": {"availableCredits": 7}}}
        response = FakeResponse(("event: message\ndata: " + json.dumps(answer) + "\n\n").encode(),
                                content_type="text/event-stream")
        class MockHttp:
            def post(self, url, **kwargs):
                self_kwargs = kwargs
                assert url == MCP_ENDPOINT
                assert kwargs["allow_redirects"] is False
                assert kwargs["json"]["params"]["name"] == "get_credit_balance"
                assert kwargs["headers"]["Authorization"] == "Bearer test-token"
                return response
        self.assertEqual(call_mcp("get_credit_balance", {}, "test-token", http=MockHttp()),
                         {"availableCredits": 7})
        self.assertTrue(response.closed)
        self.assertEqual(_parse_mcp_reply(json.dumps(answer).encode(), "application/json"), answer)

    def test_invalid_mcp_errors_are_not_exposed(self):
        error = {"jsonrpc": "2.0", "id": 1, "error": {"message": "private-token secret"}}
        class MockHttp:
            def post(self, url, **kwargs):
                return FakeResponse(json.dumps(error).encode())
        with self.assertRaises(KontoCsvMcpError) as ctx:
            call_mcp("get_credit_balance", {}, "test-token", http=MockHttp())
        self.assertNotIn("private-token", str(ctx.exception))

    def test_bounded_response(self):
        class MockHttp:
            def post(self, url, **kwargs):
                return FakeResponse(b"x" * (1024 * 1024 + 1))
        with self.assertRaises(KontoCsvMcpError):
            call_mcp("get_credit_balance", {}, "test-token", http=MockHttp())

    def test_no_disallowed_financial_tools(self):
        self.assertEqual(len(TOOLS), 8)
        self.assertFalse(any("checkout" in n or "quote_bank_statement" in n or "ingest_attached" in n
                             for n in TOOLS))


class OAuthTests(unittest.TestCase):
    def test_pkce_challenge_and_state_bound_to_client_and_callback(self):
        from provider.kontocsv import KontoCsvProvider, _cipher, _validate_callback, RESOURCE_URL
        from cryptography.fernet import InvalidToken
        p = KontoCsvProvider.__new__(KontoCsvProvider)
        creds = {"client_id": "test-client", "client_secret": "not-a-real-secret"}
        callback = "https://cloud.dify.ai/console/api/oauth/plugin/world-discovery-llp/kontocsv/tool/callback"
        url = p._oauth_get_authorization_url(callback, creds)
        query = parse_qs(urlsplit(url).query)
        self.assertEqual(query["scope"], ["mcp:tools offline_access"])
        self.assertEqual(query["resource"], [RESOURCE_URL])
        self.assertEqual(query["code_challenge_method"], ["S256"])
        verifier = _cipher(callback, creds).decrypt(query["state"][0].encode(), ttl=600).decode()
        expected = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        self.assertEqual(query["code_challenge"][0], expected)
        with self.assertRaises(InvalidToken):
            _cipher(callback, {**creds, "client_secret": "another-secret"}).decrypt(query["state"][0].encode())
        with self.assertRaises(InvalidToken):
            _cipher("https://another.example/callback", creds).decrypt(query["state"][0].encode())
        self.assertFalse(_validate_callback("http://evil.example/callback"))
        self.assertFalse(_validate_callback("https://evil.example/callback?token=1"))

    def test_oauth_callback_rejects_invalid_state_without_network(self):
        from provider.kontocsv import KontoCsvProvider, ToolProviderOAuthError
        p = KontoCsvProvider.__new__(KontoCsvProvider)
        creds = {"client_id": "test-client", "client_secret": "not-a-real-secret"}
        req = SimpleNamespace(args={"code": "dummy-code", "state": "badstate"})
        with patch("provider.kontocsv.requests.post") as post:
            with self.assertRaises(ToolProviderOAuthError):
                p._oauth_get_credentials("https://cloud.dify.ai/callback", creds, req)
            post.assert_not_called()

    def test_refresh_token_rotation_fallback(self):
        from provider.kontocsv import KontoCsvProvider
        from dify_plugin.entities.oauth import ToolOAuthCredentials
        p = KontoCsvProvider.__new__(KontoCsvProvider)
        with patch("provider.kontocsv._exchange_token", return_value=ToolOAuthCredentials(
            credentials={"access_token": "new-access"}, expires_at=1_900_000_000
        )):
            updated = p._oauth_refresh_credentials("https://cloud.dify.ai/callback",
                     {"client_id": "x", "client_secret": "y"}, {"refresh_token": "old-refresh"})
        self.assertEqual(updated.credentials["refresh_token"], "old-refresh")


if __name__ == "__main__":
    unittest.main(verbosity=2)
