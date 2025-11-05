from collections.abc import Mapping
import json

from werkzeug import Request, Response
from dify_plugin import Endpoint
from agora_token_builder import RtcTokenBuilder
import time


class ConvoAIGet(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the endpoint with the given request.
        """
        return self._generate_token(r, values, settings)
    
    def _generate_token(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        channel = values.get("channel")
        uid = values.get("uid")

        if not channel:
            return Response("channel is required", status=400)

        if not uid:
            uid = 0

        app_id = settings.get("agora_app_id")
        app_cert = settings.get("agora_app_cert")

        if not app_id:
            return Response("App ID is required", status=400)

        token = app_id

        result = {
            "token": token,
            "app_id": app_id,
        }

        if not app_cert:
            return Response(json.dumps(result), status=200, content_type="application/json")

        # Get the current time in seconds since Unix epoch
        current_timestamp = int(time.time())
        # Add 1 hour (3600 seconds)
        privilegeExpireTs = current_timestamp + 3600
        token = RtcTokenBuilder.buildTokenWithUid(app_id, app_cert, channel, uid, 1, privilegeExpireTs)

        result = {
            "token": token,
            "app_id": app_id,
        }

        return Response(
            json.dumps(result),
            status=200,
            content_type="application/json"
        )