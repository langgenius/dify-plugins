from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetContributorsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        repo = tool_parameters["repo"].strip()
        headers = {"Accept": "application/vnd.github.v3+json"}

        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}/contributors",
                headers=headers,
                params={"per_page": 10},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: GitHub API timeout.")
            return
        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(f"GitHub API error: {e.response.status_code}")
            return

        contributors = []
        for c in data:
            contributors.append({
                "username": c.get("login"),
                "contributions": c.get("contributions"),
                "profile": c.get("html_url")
            })

        yield self.create_json_message({"contributors": contributors})
