from typing import Mapping
from werkzeug import Request, Response
from dify_plugin import Endpoint


class EntryEndpoint(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the endpoint with the given request.
        """
        if settings.get("is_cloud"):
            return Response(
                "Sorry, cloud version is not supported for now. Please use this Cron plugin for self-hosted Dify."
            )
        return Response(
            '<html><head></head><body>Redirecting to main menu... <meta http-equiv="refresh" content="1;URL=./cron/status"></body></html>',
            status=200,
            content_type="text/html",
        )
