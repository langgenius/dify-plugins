import json
from collections.abc import Generator
from typing import Any, Dict

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from util.dingtalk_yida_utils import get_access_token

FORM_IDS_QUERY_URL = "https://api.dingtalk.com/v1.0/yida/forms/instances/ids/query"


class BatchGetFormInstancesTool(Tool):
    def _invoke(
            self,
            tool_parameters: Dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        try:
            form_uuid = tool_parameters['form_uuid']
            app_type = tool_parameters['app_type']
            system_token = tool_parameters['system_token']
            form_instance_id_list_str = tool_parameters['form_instance_id_list']
            yida_user_id = tool_parameters['user_id']

            need_form_instance_value = tool_parameters.get('need_form_instance_value')

            form_instance_id_list = json.loads(form_instance_id_list_str)
            if not isinstance(form_instance_id_list, list) or not all(
                    isinstance(item, str) for item in form_instance_id_list
            ):
                raise ValueError("form_instance_id_list must be a JSON array of strings.")
        except json.JSONDecodeError:
            yield self.create_text_message(
                text="Invalid JSON format for form_instance_id_list. Please provide a valid JSON array string."
            )
        except KeyError as ke:
            yield self.create_text_message(text=f"Missing required parameter: {ke}")
        except ValueError as ve:
            yield self.create_text_message(text=str(ve))

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
            "formUuid": form_uuid,
            "appType": app_type,
            "systemToken": system_token,
            "formInstanceIdList": form_instance_id_list,
            "userId": yida_user_id
        }

        if need_form_instance_value is not None:
            form_payload["needFormInstanceValue"] = need_form_instance_value

        try:
            response = requests.post(FORM_IDS_QUERY_URL, headers=form_headers, json=form_payload)
            response.raise_for_status()
            form_result = response.json()
            yield self.create_json_message(form_result)
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(text=f"Failed to batch retrieve form instances: {str(e)}")
