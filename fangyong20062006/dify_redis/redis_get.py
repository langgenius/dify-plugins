from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from store import redis_get, redis_ttl


class RedisGetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        key = tool_parameters.get("key", "").strip()
        if not key:
            raise Exception("key 不能为空")

        try:
            value = redis_get(key)
        except Exception as e:
            raise Exception(f"读取失败: {e}")

        if value is None:
            result = (
                f"GET MISS\n"
                f"key  : {key}\n"
                f"说明 : 键不存在或已过期"
            )
        else:
            ttl = redis_ttl(key)
            ttl_info = "永不过期" if ttl == -1 else f"剩余 {ttl} 秒"
            result = (
                f"GET HIT\n"
                f"key  : {key}\n"
                f"TTL  : {ttl_info}\n"
                f"value:\n{value}"
            )

        yield self.create_text_message(result)
