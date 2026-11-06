import hashlib
import importlib
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from tools._client import OdileDirectClient, OdileError


class ClientTests(unittest.TestCase):
    def test_envelope_and_headers(self):
        for key in (None, "test-key"):
            with self.subTest(key=key):
                requests = []
                client = OdileDirectClient(api_key=key, fetch=lambda req: (requests.append(req) or 200, b'{"result":{"content":[]}}'))
                client.call("find_business_agent", {"number": "+12345678"})
                req = requests[0]
                self.assertEqual(req.full_url, "https://odilelabs.com/mcp/direct")
                self.assertEqual(req.get_method(), "POST")
                self.assertEqual(req.get_header("Content-type"), "application/json")
                self.assertEqual(req.get_header("Accept"), "application/json, text/event-stream")
                self.assertEqual(req.get_header("Authorization"), "Bearer test-key" if key else None)
                self.assertEqual(json.loads(req.data), {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "find_business_agent", "arguments": {"number": "+12345678"}}})

    def test_response_content(self):
        cases = [
            ({"result": {"structuredContent": {"status": "ok"}, "content": [{"type": "text", "text": "ignored"}]}}, {"status": "ok"}),
            ({"result": {"content": [{"type": "text", "text": '{"x":1}'}]}}, {"x": 1}),
            ({"result": {"content": [{"type": "text", "text": "plain"}, {"type": "text", "text": "text"}]}}, "plain\ntext"),
        ]
        for response, expected in cases:
            with self.subTest(response=response):
                client = OdileDirectClient(fetch=lambda req: (200, json.dumps(response).encode()))
                self.assertEqual(client.call("x", {}), expected)

    def test_errors(self):
        for status, body, code, message in [(200, b'{"error":{"code":-1,"message":"bad"}}', -1, 'bad'), (403, b'{"error":{"message":"denied"}}', 403, 'denied'), (502, b'bad gateway', 502, 'bad gateway')]:
            with self.subTest(status=status), self.assertRaises(OdileError) as error:
                OdileDirectClient(fetch=lambda req: (status, body)).call("x", {})
            self.assertEqual(error.exception.code, code)
            self.assertEqual(error.exception.message, message)


REQUIRED = {
    "find_business_agent": {"number"},
    "send_to_business": {"biz", "skill", "data"},
    "get_replies": {"thread_id"},
    "reply_to_business": {"thread_id", "text"},
    "call_business": {"number", "business_name", "caller_name", "callback_number", "need", "on_behalf_consent", "message_id"},
    "get_call_result": {"task_id"},
    "answer_call_question": {"task_id", "answer"},
    "get_direct_usage": set(),
    "get_direct_payment": {"biz", "task_id"},
    "get_m2m_network": set(),
}


# Minimal runtime stand-in: tests exercise the real tool modules without Dify.
class Tool:
    def create_json_message(self, value):
        return ("json", value)

    def create_text_message(self, value):
        return ("text", value)

sdk = types.ModuleType("dify_plugin")
sdk.Tool = Tool
sdk.ToolProvider = type("ToolProvider", (), {})
errors = types.ModuleType("dify_plugin.errors")
error_tool = types.ModuleType("dify_plugin.errors.tool")
error_tool.ToolProviderCredentialValidationError = type("ToolProviderCredentialValidationError", (Exception,), {})
sys.modules.setdefault("dify_plugin", sdk)
sys.modules.setdefault("dify_plugin.errors", errors)
sys.modules.setdefault("dify_plugin.errors.tool", error_tool)


class ToolTests(unittest.TestCase):
    def test_tool_modules_have_one_dify_subclass(self):
        for name in REQUIRED:
            with self.subTest(name=name):
                module = importlib.import_module(f"tools.{name}")
                classes = [value for value in vars(module).values() if isinstance(value, type) and value is not Tool and issubclass(value, Tool)]
                self.assertEqual(len(classes), 1)

    def test_definitions_match_required_parameters(self):
        for name, required in REQUIRED.items():
            with self.subTest(name=name):
                definition = json.loads(Path(f"tools/{name}.yaml").read_text())
                self.assertEqual({p["name"] for p in definition["parameters"] if p["required"]}, required)
                self.assertEqual(definition["extra"]["python"]["source"], f"tools/{name}.py")

    def invoke(self, name, parameters):
        module = importlib.import_module(f"tools.{name}")
        cls = getattr(module, ''.join(part.title() for part in name.split('_')) + 'Tool')
        instance = cls()
        instance.runtime = types.SimpleNamespace(credentials={"api_key": "key"})
        with patch("tools._tool.OdileDirectClient") as client:
            client.return_value.call.return_value = {"state": "received"}
            messages = list(instance._invoke(parameters))
            client.assert_called_once_with(api_key="key")
            call = client.return_value.call.call_args.args
        self.assertEqual(messages, [("json", {"state": "received"}), ("text", "Odile Direct response received. Check the result for its status.")])
        return call

    def test_all_tools_invoke_server_name_and_drop_empty_optional(self):
        for name in REQUIRED:
            with self.subTest(name=name):
                params = {"optional_empty": "", "optional_none": None, "keep_false": False, "keep_zero": 0}
                if name == "send_to_business":
                    params.update(biz="x", skill="take_message", data='{"need":"help"}')
                called_name, arguments = self.invoke(name, params)
                self.assertEqual(called_name, name)
                self.assertNotIn("optional_empty", arguments)
                self.assertNotIn("optional_none", arguments)
                self.assertIs(arguments["keep_false"], False)
                self.assertEqual(arguments["keep_zero"], 0)

    def test_message_id_is_stable_and_can_be_supplied(self):
        params = {"biz": "b", "skill": "book", "data": '{"z":2,"a":1}'}
        _, arguments = self.invoke("send_to_business", params)
        expected = hashlib.sha256(('bbook' + json.dumps({"a": 1, "z": 2}, sort_keys=True)).encode()).hexdigest()[:40]
        self.assertEqual(arguments["message_id"], expected)
        _, second = self.invoke("send_to_business", {**params, "data": '{"a":1,"z":2}'})
        self.assertEqual(second["message_id"], expected)
        _, explicit = self.invoke("send_to_business", {**params, "message_id": "new-request"})
        self.assertEqual(explicit["message_id"], "new-request")

    def test_json_fields(self):
        _, args = self.invoke("call_business", {"questions": '["Open?"]'})
        self.assertEqual(args["questions"], ["Open?"])
        with self.assertRaises(ValueError):
            self.invoke("send_to_business", {"biz": "b", "skill": "book", "data": "[]"})

    def test_provider_uses_anonymous_network_check(self):
        provider = importlib.import_module("provider.odile").OdileProvider()
        with patch("provider.odile.OdileDirectClient") as client:
            provider._validate_credentials({"api_key": ""})
            client.assert_called_once_with()
            client.return_value.call.assert_called_once_with("get_m2m_network", {})
