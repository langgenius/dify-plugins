import json
from collections.abc import Generator
from typing import Any, Dict

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from util.dingtalk_yida_utils import get_access_token

BATCH_REMOVE_URL = "https://api.dingtalk.com/v1.0/yida/forms/instances/batchRemove"


class BatchDeleteFormInstancesTool(Tool):
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

            asynchronous_execution = tool_parameters.get('asynchronous_execution')
            execute_expression = tool_parameters.get('execute_expression')

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

        if asynchronous_execution is not None:
            form_payload["asynchronousExecution"] = asynchronous_execution

        if execute_expression is not None:
            form_payload["executeExpression"] = execute_expression

        try:
            response = requests.post(BATCH_REMOVE_URL, headers=form_headers, json=form_payload)
            response.raise_for_status()
            yield self.create_text_message("success")
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(text=f"Failed to batch delete form instances: {str(e)}")
