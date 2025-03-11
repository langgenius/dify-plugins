from collections.abc import Generator
from typing import Any

import base64

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File


class ImgFileContent(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        file = tool_parameters["file"]
        base64_flag = tool_parameters["base64"]

        print(file)
        
        if not file or file.url.startswith("http"):
            yield self.create_text_message("")
            return
        
        assert isinstance(file, File)
        file.url = "http://localhost" + file.url
        print("==========>",file.url, base64_flag)

        content = base64.b64encode(file.blob).decode('utf-8', errors='ignore')
        if base64_flag == "0":
            content =  file.blob.decode('utf-8', errors='ignore')

        yield self.create_text_message(content)
        return
