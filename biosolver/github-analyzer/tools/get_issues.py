from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetIssuesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        repo = tool_parameters["repo"].strip()
        limit = int(tool_parameters.get("limit") or 10)
        limit = min(limit, 30)
        headers = {"Accept": "application/vnd.github.v3+json"}

        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}/issues",
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

        issues = []
        for issue in data:
            if "pull_request" not in issue:
                issues.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "state": issue.get("state"),
                    "labels": [l["name"] for l in issue.get("labels", [])],
                    "created_at": issue.get("created_at"),
                    "url": issue.get("html_url")
                })

        yield self.create_json_message({"total": len(issues), "issues": issues})
