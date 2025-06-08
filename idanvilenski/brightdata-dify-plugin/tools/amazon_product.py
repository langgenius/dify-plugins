from collections.abc import Generator
from typing import Any
import requests
import json
import time
from urllib.parse import urlparse
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class AmazonProductTool(Tool):
    """Real Bright Data web_data_amazon_product tool - fixed polling logic."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            api_token = self.runtime.credentials["api_token"]
        except KeyError:
            raise Exception("Bright Data API token is required.")

        amazon_url = tool_parameters.get("amazon_url", "").strip()
        
        if not amazon_url:
            raise Exception("Amazon product URL cannot be empty.")

        if not self._is_valid_amazon_url(amazon_url):
            raise Exception("Invalid Amazon URL. Must contain /dp/ or /gp/product/")

        try:
            product_data = self._web_data_amazon_product(amazon_url, api_token)
            yield self.create_text_message(product_data)
        except Exception as e:
            raise Exception(f"Amazon scraping failed: {str(e)}")

    def _web_data_amazon_product(self, url: str, api_token: str) -> str:
        """Use exact same API call as Bright Data MCP server for web_data_amazon_product"""
        
        headers = {
            'user-agent': 'dify-plugin/1.0.0',
            'authorization': f'Bearer {api_token}',
        }
        
        # Dataset ID from MCP server code
        dataset_id = 'gd_l7q7dkf244hwjntr0'
        
        # Step 1: Trigger data collection (exact same as MCP server)
        trigger_payload = [{'url': url}]
        
        try:
            trigger_response = requests.post(
                'https://api.brightdata.com/datasets/v3/trigger',
                params={'dataset_id': dataset_id, 'include_errors': True},
                json=trigger_payload,
                headers=headers,
                timeout=30
            )
            
            if trigger_response.status_code != 200:
                raise Exception(f"Trigger API error {trigger_response.status_code}: {trigger_response.text}")
            
            trigger_data = trigger_response.json()
            if not trigger_data.get('snapshot_id'):
                raise Exception('No snapshot ID returned from request')
            
            snapshot_id = trigger_data['snapshot_id']
            
            # Step 2: Poll for results (FIXED - exactly like MCP server)
            max_attempts = 600  # Same as MCP server
            attempts = 0
            
            while attempts < max_attempts:
                try:
                    snapshot_response = requests.get(
                        f'https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}',
                        params={'format': 'json'},
                        headers=headers,
                        timeout=30
                    )
                    
                    # FIX: Handle 202 responses properly (this is normal during polling!)
                    if snapshot_response.status_code == 202:
                        # 202 means "still processing" - continue polling
                        attempts += 1
                        time.sleep(1)
                        continue
                    
                    if snapshot_response.status_code != 200:
                        raise Exception(f"Snapshot API error {snapshot_response.status_code}: {snapshot_response.text}")
                    
                    snapshot_data = snapshot_response.json()
                    
                    # FIX: Only continue polling if status is 'running', otherwise we have data
                    if snapshot_data.get('status') == 'running':
                        attempts += 1
                        time.sleep(1)  # Wait 1 second like MCP server
                        continue
                    
                    # Data is ready, format and return
                    return self._format_amazon_data(snapshot_data, url)
                    
                except requests.exceptions.RequestException as e:
                    attempts += 1
                    time.sleep(1)
                    if attempts >= max_attempts:
                        raise Exception(f"Request failed after {max_attempts} attempts: {str(e)}")
            
            raise Exception(f"Timeout after {max_attempts} seconds waiting for data")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def _format_amazon_data(self, data: dict, url: str) -> str:
        """Format the structured Amazon data returned by Bright Data API"""
        
        # Return the raw JSON data as formatted string (same as MCP server)
        return json.dumps(data, indent=2)

    def _is_valid_amazon_url(self, url: str) -> bool:
        """Validate if URL is a valid Amazon product URL"""
        try:
            parsed = urlparse(url)
            return 'amazon.' in parsed.netloc and ('/dp/' in parsed.path or '/gp/product/' in parsed.path)
        except:
            return False
