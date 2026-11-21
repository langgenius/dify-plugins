from dify_plugin import Tool
from weydub_api import status


class RemovalResult(Tool):
    def _invoke(self, tool_parameters):
        result = status(self.runtime.credentials, tool_parameters["work_id"])
        yield self.create_variable_message("state", result["state"])
        if result["state"] == "ready":
            yield self.create_variable_message("video_url", result["video_url"])
            message = f"Your MP4 is ready: {result['video_url']}"
        elif result["state"] == "processing":
            message = "Still processing. Check the same work ID in five minutes."
        else:
            message = f"Processing failed (status {result['code']}). Check the job in Weydub."
        yield self.create_text_message(message)
