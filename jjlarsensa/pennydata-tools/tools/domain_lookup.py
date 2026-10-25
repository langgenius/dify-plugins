from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.apify_run import MAX_ITEMS, run_actor, split_list


class DomainLookupTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        token = self.runtime.credentials["apify_api_token"]
        items = split_list(tool_parameters.get("domains"))
        if not items:
            raise ValueError("domains is required.")
        rows = run_actor(token, "bulk-domain-whois-dns-lookup", {"domains": items})
        yield self.create_json_message({"count": len(rows), "results": rows})
