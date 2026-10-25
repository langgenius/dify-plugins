from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.apify_run import MAX_ITEMS, run_actor, split_list


class TechStackTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        token = self.runtime.credentials["apify_api_token"]
        items = split_list(tool_parameters.get("urls"))
        if not items:
            raise ValueError("urls is required.")
        rows = run_actor(token, "website-tech-stack-detector", {"urls": [{"url": u} for u in items], "maxUrls": MAX_ITEMS})
        yield self.create_json_message({"count": len(rows), "results": rows})
