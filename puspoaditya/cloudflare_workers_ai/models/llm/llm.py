from collections.abc import Generator
from typing import Optional, Union

from dify_plugin import OAICompatLargeLanguageModel
from dify_plugin.entities.model.llm import LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool


class CloudflareLargeLanguageModel(OAICompatLargeLanguageModel):
    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: Optional[list[PromptMessageTool]] = None,
        stop: Optional[list[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        self._add_custom_parameters(credentials)
        return super()._invoke(
            model, credentials, prompt_messages, model_parameters, tools, stop, stream
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        self._add_custom_parameters(credentials)
        super().validate_credentials(model, credentials)

    @staticmethod
    def _add_custom_parameters(credentials: dict) -> None:
        account_id = str(credentials.get("account_id", "")).strip()
        if not account_id:
            raise ValueError("Cloudflare Account ID is required.")

        # Workers AI exposes an OpenAI-compatible endpoint:
        # https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1
        credentials["mode"] = "chat"
        credentials["endpoint_url"] = (
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1"
        )
