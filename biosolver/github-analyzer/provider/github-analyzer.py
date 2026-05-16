from typing import Any
from dify_plugin import ToolProvider
import requests


class GitHubAnalyzerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        token = credentials.get("github_token", "")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"
        response = requests.get(
            "https://api.github.com/repos/langgenius/dify",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
