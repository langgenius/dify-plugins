from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.url_to_markdown import UrlToMarkdownTool


class UrlToMarkdownProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 由于我们的工具不需要特殊的API凭据，所以这里只是简单地测试工具能否正常初始化
            # 使用一个简单的URL进行测试
            test_url = "https://example.com"
            tool = UrlToMarkdownTool.from_credentials(credentials)
            
            # 尝试调用工具，但不需要处理结果
            # 注意：这里我们只是验证工具能否正常初始化，不实际执行爬取操作
            # 因为爬取操作可能会比较耗时
            # 如果需要完整测试，可以取消下面的注释
            # for _ in tool.invoke(tool_parameters={"url": test_url}):
            #     pass
                
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"工具验证失败: {str(e)}")
