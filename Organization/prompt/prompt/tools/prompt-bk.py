from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from langfuse import Langfuse
import json

class PromptTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        secret_key = tool_parameters["secret_key"]
        public_key = tool_parameters["public_key"]
        host = tool_parameters["host"]
        name = tool_parameters["name"]
        label = tool_parameters.get("label", "latest")

        custom_data = tool_parameters.get("custom_data", {})

        # 确保 custom_data 是字典类型
        if isinstance(custom_data, str):
            try:
                # 修正JSON解析问题：使用双引号而非单引号
                # 例如: '{"text": "movie_value"}' 是有效的JSON，而 "{'text': 'movie_value'}" 不是
                custom_data = json.loads(custom_data.replace("'", "\""))
            except json.JSONDecodeError:
                print(f"警告: custom_data 是字符串但无法解析为 JSON: {custom_data}")
                custom_data = {}

        print(f"处理后的 custom_data: {custom_data}")

        langfuse = Langfuse(
            secret_key=secret_key,
            public_key=public_key,
            host=host
        )

        langfuse_prompt = langfuse.get_prompt(name=name, label=label)

        print(f"custom_data 类型: {type(custom_data)}")
        print(f"custom_data 值: {custom_data}")
        prompt = langfuse_prompt.compile(**custom_data)

        # prompt = langfuse_prompt.get_langchain_prompt()
        # prompt = [(role, text.replace('{', '{{').replace('}', '}}')) for role, text in prompt]
        # prompt = [{'content': '你是一个专业的翻译官，使用金庸《倚天屠龙记》里九阳真经的口诀进行翻译以下内容成中文', 'role': 'system'}, {'content': '待翻译内容: movie_value', 'role': 'user'}]
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
                # 检查item是否是字典
                if isinstance(item, dict):
                    # 通过键名访问值
                    role = item.get("role")
                    content = item.get("content")

                    if role == "system":
                        system_value = content
                    elif role == "user":
                        user_value = content
                    elif role == "assistant":
                        assistant_value = content

            result = {"system_value": system_value,
                    "user_value": user_value,
                    "assistant_value": assistant_value,
                    "text_value": text_value
                      }

        yield self.create_json_message(result)

        # return {"system_value": system_value,
        #           "user_value": user_value,
        #           "assistant_value": assistant_value,
        #           "text_value": text_value
        #           }


        # yield ToolInvokeMessage(
        #     type="json",
        #     message={"json_object": result}
        # )




