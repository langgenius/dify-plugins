import hashlib
import json

from dify_plugin import Tool
from tools._client import OdileDirectClient


class DirectTool(Tool):
    def _invoke(self, tool_parameters):
        arguments = {k: v for k, v in tool_parameters.items() if v is not None and v != ""}
        for key, expected in (("data", dict), ("questions", list)):
            if key in arguments:
                if isinstance(arguments[key], str):
                    arguments[key] = json.loads(arguments[key])
                if not isinstance(arguments[key], expected):
                    raise ValueError(f"{key} must be a JSON {expected.__name__}")
        if self.name == "send_to_business" and not arguments.get("message_id"):
            value = arguments["biz"] + arguments["skill"] + json.dumps(arguments["data"], sort_keys=True)
            arguments["message_id"] = hashlib.sha256(value.encode()).hexdigest()[:40]
        result = OdileDirectClient(api_key=self.runtime.credentials.get("api_key")).call(self.name, arguments)
        yield self.create_json_message(result if isinstance(result, dict) else {"result": result})
        yield self.create_text_message("Odile Direct response received. Check the result for its status.")
