from typing import Any
from collections.abc import Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from dida import DidaClient
from datetime import datetime

class GetTasksTool(Tool):
    """获取任务工具类，使用V2 API获取任务"""
    
    def _get_client(self) -> DidaClient:
        """获取滴答清单客户端"""
        token = self.runtime.credentials["token"]
        return DidaClient(token=token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        获取任务
        
        Args:
            tool_parameters: 工具参数，支持以下参数：
                - mode: 查询模式
                - keyword: 关键词筛选
                - priority: 优先级筛选
                - project_name: 项目名称筛选
                - tag_names: 标签名称列表筛选
                - created_after: 创建时间开始筛选
                - created_before: 创建时间结束筛选
                - completed_after: 完成时间开始筛选
                - completed_before: 完成时间结束筛选
                - completed: 是否已完成
                
        Returns:
            Generator[ToolInvokeMessage]: 任务列表
        """
        try:
            mode = tool_parameters.get('mode', 'all')
            keyword = tool_parameters.get('keyword', None)
            priority = tool_parameters.get('priority', None)
            project_name = tool_parameters.get('project_name', None)
            tag_names = tool_parameters.get('tag_names', None)
            created_after = tool_parameters.get('created_after', None)
            created_before = tool_parameters.get('created_before', None)
            completed_after = tool_parameters.get('completed_after', None)
            completed_before = tool_parameters.get('completed_before', None)
            completed = tool_parameters.get('completed', False)
            client = self._get_client()
            if completed_after:
                completed_after = datetime.strptime(completed_after, "%Y-%m-%dT%H:%M:%S")
            if completed_before:
                completed_before = datetime.strptime(completed_before, "%Y-%m-%dT%H:%M:%S")
            tasks = client.tasks.get_tasks(
                mode=mode,
                keyword=keyword,
                priority=priority,
                project_name=project_name,
                tag_names=tag_names,
                created_after=created_after,
                created_before=created_before,
                completed_after=completed_after,
                completed_before=completed_before,
                completed=completed
            )
            yield self.create_text_message(text=f"获取任务成功：{tasks}")
            
        except Exception as e:
            yield self.create_text_message(text=f"获取任务失败：{str(e)}") 