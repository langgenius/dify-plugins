from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from store import redis_delete


class RedisDeleteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        key = tool_parameters.get("key", "").strip()
        if not key:
            raise Exception("key 不能为空")

        try:
            existed = redis_delete(key)
        except Exception as e:
            raise Exception(f"删除失败: {e}")

        if existed:
            result = f"DEL OK\nkey  : {key}\n说明 : 键已删除"
        else:
            result = f"DEL NOP\nkey  : {key}\n说明 : 键不存在，无需删除"

        yield self.create_text_message(result)
