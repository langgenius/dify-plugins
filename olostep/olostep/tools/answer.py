import json
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from typing import Any, Generator


class AnswerTool(Tool):
    def _invoke(
        self, 
        tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        from olostep import Olostep, Olostep_BaseError
        
        api_key = self.runtime.credentials["api_key"]
        client = Olostep(api_key=api_key)
        
        task = tool_parameters.get("task", "").strip()
        json_schema_str = tool_parameters.get("json_schema")
        
        if not task:
            yield self.create_text_message("Error: Task is required")
            return
        
        try:
            kwargs = {"task": task}
            
            if json_schema_str:
                try:
                    schema_dict = json.loads(json_schema_str)
                    kwargs["json"] = schema_dict
                except json.JSONDecodeError as e:
                    yield self.create_text_message(f"Error: Invalid JSON schema: {e}")
                    return
            
            answer_result = client.answers.create(**kwargs)
            
            answer_text = answer_result.get("answer", "")
            sources = answer_result.get("sources", [])
            
            sources_str = "\n".join(sources) if sources else "No sources"
            content = f"{answer_text}\n\nSources:\n{sources_str}"
            
            yield self.create_text_message(content)
            
        except Olostep_BaseError as e:
            yield self.create_text_message(f"Olostep API error: {type(e).__name__}: {e}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {e}")
