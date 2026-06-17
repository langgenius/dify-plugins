from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from store import redis_set, redis_ttl


class RedisSetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        key = tool_parameters.get("key", "").strip()
        value = tool_parameters.get("value", "")
        ttl_raw = tool_parameters.get("ttl_seconds")

        if not key:
            raise Exception("key 不能为空")

        ttl = None
        if ttl_raw is not None:
            try:
                ttl = int(ttl_raw)
                if ttl <= 0:
                    ttl = None
            except (ValueError, TypeError):
                raise Exception(f"ttl_seconds 必须是整数，收到: {ttl_raw}")

        try:
            redis_set(key, str(value), ttl)
        except Exception as e:
            raise Exception(f"写入失败: {e}")

        value_preview = str(value)[:80] + ("..." if len(str(value)) > 80 else "")
        ttl_info = f"{ttl} 秒后过期" if ttl else "永不过期"

        result = (
            f"SET OK\n"
            f"key     : {key}\n"
            f"value   : {value_preview}\n"
            f"TTL     : {ttl_info}\n"
            f"剩余TTL : {redis_ttl(key)} 秒"
        )
        yield self.create_text_message(result)
