from collections.abc import Generator
from typing import Any, Dict

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from util.dingtalk_yida_utils import get_access_token

GET_FORM_INSTANCE_URL = "https://api.dingtalk.com/v1.0/yida/forms/instances/{form_instance_id}"


class GetFormInstanceTool(Tool):
    def _invoke(
            self,
            tool_parameters: Dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        try:
            form_instance_id = tool_parameters['form_instance_id']
            app_type = tool_parameters['app_type']
            system_token = tool_parameters['system_token']
            yida_user_id = tool_parameters['user_id']
        except KeyError as ke:
            yield self.create_text_message(text=f"Missing required parameter: {ke}")

        access_token = get_access_token(
            self.runtime.credentials.get('app_key'),
            self.runtime.credentials.get('app_secret')
        )
        if not access_token:
            yield self.create_text_message(text="Authentication failed: Access token is missing.")

        form_headers = {
            "x-acs-dingtalk-access-token": access_token,
            "Content-Type": "application/json"
        }

        form_url = GET_FORM_INSTANCE_URL.format(form_instance_id=form_instance_id)

        query_params = {
            "appType": app_type,
            "systemToken": system_token,
            "userId": yida_user_id,
        }

        try:
            response = requests.get(form_url, headers=form_headers, params=query_params)
            response.raise_for_status()
            form_result = response.json()
            yield self.create_json_message(form_result)
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(text=f"Failed to retrieve form instance: {str(e)}")
