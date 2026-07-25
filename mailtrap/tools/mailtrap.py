import json
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class MailtrapTool(Tool):
    def _invoke(self, tool_parameters: dict) -> ToolInvokeMessage:
        api_token = self.runtime.credentials.get("api_token")
        account_id = self.runtime.credentials.get("account_id")
        to_email = tool_parameters.get("to_email")
        subject = tool_parameters.get("subject")
        body = tool_parameters.get("body")
        from_email = tool_parameters.get("from_email", f"noreply@mailtrap.io")
        sandbox = tool_parameters.get("sandbox", False)

        if sandbox:
            inbox_id = self.runtime.credentials.get("inbox_id", "")
            url = f"https://sandbox.api.mailtrap.io/api/send/{inbox_id}"
        else:
            url = "https://send.api.mailtrap.io/api/send"

        payload = {
            "from": {"email": from_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "html": body,
        }

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return self.create_text_message(
                f"Email sent successfully to {to_email}"
            )
        else:
            return self.create_text_message(
                f"Failed to send email: {response.status_code} - {response.text}"
            )
