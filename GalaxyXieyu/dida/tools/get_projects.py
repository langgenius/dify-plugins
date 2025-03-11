from typing import Any
from collections.abc import Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from dida import DidaClient

class GetProjectsTool(Tool):
    """获取项目列表工具类"""
    
    def _get_client(self) -> DidaClient:
        """获取滴答清单客户端"""
        token = self.runtime.credentials["token"]
        return DidaClient(token=token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        获取项目列表
        
        Args:
            tool_parameters: 工具参数，支持以下参数：
                - name: 项目名称筛选
                - color: 项目颜色筛选
                - group_id: 项目组ID筛选
                - include_tasks: 是否包含任务列表
                
        Returns:
            Generator[ToolInvokeMessage]: 项目列表
        """
        try:
            name = tool_parameters.get('name')
            color = tool_parameters.get('color')
            group_id = tool_parameters.get('group_id')
            include_tasks = tool_parameters.get('include_tasks', True)

            print(f"获取项目参数: {tool_parameters}")
            
            client = self._get_client()
            projects = client.projects.get_projects(
                name=name,
                color=color,
                group_id=group_id,
                include_tasks=include_tasks
            )
            
            yield self.create_text_message(text=f"获取项目列表成功：{projects}")
            
        except Exception as e:
            yield self.create_text_message(text=f"获取项目列表失败：{str(e)}") 