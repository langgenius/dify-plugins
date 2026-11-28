from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

BASE = "https://pom-data-api.pomlabs.workers.dev"


class PomBase(Tool):
    PATH = ""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        key = self.runtime.credentials.get("api_key", "")
        params = {k: v for k, v in tool_parameters.items() if v not in (None, "")}
        for k, v in list(params.items()):
            if isinstance(v, float) and v.is_integer():
                params[k] = int(v)
        r = requests.get(BASE + self.PATH, params=params, headers={"X-API-Key": key}, timeout=120)
        try:
            data = r.json()
        except ValueError:
            data = {"error": r.text[:500]}
        if r.status_code >= 400:
            raise Exception("Pom Labs API %s: %s" % (r.status_code, str(data)[:500]))
        yield self.create_json_message(data)
