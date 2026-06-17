from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from store import redis_exists, redis_ttl, redis_info


class RedisExistsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        key = tool_parameters.get("key", "").strip()
        if not key:
            raise Exception("key 不能为空")

        try:
            exists = redis_exists(key)
            ttl = redis_ttl(key)
            info = redis_info()
        except Exception as e:
            raise Exception(f"查询失败: {e}")

        if exists:
            ttl_info = "永不过期" if ttl == -1 else f"剩余 {ttl} 秒"
            status = "EXISTS"
        else:
            ttl_info = "—"
            status = "NOT EXISTS"

        result = (
            f"EXISTS: {status}\n"
            f"key       : {key}\n"
            f"TTL       : {ttl_info}\n"
            f"─────────────────\n"
            f"缓存统计\n"
            f"  总键数  : {info['total_keys']}\n"
            f"  有效键  : {info['active_keys']}\n"
            f"  已过期  : {info['expired_keys']}\n"
            f"  存储大小: {info['store_size_bytes']} bytes\n"
            f"  存储路径: {info['store_path']}"
        )
        yield self.create_text_message(result)
