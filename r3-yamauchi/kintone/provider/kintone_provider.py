from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class KintoneProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        kintone の認証情報（ドメイン、アプリID、APIトークン）が正しいかどうかを検証する。
        """
        kintone_domain = credentials.get("kintone_domain")
        if not kintone_domain:
            raise ToolProviderCredentialValidationError("cybozu.com ドメインを指定してください。")

        kintone_app_id = credentials.get("kintone_app_id")
        if not kintone_app_id:
            raise ToolProviderCredentialValidationError("kintone アプリIDを指定してください。")

        kintone_api_token = credentials.get("kintone_api_token")
        if not kintone_api_token:
            raise ToolProviderCredentialValidationError("kintone APIトークンを指定してください。")

        headers = {
            "X-Cybozu-API-Token": kintone_api_token,
            "Content-Type": "application/json",
            "X-HTTP-Method-Override": "GET"
        }

        url = f"https://{kintone_domain}/k/v1/app.json"

        request_body = {
            "id": kintone_app_id
        }

        try:
            resp = requests.post(
                url,
                headers=headers,
                json=request_body,
                timeout=10
            )
            resp.raise_for_status()

        except requests.exceptions.HTTPError:
            status_code = resp.status_code
            resp_text = resp.text
            print(f"[KintoneProvider] HTTPエラー {status_code}: {resp_text}")
            raise ToolProviderCredentialValidationError(
                f"無効な kintone 認証情報 (HTTP {status_code}).\nレスポンス: {resp_text}"
            )
        except requests.exceptions.RequestException as e:
            print(f"[KintoneProvider] リクエスト失敗: {e}")
            raise ToolProviderCredentialValidationError(f"kintone への接続に失敗しました: {e}")
