from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class CreateSheetTool(Tool):
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
        
        sheet_name = tool_parameters.get("sheet_name", "")
        admin_users = tool_parameters.get("admin_users", "")
        
        if not sheet_name:
            yield self.create_text_message("缺少表格名称")
            return
        
        # 获取access_token
        access_token, error = self._get_access_token(corpid, corpsecret)
        if error:
            yield self.create_text_message(error)
            return

        # 使用智能表格专用创建接口
        url = f"https://qyapi.weixin.qq.com/cgi-bin/wedoc/create_doc?access_token={access_token}"
        payload = {
            "doc_type": 10, # 只创建智能表格
            "doc_name": sheet_name
        }
        
        # 如果提供了管理员
        if admin_users:
            admin_list = [uid.strip() for uid in admin_users.split(",") if uid.strip()]
            if admin_list:
                payload["admin_users"] = admin_list
        
        try:
            print(payload)
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            
            if result.get("errcode") == 0:
                docid = result.get("docid")
                url = result.get("url")
                yield self.create_json_message({
                    "success": True,
                    "message": "表格创建成功",
                    "docid": docid,
                    "url": url
                })
            else:
                yield self.create_json_message({
                    "success": False,
                    "errcode": result.get("errcode"),
                    "errmsg": result.get("errmsg")
                })
        except Exception as e:
            yield self.create_text_message(f"创建失败: {str(e)}")
