import sys, types, json
from unittest.mock import patch, MagicMock

# Stub dify_plugin so tools can be imported without the real package
dify_stub = types.ModuleType("dify_plugin")

class _Tool:
    class runtime:
        credentials = {}
    def create_text_message(self, text): return MagicMock(message=text)

class _Provider:
    pass

entities_stub = types.ModuleType("dify_plugin.entities")
tool_stub = types.ModuleType("dify_plugin.entities.tool")
tool_stub.ToolInvokeMessage = MagicMock

errors_stub = types.ModuleType("dify_plugin.errors")
tool_errors_stub = types.ModuleType("dify_plugin.errors.tool")
tool_errors_stub.ToolProviderCredentialValidationError = Exception

dify_stub.Tool = _Tool
dify_stub.ToolProvider = _Provider

sys.modules["dify_plugin"] = dify_stub
sys.modules["dify_plugin.entities"] = entities_stub
sys.modules["dify_plugin.entities.tool"] = tool_stub
sys.modules["dify_plugin.errors"] = errors_stub
sys.modules["dify_plugin.errors.tool"] = tool_errors_stub

# Now import the tools (they live in sdk/dify/tools/)
import importlib.util, os

def load_tool(name):
    path = os.path.join(os.path.dirname(__file__), "..", "tools", f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_remember_tool():
    mod = load_tool("remember")
    tool = mod.RememberTool()
    tool.runtime = MagicMock()
    tool.runtime.credentials = {"api_key": "kv-test", "base_url": "https://api.kronvex.io"}
    tool.create_text_message = lambda text: MagicMock(message=text)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": "mem-1", "content": "hello"}
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_resp):
        results = list(tool._invoke({"agent_id": "a1", "content": "hello"}))
    assert len(results) == 1
    assert "mem-1" in results[0].message


def test_recall_tool():
    mod = load_tool("recall")
    tool = mod.RecallTool()
    tool.runtime = MagicMock()
    tool.runtime.credentials = {"api_key": "kv-test", "base_url": "https://api.kronvex.io"}
    tool.create_text_message = lambda text: MagicMock(message=text)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"memories": [{"id": "m1", "content": "hello"}]}
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_resp):
        results = list(tool._invoke({"agent_id": "a1", "query": "hello"}))
    assert len(results) == 1
    assert "m1" in results[0].message


def test_inject_context_tool():
    mod = load_tool("inject_context")
    tool = mod.InjectContextTool()
    tool.runtime = MagicMock()
    tool.runtime.credentials = {"api_key": "kv-test", "base_url": "https://api.kronvex.io"}
    tool.create_text_message = lambda text: MagicMock(message=text)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"context_block": "You remember: hello"}
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_resp):
        results = list(tool._invoke({"agent_id": "a1", "message": "hello"}))
    assert len(results) == 1
    assert "remember" in results[0].message
