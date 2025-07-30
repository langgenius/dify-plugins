from collections.abc import Generator
import json
from urllib.parse import urljoin
import requests

# 导入 Dify 插件框架的核心组件
from dify_plugin import OAICompatLargeLanguageModel
from dify_plugin.entities.model import (
    DefaultParameterName,
    ModelFeature,
    ParameterRule,
    ParameterType,
    I18nObject,
)
from dify_plugin.entities.model.llm import LLMMode, LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool
from dify_plugin.errors.model import CredentialsValidateFailedError

import logging

# 配置日志系统
# 级别设为 DEBUG，便于开发调试时查看详细流程
# 输出格式包含时间、日志级别和消息内容
# 使用 StreamHandler 将日志输出到控制台
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到标准输出（如终端）
    ]
)

class BigMrAILanguageModel(OAICompatLargeLanguageModel):
    """
    BigMrAI 大语言模型适配器
    实现了与 OpenAI API 兼容的第三方模型接入，支持 chat/completion 模式。
    继承自 OAICompatLargeLanguageModel，复用 OpenAI 标准调用逻辑。
    """

    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: list[PromptMessageTool] | None = None,
        stop: list[str] | None = None,
        stream: bool = True,
        user: str | None = None,
    ) -> LLMResult | Generator:
        """
        执行模型调用的核心方法。
        在调用前对模型名去空格，并根据配置决定是否启用“思考模式”。

        参数:
            model: 模型名称
            credentials: 包含 API 密钥、端点等认证信息
            prompt_messages: 提示消息列表（支持多轮对话）
            model_parameters: 模型参数（如 temperature、max_tokens）
            tools: 工具定义（用于函数调用）
            stop: 停止生成的标记
            stream: 是否流式返回结果
            user: 用户标识（可选）

        返回:
            LLMResult 或 Generator（流式响应）
        """
        # 清理模型名称两端空格
        model = model.strip()
        
        # 获取兼容格式的凭证（如标准化 endpoint_url）
        compatible_credentials = self._get_compatible_credentials(credentials)
        
        # 从参数中提取 enable_thinking 配置（前端传入）
        enable_thinking = model_parameters.pop("enable_thinking", None)
        if enable_thinking is not None:
            # 若启用了思考模式，则通过 chat_template_kwargs 传递给底层模板引擎
            model_parameters["chat_template_kwargs"] = {"enable_thinking": bool(enable_thinking)}
        
        # 调用父类的标准 OpenAI 兼容调用逻辑
        return super()._invoke(
            model,
            compatible_credentials,
            prompt_messages,
            model_parameters,
            tools,
            stop,
            stream,
            user,
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        验证模型凭证是否有效。
        向模型 endpoint 发送一个简单的 'ping' 请求，检查能否成功响应。
        支持 chat 和 completion 两种模式。

        参数:
            model: 模型名称
            credentials: 用户输入的凭证信息（包含 api_key、endpoint_url、mode 等）

        异常:
            CredentialsValidateFailedError: 验证失败时抛出
        """
        try:
            # 获取标准化后的凭证（如自动补全 /v1 路径）
            credentials = self._get_compatible_credentials(credentials)
            
            # 构建请求头
            headers = {"Content-Type": "application/json"}
            api_key = credentials.get("api_key")
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"  # 添加 Bearer 认证
            
            # 获取并规范化 endpoint URL
            endpoint_url = credentials["endpoint_url"]
            if not endpoint_url.endswith("/"):
                endpoint_url += "/"  # 确保以斜杠结尾，避免 urljoin 出错

            # 准备验证请求的 payload 数据
            data = {"model": model, "max_tokens": 50}  # 最多生成 50 token
            
            # 判断调用模式（chat 或 completion）
            completion_type = LLMMode.value_of(credentials["mode"])

            if completion_type is LLMMode.CHAT:
                # 聊天模式：使用 messages 字段
                data["messages"] = [{"role": "user", "content": "ping"}]
                endpoint_url = urljoin(endpoint_url, "chat/completions")
            elif completion_type is LLMMode.COMPLETION:
                # 补全模式：使用 prompt 字段
                data["prompt"] = "ping"
                endpoint_url = urljoin(endpoint_url, "completions")
            else:
                raise ValueError("Unsupported completion type for model configuration.")

            # 发送 POST 请求进行验证
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=data,
                timeout=(10, 300)  # 连接超时10秒，读取超时300秒
            )

            if response.status_code == 200:
                    return  # ✅ 成功返回，验证通过
                            

            # HTTP 状态码非200视为验证失败
            if response.status_code != 200:
                raise CredentialsValidateFailedError(
                    f"Credentials validation failed with status code {response.status_code}"
                )

            # JSON 解析失败，但 HTTP 状态码为 200，仍视为验证通过
            # 说明服务可达且响应了内容，即使不是标准 JSON 格式（某些私有部署模型可能如此）
            # 自己本地部署的模型只支持流模式，和模型模型不是返回的json格式，直接判断请求状态
            if response.status_code == 200:
                    return  # ✅ 成功返回，验证通过
 
        # 捕获其他所有异常，统一包装为 CredentialsValidateFailedError 返回
        except Exception as ex:
            raise CredentialsValidateFailedError(
                f"An error occurred during credentials validation: {str(ex)}"
            ) from ex

    def _add_custom_parameters(self, credentials: dict) -> None:
        """
        设置默认调用模式为 'chat'。
        如果用户未指定 mode，则默认使用聊天模式。

        参数:
            credentials: 凭证字典（会被原地修改）
        """
        credentials["mode"] = "chat"

    def _get_compatible_credentials(self, credentials: dict) -> dict:
        """
        标准化凭证中的 endpoint_url。
        去除可能的版本路径（如 /v1, /v1-openai 等），然后统一加上 '/v1'。
        确保与 OpenAI API 格式兼容。

        参数:
            credentials: 原始凭证

        返回:
            新的凭证副本，其中 endpoint_url 已标准化
        """
        credentials = credentials.copy()  # 避免修改原对象
        base_url = (
            credentials["endpoint_url"]
            .rstrip("/")                    # 去除末尾斜杠
            .removesuffix("/v1")           # 移除可能的 /v1
            .removesuffix("/v1/")
            .removesuffix("/v1-openai")
            .removesuffix("/v1-openai/")
            .removesuffix("/openai-v1")
            .removesuffix("/openai-v1/")
        )
        # 重新拼接标准路径
        credentials["endpoint_url"] = f"{base_url}/v1"
        return credentials

    def get_customizable_model_schema(self, model, credentials):
        """
        定义模型支持的自定义参数和功能特性。
        在 Dify 界面中展示可配置项（如开关、下拉菜单等）。

        参数:
            model: 模型名称
            credentials: 凭证信息（用于判断支持哪些功能）

        返回:
            包含功能特性和参数规则的模型实体
        """
        # 先获取父类的基础 schema
        entity = super().get_customizable_model_schema(model, credentials)
        
        # 判断是否支持 Agent 思维链（Thought）
        agent_thought_support = credentials.get("agent_thought_support", "not_supported")
        if agent_thought_support == "supported":
            try:
                # 检查是否已存在该功能，避免重复添加
                entity.features.index(ModelFeature.AGENT_THOUGHT)
            except ValueError:
                # 不存在则添加
                entity.features.append(ModelFeature.AGENT_THOUGHT)

        # 判断是否支持结构化输出（JSON 模式）
        structured_output_support = credentials.get("structured_output_support", "not_supported")
        if structured_output_support == "supported":
            # 添加 response_format 参数（可选：text / json_object / json_schema）
            entity.parameter_rules.append(ParameterRule(
                name=DefaultParameterName.RESPONSE_FORMAT.value,
                label=I18nObject(en_US="Response Format", zh_Hans="回复格式"),
                help=I18nObject(
                    en_US="Specifying the format that the model must output.",
                    zh_Hans="指定模型必须输出的格式。",
                ),
                type=ParameterType.STRING,
                options=["text", "json_object", "json_schema"],
                required=False,
            ))
            # 添加 json_schema 参数（用于定义 JSON 结构）
            entity.parameter_rules.append(ParameterRule(
                name=DefaultParameterName.JSON_SCHEMA.value,
                use_template=DefaultParameterName.JSON_SCHEMA.value
            ))

        # 添加“思考模式”开关（如 Qwen3 的 thinking 模式）
        entity.parameter_rules += [
            ParameterRule(
                name="enable_thinking",
                label=I18nObject(en_US="Thinking mode", zh_Hans="思考模式"),
                help=I18nObject(
                    en_US="Whether to enable thinking mode, applicable to various thinking mode models deployed on reasoning frameworks such as vLLM and SGLang, for example Qwen3.",
                    zh_Hans="是否开启思考模式，适用于vLLM和SGLang等推理框架部署的多种思考模式模型，例如Qwen3。",
                ),
                type=ParameterType.BOOLEAN,
                required=False,
            )
        ]
        return entity