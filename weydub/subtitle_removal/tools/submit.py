from dify_plugin import Tool
from weydub_api import submit


class SubmitRemoval(Tool):
    def _invoke(self, tool_parameters):
        work_id = submit(self.runtime.credentials, tool_parameters["video_url"])
        yield self.create_variable_message("work_id", work_id)
        yield self.create_text_message(
            f"Submitted. Work ID: {work_id}. Use Check removal result on this ID."
        )
