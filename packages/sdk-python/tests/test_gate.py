import unittest
from unittest.mock import patch, MagicMock
from suprawall.gate import _evaluate, SupraWallOptions, SupraWallConnectionError

class TestSupraWallGate(unittest.TestCase):
    def setUp(self):
        self.options = SupraWallOptions(api_key="sw_test_123")

    def test_evaluate_test_mode_bypass(self):
        # Should return ALLOW without calling network
        result = _evaluate("test_tool", {}, self.options)
        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(result["reason"], "Test mode bypass")

    @patch("httpx.Client.post")
    def test_evaluate_real_key_success(self, mock_post):
        self.options.api_key = "sw_real_key"
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"decision": "ALLOW", "estimated_cost_usd": 0.001}
        mock_post.return_value = mock_resp

        result = _evaluate("test_tool", {}, self.options)
        self.assertEqual(result["decision"], "ALLOW")

    @patch("httpx.Client.post")
    def test_evaluate_retry_logic(self, mock_post):
        self.options.api_key = "sw_real_key"
        
        # Mock 500 then 200
        mock_resp_fail = MagicMock()
        mock_resp_fail.status_code = 500
        
        mock_resp_success = MagicMock()
        mock_resp_success.status_code = 200
        mock_resp_success.json.return_value = {"decision": "ALLOW"}
        
        mock_post.side_effect = [mock_resp_fail, mock_resp_success]

        # Should succeed after 1 retry
        result = _evaluate("test_tool", {}, self.options)
        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(mock_post.call_count, 2)

if __name__ == "__main__":
    unittest.main()
