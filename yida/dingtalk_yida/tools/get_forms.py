from collections.abc import Generator
from typing import Any, Dict

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from util.dingtalk_yida_utils import get_access_token

GET_FORMS_URL = "https://api.dingtalk.com/v1.0/yida/forms"


class GetFormsTool(Tool):
    def _invoke(
            self,
            tool_parameters: Dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        try:
            app_type = tool_parameters['app_type']
            system_token = tool_parameters['system_token']
            yida_user_id = tool_parameters['user_id']
        except KeyError as ke:
            yield self.create_text_message(text=f"Missing required parameter: {ke}")

        form_types = tool_parameters.get('form_types')
        page_size = tool_parameters.get('page_size')
        page_number = tool_parameters.get('page_number')

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

        query_params = {
            "appType": app_type,
            "systemToken": system_token,
            "userId": yida_user_id
        }

        if form_types:
            query_params["formTypes"] = form_types

        if page_size is not None:
            query_params["pageSize"] = page_size

        if page_number is not None:
            query_params["pageNumber"] = page_number

        try:
            response = requests.get(GET_FORMS_URL, headers=form_headers, params=query_params)
            response.raise_for_status()
            form_result = response.json()
            yield self.create_json_message(form_result)
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(text=f"Failed to retrieve forms: {str(e)}")
