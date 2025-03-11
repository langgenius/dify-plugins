from typing import Any, Union, Dict
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dida import DidaClient
from collections.abc import Generator
from typing import Any

class CreateProjectTool(Tool):
    """创建项目工具类"""
    
    def _get_client(self) -> DidaClient:
        """获取滴答清单客户端"""
        token = self.runtime.credentials["token"]
        return DidaClient(token=token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        创建项目
        
        Args:
            tool_parameters: 工具参数，支持以下参数：
                - name: 项目名称
                - color: 项目颜色
                - group_id: 项目组ID
                - view_mode: 视图模式
                - is_inbox: 是否为收集箱
                
        Returns:
            Union[ToolInvokeMessage, list[ToolInvokeMessage]]: 创建结果
        """
        try:
            name = tool_parameters.get('name')
            if not name:
                return self.create_text_message(text="创建项目失败：项目名称不能为空")
                
            color = tool_parameters.get('color')
            group_id = tool_parameters.get('group_id')
            view_mode = tool_parameters.get('view_mode', 'list')
            is_inbox = tool_parameters.get('is_inbox', False)

            print(f"创建项目参数: {tool_parameters}")
            
            client = self._get_client()
            project = client.projects.create_project(
                name=name,
                color=color,
                group_id=group_id,
                view_mode=view_mode,
                is_inbox=is_inbox
            )
            
            yield self.create_text_message(text=f"创建项目成功：{project}")
            
        except Exception as e:
            yield self.create_text_message(text=f"创建项目失败：{str(e)}") 