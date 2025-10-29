from collections.abc import Generator
from typing import Any
import json
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class UpdateRowsTool(Tool):
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
        record_id = tool_parameters.get("record_id", "")
        row_data = tool_parameters.get("row_data", "")
        
        if not all([sheet_id, sheet_name, record_id, row_data]):
            yield self.create_text_message("缺少必需参数")
            return
        
        # 获取access_token
        access_token, error = self._get_access_token(corpid, corpsecret)
        if error:
            yield self.create_text_message(error)
            return
        
        try:
            data = json.loads(row_data)
            if not isinstance(data, dict):
                yield self.create_text_message("row_data必须是JSON对象,如 {\"字段名\": \"值\"}")
                return
        except json.JSONDecodeError:
            yield self.create_text_message("row_data格式错误")
            return
        
        # 调用企业微信智能表格API - 更新记录
        url = f"https://qyapi.weixin.qq.com/cgi-bin/wedoc/smartsheet/update_records?access_token={access_token}"
        payload = {
            "docid": sheet_id,
            "sheet_id": sheet_name,
            "key_type": "CELL_VALUE_KEY_TYPE_FIELD_TITLE",
            "records": [{
                "record_id": record_id,
                "values": data
            }]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            
            if result.get("errcode") == 0:
                updated_records = result.get("records", [])
                yield self.create_json_message({
                    "success": True,
                    "message": "更新成功",
                    "records": updated_records
                })
            else:
                yield self.create_json_message({
                    "success": False,
                    "errcode": result.get("errcode"),
                    "errmsg": result.get("errmsg")
                })
        except Exception as e:
            yield self.create_text_message(f"更新失败: {str(e)}")
