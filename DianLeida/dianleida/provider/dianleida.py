# -*- coding: utf-8 -*-
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.mcp_client import McpClient


class DianleidaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        url = str((credentials or {}).get("api_key") or "").strip()
        if not url:
            raise ToolProviderCredentialValidationError(
                "请填写店雷达 MCP 密钥 URL，可在 https://www.dianleida.net/mcp 获取。"
            )
        try:
            tools = McpClient(url).list_tools()
        except Exception as error:
            raise ToolProviderCredentialValidationError(
                "无法连接店雷达 MCP：{}。请确认填写的是完整的 MCP 密钥 URL。".format(error)
            )
        if not tools:
            raise ToolProviderCredentialValidationError(
                "连接成功但未返回任何工具，请确认该地址是店雷达 MCP 密钥 URL。"
            )
