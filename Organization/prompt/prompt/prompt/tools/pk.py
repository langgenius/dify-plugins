from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from langfuse import Langfuse


class PromptTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        secret_key = tool_parameters["secret_key"]
        public_key = tool_parameters["public_key"]
        host = tool_parameters["host"]
        name = tool_parameters["name"]
        label = tool_parameters["label"]

        langfuse = Langfuse(
            secret_key=secret_key,
            public_key=public_key,
            host=host
        )

        langfuse_prompt = langfuse.get_prompt(name=name, label=label)
        prompt = langfuse_prompt.get_langchain_prompt()
        print(prompt)

        system_value = None
        user_value = None
        assistant_value = None
        text_value = None

        if isinstance(prompt, str):
            text_value = prompt
            result = {"text_value": text_value}
        elif isinstance(prompt, list):
            for item in prompt:
                if item[0] == "system":
                    system_value = item[1]
                elif item[0] == "user":
                    user_value = item[1]
                elif item[0] == "assistant":
                    assistant_value = item[1]

            result = {"system_value": system_value,
                    "user_value": user_value,
                    "assistant_value": assistant_value,
                    "text_value": text_value}

        yield ToolInvokeMessage(
            type="json",
            message={"json_object": result}
        )




