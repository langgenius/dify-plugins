from collections.abc import Generator
from typing import Any, Dict

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from util.dingtalk_yida_utils import get_access_token

SAVE_FORM_INSTANCE_URL = "https://api.dingtalk.com/v1.0/yida/forms/instances"


class SaveFormInstanceTool(Tool):
    def _invoke(
            self,
            tool_parameters: Dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        try:
            app_type = tool_parameters['app_type']
            system_token = tool_parameters['system_token']
            yida_user_id = tool_parameters['user_id']
            form_uuid = tool_parameters['form_uuid']
            form_data_json = tool_parameters['form_data_json']
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

        form_payload = {
            "appType": app_type,
            "systemToken": system_token,
            "userId": yida_user_id,
            "formUuid": form_uuid,
            "formDataJson": form_data_json
        }

        try:
            response = requests.post(SAVE_FORM_INSTANCE_URL, headers=form_headers, json=form_payload)
            response.raise_for_status()
            form_result = response.json()
            yield self.create_json_message(form_result)
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(text=f"Failed to create form instance: {str(e)}")
