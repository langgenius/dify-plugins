import re
from collections.abc import Generator
from typing import Optional, Union

from dify_plugin import OAICompatLargeLanguageModel
from dify_plugin.entities.model import AIModelEntity, FetchFrom, ModelFeature
from dify_plugin.entities.model.llm import LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeError,
)

from models.router_client import (
    CLIENT_HEADERS,
    SITES,
    RouterKeyError,
    check_key,
    explain_http_error,
    live_models,
    load_catalog,
    normalize_endpoint,
    resolve_endpoint,
    site_mismatch_message,
)
from models.schema import model_yaml, upstream_params

_HTTP_ERROR = re.compile(r"status code (\d{3}): (.*)", re.S)
_SITE_BY_URL = {url: site for site, url in SITES.items()}


class BumoRouterLargeLanguageModel(OAICompatLargeLanguageModel):
    def _router_credentials(self, model: str, credentials: dict) -> dict:
        """补齐 OpenAI 兼容层要的字段：站点地址（按 Key 自动识别）、来源标识、工具调用方式。"""
        creds = dict(credentials)
        try:
            endpoint = resolve_endpoint(creds)
        except RouterKeyError as e:
            raise InvokeAuthorizationError(str(e)) from e

        key_site = _SITE_BY_URL.get(endpoint)
        model_site = load_catalog().get(model, {}).get("site")
        if key_site and model_site and model_site != key_site:
            raise InvokeBadRequestError(site_mismatch_message(model, model_site, key_site))

        creds["endpoint_url"] = endpoint
        creds["mode"] = "chat"
        creds["extra_headers"] = dict(CLIENT_HEADERS)
        schema = self.get_model_schema(model, creds)
        if schema and ModelFeature.MULTI_TOOL_CALL in (schema.features or []):
            creds["function_calling_type"] = "tool_call"
        return creds

    @staticmethod
    def _owner(model: str, endpoint: str) -> str:
        """模型厂商（决定哪些参数上游不收）：先查包里的目录，新模型查 /v1/models（有 10 分钟缓存）。"""
        owner = load_catalog().get(model, {}).get("owned_by")
        if owner is None:
            try:
                owner = live_models(endpoint).get(model, {}).get("owned_by")
            except Exception:
                pass
        return owner or ""

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
        creds = self._router_credentials(model, credentials)
        model_parameters = upstream_params(self._owner(model, creds["endpoint_url"]), model_parameters)
        try:
            return super()._invoke(model, creds, prompt_messages, model_parameters, tools, stop, stream, user)
        except InvokeError as e:
            m = _HTTP_ERROR.search(str(e))
            hint = m and explain_http_error(int(m.group(1)), m.group(2))
            if hint:
                raise InvokeBadRequestError(hint) from e
            raise

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """「添加模型」时调用：Key 对不对、这个站点有没有这个模型。不发真实对话，不花钱。"""
        try:
            endpoint = check_key(credentials.get("api_key", ""), credentials.get("endpoint_url") or None)
        except RouterKeyError as e:
            raise CredentialsValidateFailedError(str(e)) from e
        except Exception as e:
            raise CredentialsValidateFailedError(f"连接 Router 失败 / Failed to reach Router: {e}") from e

        model_site = load_catalog().get(model, {}).get("site")
        if model_site:
            key_site = _SITE_BY_URL.get(endpoint)
            if key_site and model_site != key_site:
                # 和 _router_credentials 同一判据：这里放过，调用时也必然被拒
                raise CredentialsValidateFailedError(site_mismatch_message(model, model_site, key_site))
            return
        try:
            available = live_models(endpoint)
        except Exception:
            return  # 目录拉不到不拦用户，调用时 Router 会给出明确报错
        if model not in available:
            raise CredentialsValidateFailedError(
                f"当前站点没有模型 {model}，可用模型见 {endpoint}/models"
                f" / Model {model} is not available, see {endpoint}/models"
            )

    def get_customizable_model_schema(self, model: str, credentials: dict) -> Optional[AIModelEntity]:
        """目录里没有的新模型：上下文长度、工具调用、视觉都从 Router /v1/models 查，用户只填模型名。"""
        info = None
        site = load_catalog().get(model, {}).get("site")
        try:
            endpoint = (
                normalize_endpoint(credentials["endpoint_url"])
                if credentials.get("endpoint_url")
                else resolve_endpoint(credentials)
            )
            info = live_models(endpoint).get(model)
            site = _SITE_BY_URL.get(endpoint, site or "intl")
        except Exception:
            pass
        doc = model_yaml(info or {"id": model}, site or "cn")
        return AIModelEntity(**doc, fetch_from=FetchFrom.CUSTOMIZABLE_MODEL)
