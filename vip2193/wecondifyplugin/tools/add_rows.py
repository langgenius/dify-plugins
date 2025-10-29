from collections.abc import Generator
from typing import Any
import json
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class AddRowsTool(Tool):
    def _get_access_token(self, corpid: str, corpsecret: str) -> tuple[str, str]:
        """获取access_token"""
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}"
        try:
            response = requests.get(url, timeout=10)
            result = response.json()
            if result.get("errcode") == 0:
                return result.get("access_token"), None
            return None, f"获取token失败: {result.get('errmsg')}"
        except Exception as e:
            return None, f"请求异常: {str(e)}"
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 从provider凭证获取
        corpid = self.runtime.credentials.get("corpid", "")
        corpsecret = self.runtime.credentials.get("corpsecret", "")
        
        sheet_id = tool_parameters.get("sheet_id", "")
        sheet_name = tool_parameters.get("sheet_name", "")
        rows_data = tool_parameters.get("rows_data", "")
        key_type = tool_parameters.get("key_type", "CELL_VALUE_KEY_TYPE_FIELD_TITLE")
        
        if not all([sheet_id, sheet_name, rows_data]):
            yield self.create_text_message("缺少必需参数")
            return
        
        # 获取access_token
        access_token, error = self._get_access_token(corpid, corpsecret)
        if error:
            yield self.create_text_message(error)
            return
        
        try:
            data = json.loads(rows_data)
            if not isinstance(data, list):
                yield self.create_text_message("rows_data必须是JSON数组")
                return
        except json.JSONDecodeError:
            yield self.create_text_message("rows_data格式错误")
            return
        
        # 调用企业微信智能表格API - 添加记录
        url = f"https://qyapi.weixin.qq.com/cgi-bin/wedoc/smartsheet/add_records?access_token={access_token}"
        
        # 构建记录数据 - 将字符串值转换为智能表格格式
        records = []
        for row in data:
            if isinstance(row, dict):
                # 转换每个字段的值为智能表格格式
                values = {}
                for field_name, field_value in row.items():
                    # 将字符串值包装为文本类型
                    if isinstance(field_value, str):
                        values[field_name] = [{
                            "type": "text",
                            "text": field_value
                        }]
                    elif isinstance(field_value, (int, float)):
                        # 数字类型直接传值
                        values[field_name] = field_value
                    elif isinstance(field_value, bool):
                        # 布尔类型直接传值
                        values[field_name] = field_value
                    else:
                        # 其他类型转为字符串
                        values[field_name] = [{
                            "type": "text",
                            "text": str(field_value)
                        }]
                records.append({"values": values})
            else:
                yield self.create_text_message("rows_data格式错误: 需要字典格式,如 [{\"字段名\": \"值\"}]")
                return
        
        payload = {
            "docid": sheet_id,
            "sheet_id": sheet_name,
            "key_type": key_type,
            "records": records
        }

        print(records)
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            # 检查HTTP状态码
            if response.status_code != 200:
                yield self.create_text_message(f"HTTP错误: {response.status_code}, 响应: {response.text[:200]}")
                return
            
            # 尝试解析JSON
            try:
                result = response.json()
            except ValueError as e:
                yield self.create_text_message(f"JSON解析失败: {str(e)}, 响应内容: {response.text[:200]}")
                return
            
            if result.get("errcode") == 0:
                added_records = result.get("records", [])
                yield self.create_json_message({
                    "success": True,
                    "message": f"成功添加 {len(added_records)} 条记录",
                    "added_count": len(added_records),
                    "records": added_records
                })
            else:
                yield self.create_json_message({
                    "success": False,
                    "errcode": result.get("errcode"),
                    "errmsg": result.get("errmsg")
                })
        except Exception as e:
            yield self.create_text_message(f"操作失败: {str(e)}")
