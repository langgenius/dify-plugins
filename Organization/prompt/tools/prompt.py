from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from langfuse import Langfuse
import json


class PromptTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        global langfuse_prompt
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

        try:
            langfuse_prompt = langfuse.get_prompt(name=name, label=label)
        except Exception as e:
            print(f"获取prompt失败: {str(e)}")
            yield self.create_text_message(f"获取prompt失败: {str(e)}")

        print(f"custom_data 类型: {type(custom_data)}")
        print(f"custom_data 值: {custom_data}")
        prompt = langfuse_prompt.compile(**custom_data)
        print("prompt:", prompt)

        system_value = None
        user_value = None
        assistant_value = None
        text_value = None

        if isinstance(prompt, str):
            text_value = prompt
            # result = {"text_value": text_value}
            # print("text:", result)
            # 生成text提取值的消息
            yield self.create_variable_message("text_value", text_value)
        else:
            # print("chat")
            for item in prompt:
                if isinstance(item, dict):
                    role = item.get("role")
                    content = item.get("content")

                    if role == "system":
                        system_value = content
                    elif role == "user":
                        user_value = content
                    elif role == "assistant":
                        assistant_value = content

            # result = {
            #     "system_value": system_value,
            #     "user_value": user_value,
            #     "assistant_value": assistant_value,
            # }

            # print(result)

            # 生成chat提取值的消息
            yield self.create_variable_message("system_value", system_value)
            yield self.create_variable_message("user_value", user_value)
            yield self.create_variable_message("assistant_value", assistant_value)
