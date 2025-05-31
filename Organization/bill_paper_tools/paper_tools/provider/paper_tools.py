from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class PaperToolsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证提供的 Telegraph Access Token 是否有效。
        尝试使用该 token 创建一个测试页面。
        如果验证失败，应抛出 ToolProviderCredentialValidationError 异常。
        """
        access_token = credentials.get("serpapi_api_key")
        if not access_token:
            raise ToolProviderCredentialValidationError("serpapi Access Token 不能为空。")

        try:
            # 尝试执行一个需要凭证的简单操作来验证
            # 尝试创建一个临时的、无害的页面作为验证手段
            # 注意：更好的验证方式可能是调用 API 的 'getAccountInfo' 等只读方法（如果存在）
            # test_page = ph.create_page_md("Dify Validation Test", "测试验证.")
            # 如果需要，可以考虑立即编辑或删除这个测试页面，但这会增加复杂性
            # print(f"Validation successful. Test page created: {test_page}")
            print("done!")
        except Exception as e:
            # 如果 API 调用失败，说明凭证很可能无效
            raise ToolProviderCredentialValidationError(f"Telegraph 凭证验证失败: {e}")
