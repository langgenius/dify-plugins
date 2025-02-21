import json
from collections.abc import Generator
from typing import Any, Dict

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from util.dingtalk_yida_utils import get_access_token

BATCH_SAVE_URL = "https://api.dingtalk.com/v1.0/yida/forms/instances/batchSave"


class BatchSaveFormInstancesTool(Tool):
    def _invoke(
            self,
            tool_parameters: Dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        try:
            form_uuid = tool_parameters['form_uuid']
            app_type = tool_parameters['app_type']
            system_token = tool_parameters['system_token']
            form_data_json_list_str = tool_parameters['form_data_json_list']
            yida_user_id = tool_parameters['user_id']

            no_execute_expression = tool_parameters.get('no_execute_expression')
            asynchronous_execution = tool_parameters.get('asynchronous_execution')
            keep_running_after_exception = tool_parameters.get('keep_running_after_exception')

            form_data_json_list = json.loads(form_data_json_list_str)
            if not isinstance(form_data_json_list, list) or not all(
                    isinstance(item, str) for item in form_data_json_list
            ):
                raise ValueError("form_data_json_list must be a JSON array of strings.")
        except json.JSONDecodeError:
            yield self.create_text_message(
                text="Invalid JSON format for form_data_json_list. Please provide a valid JSON array string."
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
            "userId": yida_user_id,
            "formDataJsonList": form_data_json_list
        }

        if no_execute_expression is not None:
            form_payload["noExecuteExpression"] = no_execute_expression

        if asynchronous_execution is not None:
            form_payload["asynchronousExecution"] = asynchronous_execution

        if keep_running_after_exception is not None:
            form_payload["keepRunningAfterException"] = keep_running_after_exception

        try:
            response = requests.post(BATCH_SAVE_URL, headers=form_headers, json=form_payload)
            response.raise_for_status()
            form_result = response.json()
            yield self.create_json_message(form_result)
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(text=f"Failed to batch save form instances: {str(e)}")
