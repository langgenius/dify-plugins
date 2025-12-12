from collections.abc import Generator
from typing import Any, Dict, List, Optional

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# ========== 配置 ==========
BASE_URL = "http://10.19.29.140:9080"


class OntologyTool(Tool):
    """Dify 插件：封装原生的本体服务请求逻辑为三个可调用 action：

    - get_object_types: 获取本体对象类型（对应原 get_object_types）
    - get_ontology_list: 查询本体列表（对应原 get_ontology_list）
    - get_ontology_object_details: 获取本体对象详情（对应原 get_ontology_object_details）

    调用方式示例：
    {
        "action": "get_object_types",
        "ontology_id": "xxx",
        "interface_id": "yyy",
        # 可选 api_key，若未提供则使用 runtime.credentials["api_key"]
    }
    """

    def _get_api_key(self, tool_parameters: Dict[str, Any]) -> str:
        api_key = tool_parameters.get("api_key")
        if not api_key:
            api_key = self.runtime.credentials.get("api_key")
        if not api_key:
            raise RuntimeError({"message": "api_key 未提供"})
        return api_key

    def _get_object_types(self, api_key: str, ontology_id: str, interface_id: Optional[str]) -> List[Dict]:
        url = f"{BASE_URL}/ontology/_api/ontology/object/type/findAll"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{api_key}"
        }
        params = {"ontologyId": ontology_id}
        if interface_id is not None:
            params["interfaceId"] = interface_id

        resp = requests.get(url, headers=headers, params=params, timeout=10, allow_redirects=False)
        if resp.status_code in (401, 403):
            raise RuntimeError({"message": "api_key不正确或无访问权限", "status_code": resp.status_code})
        if resp.status_code in (301, 302, 303, 307, 308):
            raise RuntimeError({
                "message": "api_key不正确或缺少登录态，被重定向到登录页",
                "status_code": resp.status_code,
                "location": resp.headers.get("Location"),
            })
        resp.raise_for_status()

        try:
            result = resp.json()
        except Exception:
            raise RuntimeError({
                "message": "下游返回非 JSON 内容",
                "status_code": resp.status_code,
                "content_type": resp.headers.get("Content-Type"),
                "text": resp.text[:2000],
            })

        if not result.get("success"):
            raise RuntimeError(result)

        return result["data"]

    def _get_ontology_list(self, api_key: str, keyword: Optional[str], status: Optional[int], page: Optional[int], limit: Optional[int]) -> List[Dict[str, Any]]:
        url = f"{BASE_URL}/ontology/_api/ontology/list"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{api_key}"
        }

        params: Dict[str, Any] = {}
        if keyword is not None:
            params["keyword"] = keyword
        if status is not None:
            if status not in (0, 1):
                raise ValueError("status 必须是 0 或 1")
            params["status"] = status
        if page is not None:
            if page < 0:
                raise ValueError("page 必须 >= 0")
            params["page"] = page
        if limit is not None:
            if limit <= 0:
                raise ValueError("limit 必须 > 0")
            params["limit"] = limit

        resp = requests.get(url, headers=headers, params=params, timeout=10, allow_redirects=False)
        if resp.status_code in (401, 403):
            raise RuntimeError({"message": "api_key不正确或无访问权限", "status_code": resp.status_code})
        if resp.status_code in (301, 302, 303, 307, 308):
            raise RuntimeError({
                "message": "api_key不正确或缺少登录态，被重定向到登录页",
                "status_code": resp.status_code,
                "location": resp.headers.get("Location"),
            })
        resp.raise_for_status()

        try:
            result = resp.json()
        except Exception:
            raise RuntimeError({
                "message": "下游返回非 JSON 内容",
                "status_code": resp.status_code,
                "content_type": resp.headers.get("Content-Type"),
                "text": resp.text[:2000],
            })

        if not result.get("success"):
            raise RuntimeError(result)

        return result.get("data", {}).get("content", [])

    def _get_ontology_object_details(
        self,
        api_key: str,
        ontology_name: str,
        object_name: str,
        return_attrs: Optional[List[str]],
        where_sql: Optional[str],
        where_params: Optional[Dict[str, Any]],
        order_by: Optional[str],
        page_size: Optional[int],
        page_token: Optional[str],
    ) -> Dict:
        url = f"{BASE_URL}/ontology/_api/ontology/object/apis/find"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{api_key}",
        }

        body: Dict[str, Any] = {
            "ontology_name": ontology_name,
            "object_name": object_name,
            "return_attrs": return_attrs,
            "where_sql": where_sql,
            "where_params": where_params,
            "order_by": order_by,
            "page_size": page_size,
            "page_token": page_token,
        }
        body = {k: v for k, v in body.items() if v is not None}

        resp = requests.post(url, headers=headers, json=body, timeout=10)
        if resp.status_code in (401, 403):
            raise RuntimeError({"message": "api_key不正确或无访问权限", "status_code": resp.status_code})
        if resp.status_code in (301, 302, 303, 307, 308):
            raise RuntimeError({
                "message": "api_key不正确或缺少登录态，被重定向到登录页",
                "status_code": resp.status_code,
                "location": resp.headers.get("Location"),
            })
        resp.raise_for_status()

        try:
            result = resp.json()
        except Exception:
            raise RuntimeError({
                "message": "下游返回非 JSON 内容",
                "status_code": resp.status_code,
                "content_type": resp.headers.get("Content-Type"),
                "text": resp.text[:2000],
            })

        success_flag = False
        if isinstance(result, dict):
            if result.get("success") is True:
                success_flag = True
            elif result.get("status") == "success" or str(result.get("code")) == "200":
                success_flag = True

        if not success_flag:
            raise RuntimeError(result)

        return result.get("data", result)

    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        action = "get_ontology_object_details"
        if not action:
            yield self.create_json_message({"success": False, "error": "必须提供 action"})
            return

        try:
            api_key = self._get_api_key(tool_parameters)

            if action == "get_object_types":
                ontology_id = tool_parameters.get("ontology_id")
                interface_id = tool_parameters.get("interface_id")
                if not ontology_id:
                    raise ValueError("ontology_id 必填")
                result = self._get_object_types(api_key, ontology_id, interface_id)

            elif action == "get_ontology_list":
                keyword = tool_parameters.get("keyword")
                status = tool_parameters.get("status")
                page = tool_parameters.get("page")
                limit = tool_parameters.get("limit")
                result = self._get_ontology_list(api_key, keyword, status, page, limit)

            elif action == "get_ontology_object_details":
                ontology_name = tool_parameters.get("ontology_name")
                object_name = tool_parameters.get("object_name")
                if not ontology_name or not object_name:
                    raise ValueError("ontology_name 和 object_name 必填")
                return_attrs = tool_parameters.get("return_attrs")
                where_sql = tool_parameters.get("where_sql")
                where_params = tool_parameters.get("where_params")
                order_by = tool_parameters.get("order_by")
                page_size = tool_parameters.get("page_size")
                page_token = tool_parameters.get("page_token")
                result = self._get_ontology_object_details(
                    api_key,
                    ontology_name,
                    object_name,
                    return_attrs,
                    where_sql,
                    where_params,
                    order_by,
                    page_size,
                    page_token,
                )

            else:
                raise ValueError(f"未知 action: {action}")

            yield self.create_json_message({"success": True, "result": result})

        except Exception as e:
            # 在插件层返回可序列化的错误信息，便于上游使用与展示
            err_payload = {"success": False, "error": None}
            if isinstance(e, RuntimeError) and isinstance(e.args[0], dict):
                err_payload["error"] = e.args[0]
            else:
                err_payload["error"] = str(e)
            yield self.create_json_message(err_payload)