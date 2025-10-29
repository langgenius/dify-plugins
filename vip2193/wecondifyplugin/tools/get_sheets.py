from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetSheetsTool(Tool):
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
        sub_sheet_id = tool_parameters.get("sub_sheet_id", "")
        need_all_type = tool_parameters.get("need_all_type_sheet", False)
        
        if not sheet_id:
            yield self.create_text_message("缺少表格ID")
            return
        
        # 获取access_token
        access_token, error = self._get_access_token(corpid, corpsecret)
        if error:
            yield self.create_text_message(error)
            return
        
        # 调用企业微信智能表格API - 查询子表
        url = f"https://qyapi.weixin.qq.com/cgi-bin/wedoc/smartsheet/get_sheet?access_token={access_token}"
        payload = {
            "docid": sheet_id,
            "need_all_type_sheet": need_all_type
        }
        
        # 如果指定了子表ID
        if sub_sheet_id:
            payload["sheet_id"] = sub_sheet_id
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            
            if result.get("errcode") == 0:
                sheet_list = result.get("sheet_list", [])
                yield self.create_json_message({
                    "success": True,
                    "message": f"查询成功,共 {len(sheet_list)} 个子表",
                    "sheet_count": len(sheet_list),
                    "sheet_list": sheet_list
                })
            else:
                yield self.create_json_message({
                    "success": False,
                    "errcode": result.get("errcode"),
                    "errmsg": result.get("errmsg")
                })
        except Exception as e:
            yield self.create_text_message(f"查询失败: {str(e)}")
