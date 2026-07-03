"""Unit tests for the Dakera Memory plugin tools + provider.

Run: pip install dify_plugin requests pytest && pytest -q
"""
from conftest import msgtext

from provider.dakera import DakeraProvider
from tools.forget import DakeraForgetTool
from tools.get import DakeraGetTool
from tools.recall import DakeraRecallTool
from tools.search import DakeraSearchTool
from tools.store import DakeraStoreTool
from tools.update import DakeraUpdateTool


def test_provider_validates_healthy_server(creds):
    # Should not raise against a server returning 200 on /health/live.
    DakeraProvider().validate_credentials(credentials=creds)


def test_store_posts_full_body_with_auth(mock_server, creds):
    _, received = mock_server
    msgs = list(DakeraStoreTool.from_credentials(creds).invoke(
        {"content": "Alice prefers Rust over Python.", "agent_id": "acct-42",
         "importance": 0.9, "tags": "preference, lang"}))
    method, path, body, headers = received[-1]
    assert (method, path) == ("POST", "/v1/memory/store")
    assert body["content"] == "Alice prefers Rust over Python."
    assert body["agent_id"] == "acct-42"
    assert body["importance"] == 0.9
    assert body["tags"] == ["preference", "lang"]
    assert headers.get("Authorization") == "Bearer dk-test"
    assert "mem_abc123" in msgtext(msgs)


def test_store_clamps_importance(mock_server, creds):
    _, received = mock_server
    list(DakeraStoreTool.from_credentials(creds).invoke(
        {"content": "x", "importance": 5}))
    assert received[-1][2]["importance"] == 1.0


def test_recall_clamps_top_k_and_surfaces_ids(mock_server, creds):
    _, received = mock_server
    msgs = list(DakeraRecallTool.from_credentials(creds).invoke(
        {"query": "what language does Alice like?", "agent_id": "acct-42", "top_k": 50}))
    assert received[-1][1] == "/v1/memory/recall"
    assert received[-1][2]["top_k"] == 20
    text = msgtext(msgs)
    assert "Alice prefers Rust" in text
    assert "mem_1" in text  # id surfaced so it can be chained into get/update/forget


def test_search_filters_and_clamps(mock_server, creds):
    _, received = mock_server
    msgs = list(DakeraSearchTool.from_credentials(creds).invoke(
        {"agent_id": "acct-42", "query": "rust", "tags": "preference", "min_importance": 0.5, "top_k": 99}))
    body = received[-1][2]
    assert received[-1][1] == "/v1/memory/search"
    assert body["top_k"] == 50
    assert body["tags"] == ["preference"]
    assert body["min_importance"] == 0.5
    assert "Matched 1" in msgtext(msgs)
    assert "id: mem_1" in msgtext(msgs)


def test_get_uses_path_and_query(mock_server, creds):
    _, received = mock_server
    msgs = list(DakeraGetTool.from_credentials(creds).invoke({"memory_id": "mem_1", "agent_id": "acct-42"}))
    method, path, _, query = received[-1]
    assert method == "GET"
    assert path == "/v1/memory/get/mem_1"
    assert query.get("agent_id") == ["acct-42"]
    assert "Alice prefers Rust" in msgtext(msgs)


def test_update_puts_changed_fields(mock_server, creds):
    _, received = mock_server
    list(DakeraUpdateTool.from_credentials(creds).invoke(
        {"memory_id": "mem_1", "agent_id": "acct-42", "importance": 1.0, "tags": "pref,lang"}))
    method, path, body, query = received[-1]
    assert method == "PUT"
    assert path == "/v1/memory/update/mem_1"
    assert body["importance"] == 1.0
    assert body["tags"] == ["pref", "lang"]
    assert query.get("agent_id") == ["acct-42"]


def test_update_noop_guard_makes_no_request(mock_server, creds):
    _, received = mock_server
    before = len(received)
    msgs = list(DakeraUpdateTool.from_credentials(creds).invoke({"memory_id": "mem_1"}))
    assert len(received) == before
    assert "Nothing to update" in msgtext(msgs)


def test_forget_with_selector_reports_count(mock_server, creds):
    _, received = mock_server
    msgs = list(DakeraForgetTool.from_credentials(creds).invoke({"agent_id": "acct-42", "tags": "preference"}))
    assert received[-1][1] == "/v1/memory/forget"
    assert received[-1][2]["tags"] == ["preference"]
    assert "Deleted 2" in msgtext(msgs)


def test_forget_refuses_unscoped_mass_delete(mock_server, creds):
    _, received = mock_server
    before = len(received)
    msgs = list(DakeraForgetTool.from_credentials(creds).invoke({"agent_id": "acct-42"}))
    assert len(received) == before  # no HTTP call
    assert "Refusing" in msgtext(msgs)


def test_empty_inputs_make_no_request(mock_server, creds):
    _, received = mock_server
    before = len(received)
    list(DakeraStoreTool.from_credentials(creds).invoke({"content": "  "}))
    list(DakeraRecallTool.from_credentials(creds).invoke({"query": ""}))
    assert len(received) == before
