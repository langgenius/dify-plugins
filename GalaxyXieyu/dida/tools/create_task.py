from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dida import DidaClient
from datetime import datetime
import pytz

class CreateTaskTool(Tool):
    """创建任务工具类，使用V2 API创建任务"""
    
    def _get_client(self) -> DidaClient:
        """获取滴答清单客户端"""
        token = self.runtime.credentials["token"]
        return DidaClient(token=token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        创建任务
        
        Args:
            tool_parameters: 工具参数，支持以下参数：
                - title: 任务标题
                - content: 任务内容
                - priority: 优先级
                - project_name: 项目名称
                - tag_names: 标签名称列表
                - start_date: 开始时间 (格式: YYYY-MM-DD HH:mm:ss)
                - due_date: 截止时间 (格式: YYYY-MM-DD HH:mm:ss)
                - is_all_day: 是否为全天任务
                - reminder: 提醒设置，支持以下格式：
                    1. 相对提醒（推荐）：
                       - "0": 准时提醒
                       - "-5M": 提前5分钟
                       - "-15M": 提前15分钟
                       - "-30M": 提前30分钟
                       - "-1H": 提前1小时
                       - "-2H": 提前2小时
                       - "-1D": 提前1天
                       - "-2D": 提前2天
                       - "-1W": 提前1周
                    2. 也可以使用 ReminderOption 枚举值（推荐）
                - parent_id: 父任务ID（可选）
                
        Returns:
            Generator[ToolInvokeMessage]: 创建结果
        """
        try:
            title = tool_parameters.get('title',"")
            content = tool_parameters.get('content',"")
            priority = tool_parameters.get('priority',0)
            project_name = tool_parameters.get('project_name',"")
            tag_names = tool_parameters.get('tag_names',[])
            start_date = tool_parameters.get('start_date')
            due_date = tool_parameters.get('due_date')
            is_all_day = tool_parameters.get('is_all_day', False)
            reminder = tool_parameters.get('reminder')
            parent_id = tool_parameters.get('parent_id')

            client = self._get_client()
            task = client.tasks.create_task(
                title=title,
                content=content,
                priority=priority,
                project_name=project_name,
                tag_names=tag_names,
                start_date=start_date,
                due_date=due_date,
                is_all_day=is_all_day,
                reminder=reminder,
                parent_id=parent_id
            )


            yield self.create_text_message(text=f"创建任务成功：{task}")
            
        except Exception as e:
            yield self.create_text_message(text=f"创建任务失败：{str(e)}") 
