from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class WecondifypluginProvider(ToolProvider):
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """验证企业微信凭证"""
        try:
            corpid = credentials.get("corpid")
            corpsecret = credentials.get("corpsecret")
            
            if not corpid or not corpsecret:
                raise ToolProviderCredentialValidationError("企业ID和应用Secret不能为空")
            
            # 尝试获取access_token来验证凭证
            url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}"
            response = requests.get(url, timeout=10)
            result = response.json()
            
            if result.get("errcode") != 0:
                raise ToolProviderCredentialValidationError(
                    f"凭证验证失败: {result.get('errmsg', '未知错误')}"
                )
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
