from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetRowsTool(Tool):
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
        
        if not sheet_id:
            yield self.create_text_message("缺少必需参数")
            return
        
        # 获取access_token
        access_token, error = self._get_access_token(corpid, corpsecret)
        if error:
            yield self.create_text_message(error)
            return
        
        # 调用企业微信API - 获取表格属性
        url = f"https://qyapi.weixin.qq.com/cgi-bin/wedoc/spreadsheet/get_sheet_properties?access_token={access_token}"
        payload = {
            "docid": sheet_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            
            if result.get("errcode") == 0:
                properties = result.get("properties", [])
                yield self.create_json_message({
                    "success": True,
                    "message": "获取表格信息成功",
                    "properties": properties
                })
            else:
                yield self.create_json_message({
                    "success": False,
                    "errcode": result.get("errcode"),
                    "errmsg": result.get("errmsg")
                })
        except Exception as e:
            yield self.create_text_message(f"查询失败: {str(e)}")
