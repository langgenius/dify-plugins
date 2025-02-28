import json
from collections.abc import Generator
from typing import Any, Dict, List, Optional, Union

import requests
from requests.exceptions import RequestException, Timeout, HTTPError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class KintoneTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # kintone の認証情報およびアプリIDを取得
        kintone_domain = tool_parameters.get("kintone_domain")
        if not kintone_domain:
            yield self.create_text_message("kintone ドメインが見つかりません。kintone_domainパラメータを確認してください。")
            return

        kintone_app_id = tool_parameters.get("kintone_app_id")
        if not kintone_app_id:
            yield self.create_text_message("kintone アプリIDが見つかりません。kintone_app_idパラメータを確認してください。")
            return

        kintone_api_token = tool_parameters.get("kintone_api_token")
        if not kintone_api_token:
            yield self.create_text_message("kintone APIトークンが見つかりません。kintone_api_tokenパラメータを確認してください。")
            return

        # クエリ文字列の取得
        query_str = tool_parameters.get("query", "").strip()

        # フィールドリストの処理
        fields_list = None
        fields_param = tool_parameters.get("fields")
        if fields_param:
            # カンマ区切り文字列をリストに変換
            fields_list = [field.strip() for field in fields_param.split(',')]

        # APIリクエスト用のヘッダー設定
        headers = {
            "X-Cybozu-API-Token": kintone_api_token,
            "Content-Type": "application/json",
            "X-HTTP-Method-Override": "GET"  # GET メソッドのオーバーライドを指定
        }

        # kintone のレコード取得 API のエンドポイント
        url = f"https://{kintone_domain}/k/v1/records.json"

        # ページネーション用のパラメータ設定
        limit = 500  # 1回のリクエストで取得できる最大件数を500件に設定
        offset = 0   # 取得開始位置
        all_records = []

        try:
            # ページネーションを使用して全レコードを取得
            while True:
                # クエリ文字列にlimitとoffsetを追加
                query = query_str
                if query:
                    query += f" limit {limit} offset {offset}"
                else:
                    query = f"limit {limit} offset {offset}"

                # POSTリクエスト用のJSONボディを作成
                request_body = {
                    "app": kintone_app_id,
                    "query": query,
                }
                
                # 事前に処理したfieldsリストがある場合は追加
                if fields_list:
                    request_body["fields"] = fields_list

                # APIリクエストの実行
                try:
                    # GETの代わりにPOSTメソッドを使用
                    response = requests.post(
                        url,
                        headers=headers,
                        json=request_body,  # paramsの代わりにjsonを使用
                        timeout=10  # タイムアウトを10秒に設定
                    )
                    # HTTPエラーがあれば例外を発生
                    response.raise_for_status()
                except Timeout:
                    yield self.create_text_message("kintone APIへのリクエストがタイムアウトしました。ネットワーク接続を確認してください。")
                    return
                except HTTPError as e:
                    # HTTPステータスコードに基づいたエラーメッセージ
                    status_code = e.response.status_code if hasattr(e, 'response') else 'unknown'
                    if status_code == 401:
                        yield self.create_text_message("kintone APIの認証に失敗しました。APIトークンを確認してください。")
                    elif status_code == 403:
                        yield self.create_text_message("kintone APIへのアクセス権限がありません。APIトークンの権限を確認してください。")
                    elif status_code == 404:
                        yield self.create_text_message("指定されたkintoneアプリが見つかりません。アプリIDを確認してください。")
                    elif status_code >= 500:
                        yield self.create_text_message(f"kintoneサーバーでエラーが発生しました（ステータスコード: {status_code}）。")
                    else:
                        yield self.create_text_message(f"kintone APIリクエスト中にHTTPエラーが発生しました: {str(e)}")
                    return
                except RequestException as e:
                    yield self.create_text_message(f"kintone APIへの接続中にエラーが発生しました: {str(e)}")
                    return

                # レスポンスのJSONデータを解析
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    yield self.create_text_message("kintone APIからの応答を解析できませんでした。無効なJSONレスポンスです。")
                    return

                # レコードデータの取得と検証
                records = data.get("records", [])

                # レコードが存在しなければループを抜ける
                if not records:
                    break

                # 取得したレコードを結果リストに追加
                all_records.extend(records)

                # 取得件数が limit 未満なら、これ以上レコードは存在しないと判断
                if len(records) < limit:
                    break

                # 次のページへ
                offset += limit

            # 検索結果の有無を確認
            if not all_records:
                yield self.create_text_message(f"'{query_str}' に一致するレコードは見つかりませんでした。")
                return

            # レコードの全フィールドを取得してテキストを作成
            lines = []
            lines.append(f"取得したレコード件数: {len(all_records)}")

            # 各レコードの処理
            for i, record in enumerate(all_records):
                record_lines = []
                # レコードの各フィールドを処理
                for field_name, field_data in record.items():
                    # フィールドの値を取得
                    field_value = get_field_value(record, field_name)
                    # 空の値や"不明"の場合はスキップ
                    if field_value and field_value != "不明":
                        record_lines.append(f"{field_name}: {field_value}")
                
                # 空でない場合のみ追加
                if record_lines:
                    # 最初のレコード以外は区切り線を追加
                    if i > 0:
                        lines.append("---")  # レコード間の区切り
                    lines.extend(record_lines)

            # 結果をテキスト形式に変換
            result_str = "\n".join(lines)
            yield self.create_text_message(result_str)

        except Exception as e:
            # 予期しないエラーの処理
            error_message = f"kintone API 呼び出し中に予期しないエラーが発生しました: {str(e)}"
            yield self.create_text_message(error_message)


def get_field_value(record: Dict[str, Any], field_name: str) -> str:
    """
    kintone レコードから指定されたフィールドの値を取り出して返す関数。
    
    この関数は、kintoneの複雑なデータ構造を処理し、フィールドの値を取得します。
    入れ子になったデータ構造を再帰的に処理し、不要な情報（id, type）を除外します。
    フィールドが存在しない、または値が空の場合は "不明" を返します。

    Args:
        record (Dict[str, Any]): kintoneのレコードデータ
        field_name (str): 取得するフィールドの名前

    Returns:
        str: フィールドの値、または "不明"
    """
    # フィールドの取得と存在確認
    field = record.get(field_name)
    if field is None:
        return "不明"

    # 入れ子構造を処理する関数
    def clean_value(value: Any) -> Any:
        """
        kintoneの入れ子構造を再帰的に処理し、必要な値のみを抽出する内部関数。
        
        Args:
            value: 処理する値（任意の型）
            
        Returns:
            Any: 処理された値
        """
        # 辞書型の処理
        if isinstance(value, dict):
            # idキーのみの辞書は空文字を返す
            if set(value.keys()) == {"id"}:
                return ""
            
            # valueキーがある場合はその中身を処理
            if "value" in value:
                # typeキーは無視
                inner_value = value["value"]
                return clean_value(inner_value)
            
            # その他の辞書は再帰的に処理
            result = {}
            for k, v in value.items():
                # type と id キーは無視
                if k not in ["type", "id"]:
                    cleaned = clean_value(v)
                    # 空でない値、または0やFalseなど有効な値の場合は追加
                    if cleaned is not None and (cleaned != "" or isinstance(cleaned, (int, float, bool))):
                        result[k] = cleaned
            
            # 空の辞書は空文字を返す
            return result if result else ""
        
        # リスト型の処理
        elif isinstance(value, list):
            # リスト内の各要素を処理
            result = []
            for item in value:
                # idとvalueを持つ辞書の場合、valueの中身のみを処理
                if isinstance(item, dict) and "id" in item and "value" in item:
                    cleaned = clean_value(item["value"])
                else:
                    cleaned = clean_value(item)
                
                # 空でない値、または0やFalseなど有効な値の場合は追加
                if cleaned is not None and (cleaned != "" or isinstance(cleaned, (int, float, bool))):
                    result.append(cleaned)
            
            # 空のリストは空文字を返す
            return result if result else ""
        
        # 基本型はそのまま返す
        return value

    # 処理した値を取得
    cleaned_value = clean_value(field)
    
    # 空の辞書やリストの場合は「不明」を返す
    if cleaned_value == "" and isinstance(cleaned_value, (dict, list)):
        return "不明"
    
    # 0やFalseなどの有効な値を適切に処理
    if cleaned_value == 0 or cleaned_value is False:
        return str(cleaned_value)
    
    # 空の値は「不明」を返す
    if not cleaned_value and not isinstance(cleaned_value, (int, float, bool)):
        return "不明"
    
    # 辞書とリストはJSON文字列に変換
    if isinstance(cleaned_value, (dict, list)):
        try:
            # 日本語などの非ASCII文字をエスケープせずに処理
            return json.dumps(cleaned_value, ensure_ascii=False)
        except (TypeError, ValueError):
            # JSON変換に失敗した場合は文字列表現を返す
            return str(cleaned_value)
    
    # その他の型は文字列に変換
    return str(cleaned_value)
