from collections.abc import Generator
from typing import Any, Dict

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from util.dingtalk_yida_utils import get_access_token

DELETE_FORM_INSTANCE_URL = "https://api.dingtalk.com/v1.0/yida/forms/instances"


class DeleteFormInstanceTool(Tool):
    def _invoke(
            self,
            tool_parameters: Dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        try:
            app_type = tool_parameters['app_type']
            system_token = tool_parameters['system_token']
            yida_user_id = tool_parameters['user_id']
            form_instance_id = tool_parameters['form_instance_id']
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

        params = {
            "appType": app_type,
            "systemToken": system_token,
            "userId": yida_user_id,
            "formInstanceId": form_instance_id
        }

        try:
            response = requests.delete(DELETE_FORM_INSTANCE_URL, headers=form_headers, params=params)
            response.raise_for_status()
            yield self.create_text_message("success")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(text=f"Failed to delete form instance: {str(e)}")
