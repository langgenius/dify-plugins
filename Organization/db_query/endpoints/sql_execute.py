import json
from collections.abc import Mapping

from flask import Request, Response
from dify_plugin import Endpoint
from dify_plugin.entities.tool import ToolInvokeMessage


class SQLEndpoint(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        inner_tool = {"inner_tool": "sql_execute"}
        merged_json = {**r.json,**settings, **inner_tool}
        result = self.session.tool.invoke_builtin_tool(
            provider="fly/db_query/db_query",
            tool_name="sql_execute",
            parameters=merged_json,
        )
        for message in result:
            if message.type == ToolInvokeMessage.MessageType.JSON:
                content = message.message.to_dict().get("json_object")
                return Response(
                    json.dumps(content),
                    status=200,
                    content_type="application/json",
                )
            elif message.type == ToolInvokeMessage.MessageType.BLOB:
                headers = {
                    "Content-Type": message.meta.get(
                        "mime_type", "application/octet-stream"
                    ),
                    "Content-Disposition": f'attachment; filename="{message.meta.get("filename")}"',
                }

                return Response(message.message.blob, status=200, headers=headers)
            else:
                # ToolInvokeMessage.MessageType.TEXT
                return Response(message.message.text, status=200)
