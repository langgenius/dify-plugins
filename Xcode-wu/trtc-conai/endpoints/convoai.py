import base64
from collections.abc import Mapping
import json
from typing import Optional

from werkzeug import Request, Response
import requests
from dify_plugin import Endpoint
from agora_token_builder import RtcTokenBuilder
import time


class ConvoAI(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the endpoint with the given request.
        """
        route = values.get("action")

        if route == "dify-completion":
            return self._dify_completion(r, values, settings)
        elif route == "convoai-start":
            return self._convoai_start(r, values, settings)
        elif route == "convoai-stop":
            return self._convoai_stop(r, values, settings)

        return Response("no action found", status=404, content_type="text/html")

    def _dify_completion(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        app: Optional[dict] = settings.get("app")
        if not app:
            return Response("App is required", status=400)

        api_key = settings.get("api_key") or ""
        header_authorization = r.headers.get("Authorization")
        if api_key != "":
            authorization = f"Bearer {api_key}"
            if authorization != header_authorization:
                return Response("Unauthorized", status=401)


        data = r.get_json()
        query = data.get("query")
        conversation_id = data.get("conversation_id")

        if not query:
            return Response("Query is required", status=400)

        def generator():
            response = self.session.app.chat.invoke(
                app_id=app.get("app_id"),
                query=query,
                inputs={},
                conversation_id=conversation_id,
                response_mode="streaming",
            )

            for chunk in response:
                yield f"data:{json.dumps(chunk)}\n\n"

        return Response(generator(), status=200, content_type="text/event-stream")

    def _convoai_start(self, r: Request, values: Mapping, settings: Mapping) -> Response:

        # Define the URL for the request
        data = r.get_json()

        # Define mandatory parameters that must exist in data
        mandatory_data_params = ["channel"]

        # Check for missing mandatory parameters
        missing_data_params = [param for param in mandatory_data_params if not data.get(param)]
        if missing_data_params:
            raise ValueError(f"Missing mandatory parameters: {', '.join(missing_data_params)}")

        # body params
        base_url = data.get("base_url")
        dify_url = f"{base_url}/convoai/dify-completion"
        dify_chat_user = data.get("dify_chat_user") or "user"
        agent_rtc_uid = data.get("agent_rtc_uid") or 10000
        channel = data.get("channel")

        # app params
        agora_app_id = settings.get("agora_app_id")
        agora_app_cert = settings.get("agora_app_cert")
        agora_restful_customer_id = settings.get("agora_restful_customer_id")
        agora_restful_customer_secret = settings.get("agora_restful_customer_secret")
        greeting_message = settings.get("greeting_message") or ""
        failure_message = settings.get("failure_message") or "Something is wrong with the system. Please try again later."

        api_key = settings.get("api_key") or ""

        asr_language = settings.get("asr_language") or "en-US"

        tts_vendor = settings.get("tts_vendor")
        tts_params = json.loads(settings.get("tts_params", "{}"))
        asr_vendor = settings.get("asr_vendor")
        asr_language = settings.get("asr_language") or "en-US"
        asr_params_str = settings.get("asr_params", None)
        asr_params = json.loads(asr_params_str) if asr_params_str else None


        # Combine the credentials
        credentials = f"{agora_restful_customer_id}:{agora_restful_customer_secret}"
        # Encode in Base64
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        agora_token = ""
        if agora_app_id and agora_app_cert:
            # Get the current time in seconds since Unix epoch
            current_timestamp = int(time.time())
            # Add 1 hour (3600 seconds)
            privilegeExpireTs = current_timestamp + 3600
            agora_token = RtcTokenBuilder.buildTokenWithUid(agora_app_id, agora_app_cert, channel, agent_rtc_uid, 1, privilegeExpireTs)

        # Define the data (payload)
        data = {
            "name": channel,
            "properties": {
                "channel": channel,
                "token": agora_token,
                "agent_rtc_uid": f"{agent_rtc_uid}",
                "remote_rtc_uids": ["*"],
                "idle_timeout": 30,
                "advanced_features": {
                    "enable_aivad": False,
                    "enable_bhvs": True
                },
                "llm": {
                    "url": dify_url,
                    "api_key": api_key,
                    "system_messages": [],
                    "max_history": 10,
                    "greeting_message": greeting_message,
                    "failure_message": failure_message,
                    "params": {
                        "user": dify_chat_user
                    },
                    "style": "dify"
                },
                "tts": {
                    "vendor": tts_vendor,
                    "params": tts_params
                },
                "asr": {
                    "vendor": asr_vendor,
                    "params": asr_params,
                    "language": asr_language
                },
                "parameters": {
                    "enable_flexible": True
                }
            }
        }

        # print("Data to be sent:", json.dumps(data, indent=2))

        url = f"https://api.agora.io/api/conversational-ai-agent/v2/projects/{agora_app_id}/join"

        # raise Exception(json.dumps(data))

        # Set the headers to specify that the content is JSON
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}"
        }
        # Send the POST request
        response = requests.post(url, headers=headers, data=json.dumps(data))

        return Response(response.text, status=response.status_code, content_type="application/json")
    
    def _convoai_stop(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        data = r.get_json()
        agent_id = data.get("agent_id")
        app_id = settings.get("agora_app_id")
        credentials = f"{settings.get('agora_restful_customer_id')}:{settings.get('agora_restful_customer_secret')}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        url = f"https://api.agora.io/api/conversational-ai-agent/v2/projects/{app_id}/agents/{agent_id}/leave"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}"
        }
        response = requests.post(url, headers=headers)
        return Response(response.text, status=response.status_code, content_type="application/json")