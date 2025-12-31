from dify_plugin import ToolProvider


class SemanticScholarProvider(ToolProvider):
    def validate_credentials(self, credentials: dict) -> None:
        """
        Validate the API key by making a test request
        """
        import requests
        
        api_key = credentials.get("api_key", "")
        if not api_key:
            raise Exception("API key is required")
        
        # Test the API key with a simple search
        try:
            response = requests.get(
                "https://ai4scholar.net/graph/v1/paper/search",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"query": "test", "limit": 1},
                timeout=10
            )
            
            if response.status_code == 401:
                raise Exception("Invalid API key")
            elif response.status_code == 402:
                raise Exception("Insufficient credits. Please recharge at ai4scholar.net")
            elif response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise Exception("API request timeout")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
