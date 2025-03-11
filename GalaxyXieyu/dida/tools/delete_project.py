from typing import Any
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dida import DidaClient

class DeleteProjectTool(Tool):
    """删除项目工具类"""
    
    def _get_client(self) -> DidaClient:
        """获取滴答清单客户端"""
        token = self.runtime.credentials["token"]
        return DidaClient(token=token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        删除项目
        
        Args:
            tool_parameters: 工具参数，支持以下参数：
                - project_id: 项目ID
                
        Returns:
            Generator[ToolInvokeMessage]: 删除结果
        """
        try:
            # 获取并验证参数
            project_id = tool_parameters.get('project_id')
            if not project_id:
                yield self.create_text_message(text="删除项目失败：项目ID不能为空")

            print(f"删除项目参数: {tool_parameters}")
            
            # 尝试删除项目
            client = self._get_client()
            result = client.projects.delete_project(project_id=project_id)
            
            # 处理返回结果
            if isinstance(result, dict):
                if result.get('success'):
                    yield self.create_text_message(text=f"删除项目成功：{result.get('info')}")
                else:
                    yield self.create_text_message(text=f"删除项目失败：{result.get('info')}")
            elif result:
                yield self.create_text_message(text="删除项目成功")
            else:
                yield self.create_text_message(text="删除项目失败：项目可能不存在")
            
        except Exception as e:
            error_msg = str(e)
            if "NoneType" in error_msg:
                yield self.create_text_message(text="删除项目失败：项目不存在或已被删除")
            yield self.create_text_message(text=f"删除项目失败：{error_msg}") 