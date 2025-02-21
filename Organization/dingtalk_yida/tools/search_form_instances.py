from collections.abc import Generator
from typing import Any, Dict

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from util.dingtalk_yida_utils import get_access_token

SEARCH_FORM_INSTANCES_URL = "https://api.dingtalk.com/v1.0/yida/forms/instances/ids/{app_type}/{form_uuid}"


class SearchFormInstancesTool(Tool):
    def _invoke(
            self,
            tool_parameters: Dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        try:
            app_type = tool_parameters['app_type']
            form_uuid = tool_parameters['form_uuid']
            system_token = tool_parameters['system_token']
            yida_user_id = tool_parameters['user_id']

            page_number = tool_parameters.get('page_number')
            page_size = tool_parameters.get('page_size')
            modified_to_time_gmt = tool_parameters.get('modified_to_time_gmt')
            modified_from_time_gmt = tool_parameters.get('modified_from_time_gmt')
            search_field_json = tool_parameters.get('search_field_json')
            originator_id = tool_parameters.get('originator_id')
            create_to_time_gmt = tool_parameters.get('create_to_time_gmt')
            create_from_time_gmt = tool_parameters.get('create_from_time_gmt')
        except KeyError as ke:
            yield self.create_text_message(text=f"Missing required parameter: {ke}")

        access_token = get_access_token(
            self.runtime.credentials.get('app_key'),
            self.runtime.credentials.get('app_secret')
        )
        if not access_token:
            yield self.create_text_message(text="认证失败：缺少访问令牌。")

        form_headers = {
            "x-acs-dingtalk-access-token": access_token,
            "Content-Type": "application/json"
        }

        form_url = SEARCH_FORM_INSTANCES_URL.format(app_type=app_type, form_uuid=form_uuid)

        form_payload = {
            "systemToken": system_token,
            "userId": yida_user_id
        }

        if page_number is not None:
            form_payload["pageNumber"] = page_number

        if page_size is not None:
            form_payload["pageSize"] = page_size

        if modified_to_time_gmt:
            form_payload["modifiedToTimeGMT"] = modified_to_time_gmt

        if modified_from_time_gmt:
            form_payload["modifiedFromTimeGMT"] = modified_from_time_gmt

        if search_field_json:
            form_payload["searchFieldJson"] = search_field_json

        if originator_id:
            form_payload["originatorId"] = originator_id

        if create_to_time_gmt:
            form_payload["createToTimeGMT"] = create_to_time_gmt

        if create_from_time_gmt:
            form_payload["createFromTimeGMT"] = create_from_time_gmt

        try:
            response = requests.post(form_url, headers=form_headers, json=form_payload)
            response.raise_for_status()
            form_result = response.json()
            yield self.create_json_message(form_result)
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(text=f"Failed to search form instances: {str(e)}")
