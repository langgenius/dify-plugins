from typing import Any, Generator, Optional, Union
from urllib.parse import urljoin

import certifi
import requests
from pydantic import TypeAdapter

from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.entities.model.llm import LLMMode, LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageFunction, PromptMessageTool
from dify_plugin.errors.model import CredentialsValidateFailedError, InvokeError
from dify_plugin.interfaces.model.openai_compatible.llm import OAICompatLargeLanguageModel

_plugin_config = DifyPluginEnv()


class BytePlusModelArkLargeLanguageModel(OAICompatLargeLanguageModel):
    def _get_ssl_verify(self, credentials: dict):
        ca_bundle_path = credentials.get("ca_bundle_path")
        if ca_bundle_path:
            return ca_bundle_path
        ssl_verify = credentials.get("ssl_verify", True)
        if isinstance(ssl_verify, str):
            ssl_verify = ssl_verify.strip().lower() in {"true", "1", "yes", "y"}
        if ssl_verify is True:
            return certifi.where()
        return ssl_verify

    def validate_credentials(self, model: str, credentials: dict) -> None:
        headers = {"Content-Type": "application/json"}

        api_key = credentials.get("api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        verify = self._get_ssl_verify(credentials)
        endpoint_url = credentials["endpoint_url"]
        if not endpoint_url.endswith("/"):
            endpoint_url += "/"

        data = {
            "model": credentials.get("endpoint_model_name") or model,
            "max_tokens": credentials.get("validate_credentials_max_tokens", 5) or 5,
        }

        completion_type = LLMMode.value_of(credentials["mode"])

        if completion_type is LLMMode.CHAT:
            data["messages"] = [{"role": "user", "content": "ping"}]
            endpoint_url = urljoin(endpoint_url, "chat/completions")
        elif completion_type is LLMMode.COMPLETION:
            data["prompt"] = "ping"
            endpoint_url = urljoin(endpoint_url, "completions")
        else:
            raise CredentialsValidateFailedError("Unsupported completion type for model configuration.")

        response = None
        try:
            stream_mode_auth = credentials.get("stream_mode_auth", "not_use")
            if stream_mode_auth == "use":
                data["stream"] = True
                data["max_tokens"] = credentials.get("validate_credentials_max_tokens", 10) or 10
                response = requests.post(
                    endpoint_url, headers=headers, json=data, timeout=(10, 300), stream=True, verify=verify
                )
                if response.status_code != 200:
                    raise CredentialsValidateFailedError(
                        f"Credentials validation failed with status code {response.status_code} "
                        f"and response body {response.text}"
                    )
                return

            response = requests.post(endpoint_url, headers=headers, json=data, timeout=(10, 300), verify=verify)
            if response.status_code != 200:
                raise CredentialsValidateFailedError(
                    f"Credentials validation failed with status code {response.status_code} "
                    f"and response body {response.text}"
                )

            try:
                json_result = response.json()
            except Exception:
                raise CredentialsValidateFailedError(
                    f"Credentials validation failed: JSON decode error, response body {response.text}"
                ) from None

            if completion_type is LLMMode.CHAT and json_result.get("object", "") == "":
                json_result["object"] = "chat.completion"
            elif completion_type is LLMMode.COMPLETION and json_result.get("object", "") == "":
                json_result["object"] = "text_completion"

            if completion_type is LLMMode.CHAT and (
                "object" not in json_result or json_result["object"] != "chat.completion"
            ):
                raise CredentialsValidateFailedError(
                    "Credentials validation failed: invalid response object, "
                    f"must be 'chat.completion', response body {response.text}"
                )
            if completion_type is LLMMode.COMPLETION and (
                "object" not in json_result or json_result["object"] != "text_completion"
            ):
                raise CredentialsValidateFailedError(
                    "Credentials validation failed: invalid response object, "
                    f"must be 'text_completion', response body {response.text}"
                )
        except CredentialsValidateFailedError:
            raise
        except Exception as ex:
            response_body = response.text if response is not None else ""
            raise CredentialsValidateFailedError(
                f"An error occurred during credentials validation: {ex!s}, response body {response_body}"
            ) from ex

    def _generate(
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
        headers = {
            "Content-Type": "application/json",
            "Accept-Charset": "utf-8",
        }
        extra_headers = credentials.get("extra_headers")
        if extra_headers is not None:
            headers = {
                **headers,
                **extra_headers,
            }

        api_key = credentials.get("api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint_url = credentials["endpoint_url"]
        if not endpoint_url.endswith("/"):
            endpoint_url += "/"

        response_format = model_parameters.get("response_format")
        if response_format:
            if response_format == "json_schema":
                json_schema = model_parameters.get("json_schema")
                if not json_schema:
                    raise ValueError("Must define JSON Schema when the response format is json_schema")
                try:
                    schema = TypeAdapter(dict[str, Any]).validate_json(json_schema)
                except Exception as exc:
                    raise ValueError(f"not correct json_schema format: {json_schema}") from exc
                model_parameters.pop("json_schema")
                model_parameters["response_format"] = {"type": "json_schema", "json_schema": schema}
            else:
                model_parameters["response_format"] = {"type": response_format}
        elif "json_schema" in model_parameters:
            del model_parameters["json_schema"]

        data = {"model": credentials.get("endpoint_model_name", model), "stream": stream, **model_parameters}

        completion_type = LLMMode.value_of(credentials["mode"])

        if completion_type is LLMMode.CHAT:
            endpoint_url = urljoin(endpoint_url, "chat/completions")
            data["messages"] = [self._convert_prompt_message_to_dict(m, credentials) for m in prompt_messages]
        elif completion_type is LLMMode.COMPLETION:
            endpoint_url = urljoin(endpoint_url, "completions")
            data["prompt"] = prompt_messages[0].content
        else:
            raise ValueError("Unsupported completion type for model configuration.")

        function_calling_type = credentials.get("function_calling_type", "no_call")
        formatted_tools = []
        if tools:
            if function_calling_type == "function_call":
                data["functions"] = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    }
                    for tool in tools
                ]
            elif function_calling_type == "tool_call":
                data["tool_choice"] = "auto"
                for tool in tools:
                    formatted_tools.append(PromptMessageFunction(function=tool).model_dump())
                data["tools"] = formatted_tools

        if stop:
            data["stop"] = stop

        if user:
            data["user"] = user

        response = requests.post(
            endpoint_url,
            headers=headers,
            json=data,
            timeout=(10, _plugin_config.MAX_REQUEST_TIMEOUT),
            stream=stream,
            verify=self._get_ssl_verify(credentials),
        )

        if response.encoding is None or response.encoding == "ISO-8859-1":
            response.encoding = "utf-8"

        if response.status_code != 200:
            raise InvokeError(f"API request failed with status code {response.status_code}: {response.text}")

        if stream:
            return self._handle_generate_stream_response(model, credentials, response, prompt_messages)

        return self._handle_generate_response(model, credentials, response, prompt_messages)

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
        api_model = credentials.get("endpoint_model_name") or model
        return self._generate(
            api_model,
            credentials,
            prompt_messages,
            model_parameters,
            tools,
            stop,
            stream,
            user,
        )
