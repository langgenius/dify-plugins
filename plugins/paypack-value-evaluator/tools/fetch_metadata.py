from typing import Any
from urllib.request import urlopen, Request
from urllib.error import URLError
import json
from dify_plugin import Tool

WELL_KNOWN_PATH = "/.well-known/ai-service-metadata.json"


class FetchServiceMetadataTool(Tool):
    name = "fetch_service_metadata"
    description = (
        "Fetch the AI service metadata from a given base URL. "
        "This metadata includes pricing, performance, reputation, and refund policy "
        "— essential for AI agents to evaluate whether a payment is worthwhile. "
        "This tool only READS data; it does NOT execute any payment."
    )

    parameters = {
        "type": "object",
        "properties": {
            "service_url": {
                "type": "string",
                "description": "The base URL of the service to evaluate, e.g., https://api.weather.com"
            }
        },
        "required": ["service_url"]
    }

    def execute(self, service_url: str) -> dict[str, Any]:
        metadata_url = f"{service_url.rstrip('/')}{WELL_KNOWN_PATH}"
        try:
            req = Request(metadata_url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "metadata": data}
        except URLError as e:
            return {"success": False, "error": f"Failed to fetch metadata: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON: {str(e)}"}
