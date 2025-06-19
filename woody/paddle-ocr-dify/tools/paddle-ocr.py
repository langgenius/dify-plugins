# Copyright 2025 woody
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This file is based on PaddleOCR (https://github.com/PaddlePaddle/PaddleOCR)
# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from paddleocr import PaddleOCR



class PaddleOcrTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 定义参数默认值映射
        default_params = {
            "doc_orientation_classify_model_name": "PP-LCNet_x1_0_doc_ori",
            "doc_unwarping_model_name": "UVDoc", 
            "textline_orientation_model_name": "PP-LCNet_x1_0_textline_ori",
            "text_detection_model_name": "PP-OCRv5_mobile_det",
            "text_recognition_model_name": "PP-OCRv5_mobile_rec",
            "use_doc_orientation_classify": False,
            "use_doc_unwarping": False,
            "use_textline_orientation": False,
            "lang": "ch"
        }
        
        # 获取参数，处理空字符串情况
        def get_param(key: str) -> Any:
            value = tool_parameters.get(key, default_params[key])
            # 如果值为空字符串，使用默认值
            return default_params[key] if value == "" else value
        
        # 提取所有参数
        params = {key: get_param(key) for key in default_params.keys()}
        
        ocr_engine = PaddleOCR(
            doc_orientation_classify_model_name=params["doc_orientation_classify_model_name"],
            doc_unwarping_model_name=params["doc_unwarping_model_name"],
            textline_orientation_model_name=params["textline_orientation_model_name"],
            text_detection_model_name=params["text_detection_model_name"],
            text_recognition_model_name=params["text_recognition_model_name"],
            use_doc_orientation_classify=params["use_doc_orientation_classify"],
            use_doc_unwarping=params["use_doc_unwarping"],
            use_textline_orientation=params["use_textline_orientation"],
            lang=params["lang"],
            enable_mkldnn=False
        )
        img=tool_parameters.get("img",None)
        ocr_res=[]
        img_url=img.url
        import tempfile
        import os
        import requests
        ocr_res={}
        # 下载图片到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=img.extension) as temp_file:
            response = requests.get(img_url)
            response.raise_for_status()
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        try:
            # 使用临时文件路径进行OCR识别
            res = ocr_engine.predict(temp_file_path)
            boxes=[]
            for box in res[0]['rec_boxes']:
                boxes.append(box.tolist())
            ocr_res['rec_texts']=res[0]['rec_texts']
            ocr_res['rec_boxes']=boxes
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
        yield self.create_json_message(ocr_res)
        
        
        
