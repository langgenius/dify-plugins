class PromptTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        custom_json = tool_parameters.get("custom_json")
        print(custom_json)

        langfuse = Langfuse(
            secret_key=secret_key,
            public_key=public_key,
            host=host
        )

        langfuse_prompt = langfuse.get_prompt(name=name, label=label)

        prompt = langfuse_prompt.compile(custom_json)
        print(prompt)