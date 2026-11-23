from collections.abc import Generator
from typing import Optional, Union

from dify_plugin import OAICompatLargeLanguageModel
from dify_plugin.entities.model.llm import LLMMode, LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool

DEFAULT_ENDPOINT = "https://api.fikraapi.co.ke/v1"


class FikraLargeLanguageModel(OAICompatLargeLanguageModel):
    """Fikra API is OpenAI-compatible; this only fixes the endpoint and chat mode."""

    @staticmethod
    def _add_custom_parameters(credentials: dict) -> None:
        endpoint = (credentials.get("endpoint_url") or "").strip().rstrip("/")
        credentials["endpoint_url"] = endpoint or DEFAULT_ENDPOINT
        credentials["mode"] = LLMMode.CHAT.value
        credentials["function_calling_type"] = "tool_call"
        credentials["stream_function_calling"] = "supported"

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
        return super()._invoke(model, credentials, prompt_messages, model_parameters, tools, stop, stream, user)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        self._add_custom_parameters(credentials)
        super().validate_credentials(model, credentials)

    def get_customizable_model_schema(self, model: str, credentials: dict):
        self._add_custom_parameters(credentials)
        return super().get_customizable_model_schema(model, credentials)
