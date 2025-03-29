import json
from alibabacloud_ocr_api20210707.client import Client as ocr_client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_model
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as util_client
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DuGuangTool(Tool):
    """
    AliYun OCR tool
    """

    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        image_url = tool_parameters.get("image_url", "").strip()
        if not image_url:
            yield self.create_text_message("Invalid image_url")
        ocr_result = self._ocr_image_url(image_url)
        yield self.create_text_message(ocr_result)

    def _ocr_image_url(
            self,
            image_url: str
    ) -> str:
        access_key_id = self.runtime.credentials.get("access_key_id")
        access_key_secret = self.runtime.credentials.get("access_key_secret")
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
        )
        config.endpoint = f'ocr-api.cn-hangzhou.aliyuncs.com'
        client = ocr_client(config)
        recognize_request = ocr_model.RecognizeAdvancedRequest(
            url=image_url,
            need_rotate=False
        )
        try:
            # recognize_basic_with_options
            result = client.recognize_advanced_with_options(recognize_request, util_models.RuntimeOptions())
            data_str = util_client.to_jsonstring(result.body.data)
            data_json = json.loads(data_str)
            return data_json.get("content")
        except Exception as e:
            raise Exception(f'AliYun DuGuangTool error {str(e)}')
