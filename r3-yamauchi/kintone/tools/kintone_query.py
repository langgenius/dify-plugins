from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class KintoneTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        ※ kintone に query を投げてレコードを取得する
        """
        query_str = tool_parameters.get("query", "").strip()
        if not query_str:
            yield self.create_text_message("query文字列を指定してください。")
            return

        kintone_domain = self.runtime.credentials.get("kintone_domain")
        if not kintone_domain:
            yield self.create_text_message("cybozu.com ドメインを指定してください。")
            return

        kintone_app_id = self.runtime.credentials.get("kintone_app_id")
        if not kintone_app_id:
            yield self.create_text_message("kintone アプリIDを指定してください。")
            return

        kintone_api_token = self.runtime.credentials.get("kintone_api_token")
        if not kintone_api_token:
            yield self.create_text_message("kintone APIトークンを指定してください。")
            return

        headers = {
            "X-Cybozu-API-Token": kintone_api_token,
            "Content-Type": "application/json",
            "X-HTTP-Method-Override": "GET"
        }

        url = f"https://{kintone_domain}/k/v1/records.json"

        # ページネーション用のパラメータ
        limit = 500  # 1回のリクエストで取得する最大件数を500件に指定
        offset = 0   # 取得開始位置
        all_records = []

        try:
            while True:
                request_body = {
                    "app": kintone_app_id,
                    "query": query_str,
                    "limit": limit,
                    "offset": offset
                }

                # GETの代わりにPOSTメソッドを使用
                response = requests.post(
                    url,
                    headers=headers,
                    json=request_body,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                records = data.get("records", [])

                # レコードが存在しなければループを抜ける
                if not records:
                    break

                all_records.extend(records)

                # 取得件数が limit 未満なら、これ以上レコードは存在しないと判断
                if len(records) < limit:
                    break

                # 次のページへ
                offset += limit

            if not all_records:
                yield self.create_text_message(f"'{query_str}' に一致するレコードは見つかりませんでした。")
                return

            # レコードの全フィールドを取得してテキストを作成
            lines = []
            for record in all_records:
                lines.append(f"検索クエリ: {query_str}")

                # レコードの各フィールドを処理
                for field_code, field_data in record.items():
                    # フィールドの値を取得
                    field_value = get_field_value(record, field_code)
                    lines.append(f"{field_code}: {field_value}")

                lines.append("")  # レコード間の区切りとして空行を追加

            result_str = "\n".join(lines)
            yield self.create_text_message(result_str)

        except Exception as e:
            yield self.create_text_message(f"kintone API 呼び出し中にエラーが発生しました: {str(e)}")

def get_field_value(record: dict, field_code: str) -> str:
    """
    kintone レコードから指定されたフィールドの値を取り出して返す関数。
    フィールドが存在しない、または値が空の場合は "不明" を返す。

    Args:
        record (dict): kintoneのレコードデータ
        field_name (str): 取得するフィールドのフィールドコード

    Returns:
        str: フィールドの値、または "不明"
    """
    field = record.get(field_code)
    if not field:
        return "不明"

    # フィールドの種類に応じて値を取得
    if isinstance(field, dict) and "value" in field:
        return field["value"] if field["value"] else "不明"
    elif isinstance(field, (str, int, float)):
        return str(field)
    elif isinstance(field, list):
        # 複数選択フィールドなどの配列の場合
        return ", ".join(map(str, field))
    return "不明"
