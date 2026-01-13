
import sys
import unittest
from typing import Mapping, Any
import urllib.parse

# Import provider
# We need to mock dify_plugin.ToolProvider for the import to work if not in full env
from unittest.mock import MagicMock
import types

dify_plugin = types.ModuleType("dify_plugin")
class MockToolProvider:
    def _validate_credentials(self, credentials): pass
dify_plugin.ToolProvider = MockToolProvider
dify_plugin.errors = types.ModuleType("dify_plugin.errors")
dify_plugin.errors.tool = types.ModuleType("dify_plugin.errors.tool")
dify_plugin.errors.tool.ToolProviderCredentialValidationError = Exception

sys.modules['dify_plugin'] = dify_plugin
sys.modules['dify_plugin.errors'] = dify_plugin.errors
sys.modules['dify_plugin.errors.tool'] = dify_plugin.errors.tool

# Now import the provider
import importlib.util
spec = importlib.util.spec_from_file_location("linkedin_provider", "provider/linkedin.py")
linkedin_provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(linkedin_provider)

class TestOAuthURL(unittest.TestCase):
    def test_url_generation(self):
        provider = linkedin_provider.LinkedinProvider()
        creds = {"client_id": "YOUR_CLIENT_ID", "client_secret": "YOUR_CLIENT_SECRET"}
        redirect_uri = "https://example.com/callback"
        
        url = provider._oauth_get_authorization_url(redirect_uri, creds)
        
        print(f"\nGenerated URL: {url}")
        
        # Parse and verify
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        self.assertEqual(params['client_id'][0], "YOUR_CLIENT_ID")
        self.assertEqual(params['redirect_uri'][0], redirect_uri)
        # Check scope encoding (should be %20 or + depending on implementation, but we used quote so %20)
        self.assertIn("w_member_social", params['scope'][0])
        print("Success: URL contains correct client_id and scopes.")

if __name__ == '__main__':
    unittest.main()
