import json
import socket
from pathlib import Path

from dify_plugin import DifyPluginEnv
import httpx
import pytest
import yaml
from dify_plugin.core.plugin_registration import PluginRegistration
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from lib.client import SentFromAIClient, SentFromAIError
from lib.operations import execute
from provider.sentfromai import SentFromAIProvider

ROOT = Path(__file__).resolve().parents[1]
ID = "11111111-1111-4111-8111-111111111111"
KEY = "test-key-only-not-a-real-credential"
SEND = {"inbox_id": ID, "to": "recipient@example.com", "subject": "Synthetic test",
        "text": "Synthetic message", "client_id": "workflow-event-1:send"}


@pytest.fixture(autouse=True)
def deny_real_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Unit tests must use MockTransport, never real network calls")
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def mock_api(response=None, status=200, headers=None):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(status, json=response if response is not None else {"id": ID}, headers=headers)
    return SentFromAIClient(KEY, transport=httpx.MockTransport(handler)), calls


@pytest.mark.parametrize("name,parameters,method,path,expected", [
    ("get_account", {}, "GET", "/v1/account", None),
    ("list_inboxes", {}, "GET", "/v1/inboxes", None),
    ("create_inbox", {"local_part": "Test", "display_name": "QA", "domain_id": ID}, "POST", "/v1/inboxes", {"local_part": "test", "display_name": "QA", "domain_id": ID}),
    ("list_messages", {"query": "invoice & update", "inbox_id": ID, "mode": "hybrid", "limit": 10}, "GET", "/v1/messages", None),
    ("get_message", {"message_id": ID}, "GET", f"/v1/messages/{ID}", None),
    ("send_message", SEND, "POST", "/v1/messages", {**SEND, "to": ["recipient@example.com"], "cc": [], "bcc": []}),
    ("reply_to_message", {"message_id": ID, "text": "Reply", "client_id": "event:reply"}, "POST", f"/v1/messages/{ID}/reply", {"text": "Reply", "client_id": "event:reply", "reply_all": False}),
    ("create_draft", {"inbox_id": ID, "text": "Review first", "reply_to_message_id": ID}, "POST", "/v1/drafts", {"inbox_id": ID, "text": "Review first", "reply_to_message_id": ID, "to": [], "cc": [], "bcc": []}),
    ("get_draft", {"draft_id": ID}, "GET", f"/v1/drafts/{ID}", None),
])
def test_routes_and_payloads(name, parameters, method, path, expected):
    api, calls = mock_api()
    assert execute(name, parameters, api) == {"id": ID}
    assert len(calls) == 1
    req = calls[0]
    assert req.method == method and req.url.path == path
    assert req.url.scheme == "https" and req.url.host == "api.sentfrom.ai"
    assert req.headers["Authorization"] == f"Bearer {KEY}"
    if expected is not None:
        assert json.loads(req.content) == expected
    if name == "list_messages":
        assert req.url.params["query"] == parameters["query"]
        assert req.url.params["mode"] == "hybrid"
        assert req.url.params["limit"] == "10"


def test_default_search_and_server_fallback_are_preserved():
    api, calls = mock_api({"mode_used": "keyword", "messages": []})
    assert execute("list_messages", {}, api)["mode_used"] == "keyword"
    assert dict(calls[0].url.params) == {"mode": "keyword", "limit": "25"}


def test_addresses_body_and_reply_all():
    api, calls = mock_api()
    execute("send_message", {**SEND, "to": '["a@example.com", "b@example.com"]',
                            "cc": "c@example.com\nd@example.com", "bcc": "e@example.com", "html": "<p>Hello</p>"}, api)
    body = json.loads(calls[0].content)
    assert body["to"] == ["a@example.com", "b@example.com"]
    assert body["cc"] == ["c@example.com", "d@example.com"]
    assert body["bcc"] == ["e@example.com"] and body["html"] == "<p>Hello</p>"
    execute("reply_to_message", {"message_id": ID, "html": "<p>Reply</p>", "reply_all": True, "client_id": "reply-1"}, api)
    assert json.loads(calls[1].content)["reply_all"] is True


@pytest.mark.parametrize("name,p", [
    ("get_account", {"base_url": "https://evil.example"}),
    ("get_message", {"message_id": "../account"}),
    ("get_message", {"message_id": "https://evil.example"}),
    ("get_draft", {"draft_id": ID + "/send"}),
    ("list_messages", {"limit": 101}), ("list_messages", {"limit": 0}),
    ("list_messages", {"limit": 1.5}), ("list_messages", {"limit": True}),
    ("list_messages", {"limit": "10"}), ("list_messages", {"mode": "arbitrary"}),
    ("create_inbox", {"local_part": "bad@domain"}),
    ("create_inbox", {"local_part": "test", "domain_id": "not-a-uuid"}),
    ("send_message", {**SEND, "client_id": ""}),
    ("send_message", {**SEND, "client_id": "é" * 128}),
    ("send_message", {**SEND, "to": '[]'}),
    ("send_message", {**SEND, "to": '[123]'}),
    ("send_message", {**SEND, "to": '["a@example.com"'}),
    ("send_message", {**SEND, "to": 'Name <a@example.com>'}),
    ("send_message", {**SEND, "to": 'a@example.com\rbcc:secret@example.com'}),
    ("send_message", {**SEND, "to": ','.join(f"person{i}@example.com" for i in range(11))}),
    ("send_message", {**SEND, "text": None}),
    ("send_message", {**SEND, "text": "x" * 1_000_001}),
    ("send_message", {**SEND, "subject": "subject\nBcc:bad@example.com"}),
    ("reply_to_message", {"message_id": ID, "text": "hello", "reply_all": "false", "client_id": "id"}),
    ("create_draft", {"inbox_id": ID, "text": "never schedule", "scheduled_at": "2030-01-01T00:00:00Z"}),
    ("create_draft", {"inbox_id": ID, "text": "no uploads", "attachments": []}),
])
def test_invalid_inputs_never_reach_network(name, p):
    api, calls = mock_api()
    with pytest.raises(SentFromAIError):
        execute(name, p, api)
    assert calls == []


@pytest.mark.parametrize("key", [None, "", " ", "bad\nkey", "bad\x00key", "非ascii"])
def test_invalid_key_is_redacted(key):
    with pytest.raises(SentFromAIError, match="provider credentials"):
        SentFromAIClient(key)


@pytest.mark.parametrize("status", [400, 401, 402, 403, 404, 409, 410, 413, 429, 500, 503])
def test_no_retries_or_error_content_leaks(status):
    secret = "private-email-content-" + KEY
    api, calls = mock_api({"error": secret, "message": secret}, status, {"Retry-After": "60"})
    with pytest.raises(SentFromAIError) as error:
        execute("send_message", SEND, api)
    assert secret not in str(error.value) and KEY not in str(error.value)
    assert f"HTTP {status}" in str(error.value) and len(calls) == 1
    if status == 429:
        assert "60 seconds" in str(error.value)


def test_known_pending_error_prevents_blind_retry():
    api, calls = mock_api({"error": "send_outcome_pending"}, 409)
    with pytest.raises(SentFromAIError, match="original client_id") as error:
        execute("send_message", SEND, api)
    assert "send_outcome_pending" in str(error.value) and len(calls) == 1


def test_timeout_is_sanitized_and_write_outcome_is_uncertain():
    calls = []
    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("secret content " + KEY, request=request)
    api = SentFromAIClient(KEY, transport=httpx.MockTransport(handler))
    with pytest.raises(SentFromAIError, match="may already have completed") as error:
        execute("send_message", SEND, api)
    assert KEY not in str(error.value) and len(calls) == 1


@pytest.mark.parametrize("status", [301, 302, 307, 308])
def test_redirect_never_forwards_authorization(status):
    api, calls = mock_api({}, status, {"Location": "https://evil.example/steal"})
    with pytest.raises(SentFromAIError, match="not followed"):
        execute("get_account", {}, api)
    assert len(calls) == 1 and calls[0].url.host == "api.sentfrom.ai"


@pytest.mark.parametrize("method,path", [("GET", "https://evil.example"), ("GET", "//evil.example"),
                                         ("POST", "/v1/account/claim-link"), ("DELETE", "/v1/inboxes"),
                                         ("POST", f"/v1/drafts/{ID}/send")])
def test_client_route_allowlist(method, path):
    api, calls = mock_api()
    with pytest.raises(SentFromAIError, match="Unsupported"):
        api.request(method, path)
    assert not calls


def test_oversized_and_non_json_responses(monkeypatch):
    monkeypatch.setattr("lib.client.MAX_RESPONSE_BYTES", 64)
    api, _ = mock_api({"body": "x" * 100})
    with pytest.raises(SentFromAIError, match="8 MiB"):
        execute("get_account", {}, api)
    api = SentFromAIClient(KEY, transport=httpx.MockTransport(lambda r: httpx.Response(200, text="<html>secret</html>")))
    with pytest.raises(SentFromAIError, match="invalid JSON"):
        execute("get_account", {}, api)


def test_tls_timeout_and_environment_proxy_configuration(monkeypatch):
    original, options = httpx.Client, []
    def capture(**kwargs):
        options.append(kwargs)
        return original(**kwargs)
    monkeypatch.setattr("lib.client.httpx.Client", capture)
    api, _ = mock_api()
    execute("get_account", {}, api)
    assert options[0]["verify"] is True
    assert options[0]["trust_env"] is False and options[0]["follow_redirects"] is False
    assert options[0]["timeout"].read == 30 and options[0]["timeout"].connect == 10


def test_provider_validation_only_reads_account(monkeypatch):
    api, calls = mock_api({"capabilities": {"send": False}})
    monkeypatch.setattr("provider.sentfromai.SentFromAIClient", lambda key: api)
    SentFromAIProvider()._validate_credentials({"api_key": KEY})
    assert [(r.method, r.url.path) for r in calls] == [("GET", "/v1/account")]
    api, _ = mock_api({"error": KEY}, 401)
    with pytest.raises(ToolProviderCredentialValidationError) as error:
        SentFromAIProvider()._validate_credentials({"api_key": KEY})
    assert KEY not in str(error.value)


def test_real_sdk_loads_manifest_and_invokes_every_tool(monkeypatch):
    monkeypatch.chdir(ROOT)
    registration = PluginRegistration(DifyPluginEnv())
    _, _, tools = registration.tools_mapping["sentfromai"]
    from lib.operations import FIELDS
    assert set(tools) == set(FIELDS)
    for name, (configuration, tool_class) in tools.items():
        assert {p.name for p in configuration.parameters} == FIELDS[name]
        # SDK loads from source into a separate module, not sys.modules.
        monkeypatch.setitem(tool_class._invoke.__globals__, "execute", lambda *args: {"id": ID})
        outputs = list(tool_class.from_credentials({"api_key": KEY}).invoke({}))
        assert outputs[0].message.json_object == {"id": ID}
        assert outputs[1].message.variable_name == "result"
        assert outputs[1].message.variable_value == {"id": ID}
    manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text())
    assert manifest["resource"]["permission"] == {}
    assert manifest["verified"] is False
