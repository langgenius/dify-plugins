from collections.abc import Generator
from typing import Any

import base64
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ImgUrlContent(Tool):
    def url_image_content(self, image_url,base64_flag):
        try:
            # 发送 HTTP 请求获取图片数据
            response = requests.get(image_url)
            # 检查响应状态码
            response.raise_for_status()
            if response.status_code == 200:
                # 获取图片的字节数据
                image_bytes = response.content
                if base64_flag == "0": 
                    return image_bytes.decode('utf-8')
                else:
                    # 将字节数据编码为 Base64 字符串
                    base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
                    return base64_encoded

        except requests.RequestException as e:
            print(f"请求图片时发生错误: {e}")
        except Exception as e:
            print(f"发生错误: {e}")


    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        url = tool_parameters["url"]
        base64_flag = tool_parameters["base64"]
        if not url or not url.startswith("http"):
            yield self.create_text_message("")
            return
        
        result = self.url_image_content(url,base64_flag)
        yield self.create_text_message(result)
        return
