from typing import Any, Optional
from collections.abc import Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from dida import DidaClient
from datetime import datetime

class UpdateTaskTool(Tool):
    """更新任务工具类，使用V2 API更新任务"""
    
    def _get_client(self) -> DidaClient:
        """获取滴答清单客户端"""
        token = self.runtime.credentials["token"]
        return DidaClient(token=token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        更新任务
        
        Args:
            tool_parameters: 工具参数，支持以下参数：
                - task_id_or_title: 任务ID或标题（支持模糊匹配）
                - title: 任务标题
                - content: 任务内容
                - priority: 优先级
                - project_name: 项目名称
                - tag_names: 标签名称列表（逗号分隔的字符串）
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
                    3. None: 清除提醒设置
                - status: 任务状态
                
        Returns:
            Generator[ToolInvokeMessage]: 更新结果
        """
        try:
            task_id_or_title = tool_parameters.get('task_id_or_title')
            if not task_id_or_title:
                yield self.create_text_message(text="更新任务失败：任务ID或标题不能为空")
                
            # 处理标签列表
            tag_names = tool_parameters.get('tag_names')
            if tag_names and isinstance(tag_names, str):
                tag_names = [tag.strip() for tag in tag_names.split(',')]
                
            # 处理日期时间
            start_date = None
            if tool_parameters.get('start_date'):
                try:
                    start_date = datetime.strptime(tool_parameters['start_date'], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    yield self.create_text_message(text="更新任务失败：开始时间格式错误，应为YYYY-MM-DD HH:mm:ss")
                    
            due_date = None
            if tool_parameters.get('due_date'):
                try:
                    due_date = datetime.strptime(tool_parameters['due_date'], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    yield self.create_text_message(text="更新任务失败：截止时间格式错误，应为YYYY-MM-DD HH:mm:ss")

            client = self._get_client()
            result = client.tasks.update_task(
                task_id_or_title=task_id_or_title,
                title=tool_parameters.get('title'),
                content=tool_parameters.get('content'),
                priority=tool_parameters.get('priority'),
                project_name=tool_parameters.get('project_name'),
                tag_names=tag_names,
                start_date=start_date,
                due_date=due_date,
                is_all_day=tool_parameters.get('is_all_day'),
                reminder=tool_parameters.get('reminder'),
                status=tool_parameters.get('status')
            )
            
            if result.get('success'):
                yield self.create_text_message(text=f"更新任务成功：{result.get('info')}\n任务数据：{result.get('data')}")
            else:
                yield self.create_text_message(text=f"更新任务失败：{result.get('info')}")
            
        except Exception as e:
            yield self.create_text_message(text=f"更新任务失败：{str(e)}") 

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        解析日期字符串为datetime对象
        
        Args:
            date_str: 日期字符串
            
        Returns:
            Optional[datetime]: 解析后的datetime对象，解析失败返回None
        """
        if not date_str:
            return None
            
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"Warning: Unrecognized date format: {date_str}")
            return None 