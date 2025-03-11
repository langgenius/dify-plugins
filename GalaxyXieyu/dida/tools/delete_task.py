from typing import Any
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dida import DidaClient

class DeleteTaskTool(Tool):
    """删除任务工具类，使用V2 API删除任务"""
    
    def _get_client(self) -> DidaClient:
        """获取滴答清单客户端"""
        token = self.runtime.credentials["token"]
        return DidaClient(token=token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        删除任务
        
        Args:
            tool_parameters: 工具参数，支持以下参数：
                - task_id_or_title: 任务ID或标题（支持模糊匹配）
                
        Returns:
            Generator[ToolInvokeMessage]: 删除结果
        """
        try:
            # 获取并验证参数
            task_id_or_title = tool_parameters.get('task_id_or_title')
            if not task_id_or_title:
                yield self.create_text_message(text="删除任务失败：任务ID或标题不能为空")

            # 尝试删除任务
            client = self._get_client()
            result = client.tasks.delete_task(task_id_or_title)
            
            # 处理返回结果
            if isinstance(result, dict):
                if result.get('success'):
                    yield self.create_text_message(text=f"删除任务成功：{result.get('info')}")
                else:
                    yield self.create_text_message(text=f"删除任务失败：{result.get('info')}")
            elif result:
                yield self.create_text_message(text="删除任务成功")
            else:
                yield self.create_text_message(text="删除任务失败：任务可能不存在")
            
        except Exception as e:
            yield self.create_text_message(text=f"删除任务失败：{str(e)}") 