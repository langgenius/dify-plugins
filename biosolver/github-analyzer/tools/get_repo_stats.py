from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetRepoStatsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        repo = tool_parameters["repo"].strip()
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            yield self.create_text_message("Error: GitHub API timeout.")
            return
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                yield self.create_text_message(f"Repository '{repo}' not found.")
            else:
                yield self.create_text_message(f"GitHub API error: {e.response.status_code}")
            return

        result = {
            "name": data.get("full_name"),
            "description": data.get("description"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "watchers": data.get("watchers_count"),
            "open_issues": data.get("open_issues_count"),
            "language": data.get("language"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "license": data.get("license", {}).get("name") if data.get("license") else None,
            "topics": data.get("topics", []),
            "url": data.get("html_url")
        }
        yield self.create_json_message(result)
