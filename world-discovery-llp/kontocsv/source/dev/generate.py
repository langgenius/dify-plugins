"""Generate KontoCSV Dify tool definitions from the live public read-only MCP catalog."""
from __future__ import annotations

import json
import pathlib
import urllib.request
from urllib.error import URLError

import yaml

ROOT = pathlib.Path(__file__).resolve().parent / "src"
CATALOG_URL = "https://www.kontocsv.de/api/mcp/claude/catalog"
EXPECTED = [
    "create_browser_upload_session",
    "complete_browser_upload",
    "inspect_bank_statement",
    "prepare_bank_statement_conversion",
    "get_credit_balance",
    "convert_bank_statement_for_accounting",
    "get_conversion_status",
    "download_accounting_export",
]
LABELS = {
    "create_browser_upload_session": "Create secure browser upload",
    "complete_browser_upload": "Check completed browser upload",
    "inspect_bank_statement": "Inspect bank or payment statement",
    "prepare_bank_statement_conversion": "Prepare existing-credit conversion",
    "get_credit_balance": "Check available conversion credits",
    "convert_bank_statement_for_accounting": "Start confirmed conversion",
    "get_conversion_status": "Check conversion and quality status",
    "download_accounting_export": "Get validated accounting export",
}
PARAM_LABELS = {
    "filename": "File name",
    "mediaType": "Source format",
    "locale": "Language",
    "uploadSessionId": "Upload session ID",
    "sourceId": "Source reference",
    "exportProfile": "Accounting export profile",
    "quoteId": "Prepared conversion quote",
    "confirmedByUser": "User explicitly confirmed",
    "jobId": "Conversion job ID",
}


def fetch_tools() -> list[dict]:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}).encode()
    request = urllib.request.Request(
        CATALOG_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2025-06-18",
            "User-Agent": "KontoCSV-Dify-contract-sync/0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(120000).decode("utf-8")
    if raw.startswith("event:"):
        content = next((line[5:].lstrip() for line in raw.splitlines() if line.startswith("data:")), None)
        if not content:
            raise RuntimeError("No MCP tool catalog message")
        parsed = json.loads(content)
    else:
        parsed = json.loads(raw)
    tools = parsed["result"]["tools"]
    actual_names = [tool["name"] for tool in tools]
    if actual_names != EXPECTED:
        raise RuntimeError("Published KontoCSV tool contract changed unexpectedly: " + str(actual_names))
    return tools


def parameter_spec(key: str, schema: dict, required: bool, *, tool_name: str) -> dict:
    typ = schema.get("type")
    if typ == "string" and "enum" in schema:
        parameter_type = "select"
    elif typ == "string":
        parameter_type = "string"
    elif typ == "boolean":
        parameter_type = "boolean"
    elif typ in ("integer", "number"):
        parameter_type = "number"
    else:
        raise ValueError(f"Unsupported Dify parameter type: {tool_name}.{key}={typ}")
    description = f"{PARAM_LABELS.get(key, key)} for {LABELS[tool_name]}."
    if key in ("sourceId", "uploadSessionId", "quoteId", "jobId"):
        description += " Reuse the exact opaque ID from the immediately preceding KontoCSV result; never guess or fabricate one."
    if key == "confirmedByUser":
        description = (
            "Set true ONLY after the human explicitly confirms the exact prepared conversion "
            "and required credits in this conversation. Never infer consent or preauthorize future operations."
        )
    if key == "filename":
        description += " Use only a filename; no bank login credentials."
    if key == "exportProfile":
        description += " Choose only a profile listed as supported by the inspection result."
    parameter = {
        "name": key,
        "type": parameter_type,
        "required": required,
        "label": {"en_US": PARAM_LABELS.get(key, key)},
        "human_description": {"en_US": description},
        "llm_description": description,
        "form": "llm",
    }
    if parameter_type == "select":
        parameter["options"] = [{"value": value, "label": {"en_US": str(value)}} for value in schema["enum"]]
    return parameter


def main() -> None:
    tools = fetch_tools()
    (ROOT / "tools").mkdir(parents=True, exist_ok=True)
    contracts = []
    for tool in tools:
        name = tool["name"]
        schema = tool["inputSchema"]
        properties = schema["properties"]
        required = set(schema.get("required", []))
        assert schema.get("additionalProperties") is False
        parameters = [
            parameter_spec(key, definition, key in required, tool_name=name)
            for key, definition in properties.items()
        ]
        description = tool["description"]
        notes = {
            "create_browser_upload_session":
                "Give the returned browserUploadUrl to the user for direct upload on KontoCSV, not in Dify.",
            "complete_browser_upload":
                "Call after the user finishes uploading. Reuse the same uploadSessionId until upload completes or expires.",
            "inspect_bank_statement":
                "Read-only; select the export profile based on the supportedExportProfiles response.",
            "prepare_bank_statement_conversion":
                "Uses existing credits only. If credits are insufficient, do not create a checkout; direct the user to KontoCSV's website.",
            "get_credit_balance": "Read-only and does not spend credits.",
            "convert_bank_statement_for_accounting":
                "CHARGES credits only after explicit human confirmation and a valid quoteId from preparation. Never confirm implicitly.",
            "get_conversion_status": "Read-only; repeat only as needed, no background polling loop built into the plugin.",
            "download_accounting_export":
                "Only returns a short-lived URL for a completed, eligible export. Never invent export readiness.",
        }
        llm_description = description + " " + notes[name]
        definition = {
            "identity": {"name": name, "author": "world-discovery-llp",
                         "label": {"en_US": LABELS[name]}},
            "description": {"human": {"en_US": description}, "llm": llm_description},
            "parameters": parameters,
            "extra": {"python": {"source": f"tools/{name}.py"}},
        }
        (ROOT / "tools" / (name + ".yaml")).write_text(
            yaml.safe_dump(definition, sort_keys=False, allow_unicode=True, width=110),
            encoding="utf-8",
        )
        class_name = "".join(p.title() for p in name.split("_")) + "Tool"
        (ROOT / "tools" / (name + ".py")).write_text(
            "from tools._base import KontoCsvTool\n\n\n" +
            f"class {class_name}(KontoCsvTool):\n    mcp_tool_name = \"{name}\"\n",
            encoding="utf-8",
        )
        contracts.append({
            "name": name,
            "description": description,
            "inputSchema": schema,
            "outputSchema": tool["outputSchema"],
            "annotations": tool.get("annotations", {}),
        })
    (ROOT / "tools" / "contract.json").write_text(
        json.dumps(contracts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"tools": len(contracts), "names": EXPECTED,
                      "required_parameters": {c["name"]: c["inputSchema"].get("required", []) for c in contracts}}, indent=2))


if __name__ == "__main__":
    main()
