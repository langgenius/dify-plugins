
import sys
import unittest
from unittest.mock import MagicMock, patch
import json
import types

# 1. Define a Mock Tool class that mimics the behavior we need
class MockTool:
    def __init__(self, runtime):
        self.runtime = runtime
    
    def create_text_message(self, text):
        return {"type": "text", "text": text}
        
    def create_json_message(self, json_data):
        return {"type": "json", "json": json_data}
        
    def _invoke(self, params):
        pass

# 2. Register this class in sys.modules so imports work
dify_plugin = types.ModuleType("dify_plugin")
dify_plugin.Tool = MockTool
dify_plugin.entities = types.ModuleType("dify_plugin.entities")
dify_plugin.entities.tool = types.ModuleType("dify_plugin.entities.tool")
dify_plugin.entities.tool.ToolInvokeMessage = dict # Mock type

sys.modules['dify_plugin'] = dify_plugin
sys.modules['dify_plugin.entities'] = dify_plugin.entities
sys.modules['dify_plugin.entities.tool'] = dify_plugin.entities.tool

# 3. Import the tool logic
import importlib.util
spec = importlib.util.spec_from_file_location("linkedin_tool", "tools/linkedin.py")
linkedin_module = importlib.util.module_from_spec(spec)
# We must execute the module so the class is defined
spec.loader.exec_module(linkedin_module)

class TestLinkedinTool(unittest.TestCase):
    def setUp(self):
        # Create a mock runtime with credentials
        self.mock_runtime = MagicMock()
        self.mock_runtime.credentials = {"access_token": "fake_token"}
        
        # Instantiate the tool
        self.tool = linkedin_module.LinkedinTool(self.mock_runtime)

    @patch('requests.get')
    @patch('requests.post')
    def test_invoke_success(self, mock_post, mock_get):
        # Mock Profile Response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": "test_urn"}
        # Mock Post Response
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": "urn:li:share:123"}

        params = {"content": "Hello LinkedIn", "visibility": "PUBLIC"}
        
        # Execute
        generator = self.tool._invoke(params)
        result = next(generator) # Should be a dict (our mock message)

        # Assertions
        # Check payload
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['specificContent']['com.linkedin.ugc.ShareContent']['shareCommentary']['text'], "Hello LinkedIn")
        self.assertEqual(kwargs['json']['visibility']['com.linkedin.ugc.MemberNetworkVisibility'], "PUBLIC")
        
        # Check result
        self.assertEqual(result['type'], "json")
        self.assertIn("urn:li:share:123", result['json']['url'])
        print("\nSUCCESS: test_invoke_success passed")

    @patch('requests.get')
    def test_invoke_no_token(self, mock_get):
        self.tool.runtime.credentials = {} # Empty
        
        try:
             generator = self.tool._invoke({"content": "fail"})
             next(generator)
        except ValueError as e:
            self.assertIn("Access Token is missing", str(e))
            print("\nSUCCESS: test_invoke_no_token passed")

    @patch('requests.get')
    def test_invoke_dict_runtime(self, mock_get):
        # Mock Profile Response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": "test_urn"}

        # Use a dict for runtime instead of MagicMock
        self.tool.runtime = {"credentials": {"access_token": "dict_token"}}
        
        params = {"content": "Hello LinkedIn"}
        generator = self.tool._invoke(params)
        # It will fail at requests.post call if we don't mock it, but we just want to see it pass the credentials check
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {"id": "123"}
            result = next(generator)
            self.assertEqual(result['type'], "json")
        print("\nSUCCESS: test_invoke_dict_runtime passed")

if __name__ == '__main__':
    # Print header
    print("Running Linkedin Plugin Logic Tests...")
    unittest.main()
