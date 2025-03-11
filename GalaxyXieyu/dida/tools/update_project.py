from typing import Any
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dida import DidaClient

class UpdateProjectTool(Tool):
    """更新项目工具类"""
    
    def _get_client(self) -> DidaClient:
        """获取滴答清单客户端"""
        token = self.runtime.credentials["token"]
        return DidaClient(token=token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        更新项目
        
        Args:
            tool_parameters: 工具参数，支持以下参数：
                - project_id: 项目ID
                - name: 新的项目名称
                - color: 新的项目颜色
                - group_id: 新的项目组ID
                - view_mode: 新的视图模式
                
        Returns:
            Generator[ToolInvokeMessage]: 更新结果
        """
        try:
            # 获取并验证参数
            project_id = tool_parameters.get('project_id')
            if not project_id:
                yield self.create_text_message(text="更新项目失败：项目ID不能为空")
                
            # 获取更新参数
            name = tool_parameters.get('name')
            color = tool_parameters.get('color')
            group_id = tool_parameters.get('group_id')
            view_mode = tool_parameters.get('view_mode')

            # 检查是否有任何要更新的参数
            if not any([name, color, group_id, view_mode]):
                yield self.create_text_message(text="更新项目失败：至少需要提供一个要更新的参数（name、color、group_id 或 view_mode）")

            print(f"更新项目参数: {tool_parameters}")
            
            # 尝试更新项目
            client = self._get_client()
            result = client.projects.update_project(
                project_id=project_id,
                name=name,
                color=color,
                group_id=group_id,
                view_mode=view_mode
            )
            
            # 处理返回结果
            if isinstance(result, dict):
                if result.get('success'):
                    yield self.create_text_message(text=f"更新项目成功：{result.get('data')}")
                else:
                    yield self.create_text_message(text=f"更新项目失败：{result.get('info')}")
            elif result:
                yield self.create_text_message(text="更新项目成功")
            else:
                yield self.create_text_message(text="更新项目失败：项目可能不存在")
            
        except Exception as e:
            yield self.create_text_message(text=f"更新项目失败：{str(e)}") 