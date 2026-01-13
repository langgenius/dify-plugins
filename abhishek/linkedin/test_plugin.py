
import sys
import unittest
from unittest.mock import MagicMock, patch
import json

# Mock dify_plugin modules before importing the tool
sys.modules['dify_plugin'] = MagicMock()
sys.modules['dify_plugin.entities.tool'] = MagicMock()

# Now we can import the tool, but we need to patch the parent class if it's imported from dify_plugin
# Since we mocked the module, Tool is a MagicMock. 
# We need to define our own base class or let the import happen if parameters are simple.

# Use a trick to allow the import but replace the base class
from dify_plugin import Tool

# We need to import the actual file content to test it. 
# Since the file is at tools/linkedin.py, we can load it.
import importlib.util
import os

spec = importlib.util.spec_from_file_location("linkedin_tool", "tools/linkedin.py")
linkedin_module = importlib.util.module_from_spec(spec)
sys.modules["linkedin_tool"] = linkedin_module
spec.loader.exec_module(linkedin_module)

class TestLinkedinTool(unittest.TestCase):
    def setUp(self):
        self.tool = linkedin_module.LinkedinTool(None) # Assuming __init__ can handle None or we mock it
        # Mock runtime and credentials
        self.tool.runtime = MagicMock()
        self.tool.runtime.credentials = {"access_token": "fake_token"}
        # Mock create_text_message and create_json_message
        self.tool.create_text_message = MagicMock(side_effect=lambda x: {"type": "text", "text": x})
        self.tool.create_json_message = MagicMock(side_effect=lambda x: {"type": "json", "json": x})

    @patch('requests.get')
    @patch('requests.post')
    def test_invoke_success(self, mock_post, mock_get):
        # Mock Profile Response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": "test_urn"}

        # Mock Post Response
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": "urn:li:share:123"}

        # Params
        params = {"content": "Hello LinkedIn", "visibility": "PUBLIC"}

        # Run invoke
        generator = self.tool._invoke(params)
        result = next(generator)

        # Assertions
        # 1. Check Profile Call
        mock_get.assert_called_with(
            "https://api.linkedin.com/v2/me",
            headers={"Authorization": "Bearer fake_token", "X-Restli-Protocol-Version": "2.0.0"}
        )

        # 2. Check Post Call
        expected_payload = {
            "author": "urn:li:person:test_urn",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": "Hello LinkedIn"},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        mock_post.assert_called_with(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={"Authorization": "Bearer fake_token", "X-Restli-Protocol-Version": "2.0.0"},
            json=expected_payload
        )

        # 3. Check Result
        self.assertEqual(result['type'], 'json')
        self.assertIn('url', result['json'])
        self.assertIn('https://www.linkedin.com/feed/update/urn:li:share:123', result['json']['url'])
        print("Test Success: Logic verified.")

    @patch('requests.get')
    def test_invoke_no_profile(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {} # No ID

        params = {"content": "Test"}
        generator = self.tool._invoke(params)
        result = next(generator)

        self.assertEqual(result['type'], 'text')
        self.assertIn('Failed to retrieve User ID', result['text'])
        print("Test Success: Missing profile handled.")

if __name__ == '__main__':
    unittest.main()
