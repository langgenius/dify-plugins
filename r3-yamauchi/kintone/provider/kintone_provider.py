from typing import Any

from dify_plugin import ToolProvider

class KintoneProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        認証情報の検証をスキップします。
        kintone_query側で指定された認証情報を使用する仕様に変更されたため、
        ここでの検証は不要になりました。
        """
        # 認証情報の検証をスキップ
        pass
