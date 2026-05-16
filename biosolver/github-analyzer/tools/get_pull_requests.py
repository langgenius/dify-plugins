from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetPullRequestsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        repo = tool_parameters["repo"].strip()
        limit = int(tool_parameters.get("limit") or 10)
        limit = min(limit, 30)
        headers = {"Accept": "application/vnd.github.v3+json"}

        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}/pulls",
                headers=headers,
                params={"state": "open", "per_page": limit},
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

        prs = []
        for pr in data:
            prs.append({
                "number": pr.get("number"),
                "title": pr.get("title"),
                "author": pr.get("user", {}).get("login"),
                "created_at": pr.get("created_at"),
                "url": pr.get("html_url")
            })

        yield self.create_json_message({"total": len(prs), "pull_requests": prs})
