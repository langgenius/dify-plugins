import json
from typing import Mapping

from dify_plugin import Endpoint
from volcengine.viking_knowledgebase import VikingKnowledgeBaseService
from werkzeug import Request, Response


class VikingdbKnowledgeBaseEndpoint(Endpoint):
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the endpoint with the given request.
        """
        # Parse JSON from the incoming request
        body = r.json

        resource_id = body.get("knowledge_id")

        query = body.get("query")

        # Extract retrieval settings with sensible defaults
        retrieval_settings = body.get("retrieval_setting")
        top_k = retrieval_settings.get("top_k")
        score_threshold = retrieval_settings.get("score_threshold", .0)

        viking_knowledgebase_service = VikingKnowledgeBaseService(host="api-knowledgebase.mlp.cn-beijing.volces.com",
                                                                  scheme="https", connection_timeout=30,
                                                                  socket_timeout=30)
        viking_knowledgebase_service.set_ak(settings.get("vikingdb_ak"))
        viking_knowledgebase_service.set_sk(settings.get("vikingdb_sk"))

        results = []
        try:
            res = viking_knowledgebase_service.search_knowledge(collection_name=resource_id, resource_id=resource_id,
                                                            query=query, limit=top_k)
            result_list = res["result_list"]

            top_result = result_list[:top_k]
            # parse response
            for retrieval_result in top_result:
                # filter out results with score less than threshold
                if retrieval_result.get("score") < score_threshold:
                    continue
                result = {
                    "metadata": retrieval_result.get("doc_info"),
                    "score": retrieval_result.get("score"),
                    "title": retrieval_result.get("doc_info").get("doc_name"),
                    "content": retrieval_result.get("content"),
                }
                results.append(result)
        except Exception:
            pass

        # Construct and return the response
        return Response(
            response=json.dumps({"records": results}),
            status=200,
            content_type="application/json"
        )
