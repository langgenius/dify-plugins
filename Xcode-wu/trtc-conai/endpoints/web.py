import contextlib
import time
from collections.abc import Mapping

from werkzeug import Request, Response

from dify_plugin import Endpoint
import os


class WebStatic(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the endpoint with the given request.
        """
        # raise Exception(values.items())
        file = values.get("file")
        content_type = "text/html"

        if file.endswith(".js"):
            content_type = "application/javascript; charset=UTF-8"
        elif file.endswith(".css"):
            content_type = "text/css; charset=UTF-8"
        elif file.endswith(".svg"):
            content_type = "image/svg+xml; charset=utf-8"

        if file is None:
            return Response("File is required", status=400)


        with open(os.path.join(os.path.dirname(__file__), "web", "release", file), "r", encoding="utf-8") as f:
            return Response(
                # f.read().replace("%%TIMESTAMP%%", f"{current_timestamp}"),
                f.read(),
                status=200,
                content_type=content_type,
            )
