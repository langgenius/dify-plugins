from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.model import (
    InvokeServerUnavailableError,
)
import json
import types
import time
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.cls.v20201016 import cls_client, models


class ClsLogSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            
            # 获取当前时间戳（毫秒）
            current_time = int(time.time() * 1000)
            # 计算30分钟前的时间戳（毫秒）
            thirty_minutes_ago = current_time - 30 * 60 * 1000
            # 获取查询参数
            Query = tool_parameters.get('Query', '')
            Region = tool_parameters.get('Region', '')
            TopicId = tool_parameters.get('TopicId', '')
            From = tool_parameters.get('From', '')
            To = tool_parameters.get('To', '')
            Limit = tool_parameters.get('Limit', '')
            if not Query:
                Query = '*'
            if not Region:
                Region = self.runtime.credentials['Region']
            if not TopicId:
                TopicId = self.runtime.credentials['TopicId']
            if not From:
                From = thirty_minutes_ago
            if not To:
                To = current_time
            if not Limit:
                Limit = 20

            # 获取凭证
            SecretId = self.runtime.credentials['SecretId']
            SecretKey = self.runtime.credentials['SecretKey']

            # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey
            cred = credential.Credential(SecretId, SecretKey)
            # 实例化一个http选项
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cls.tencentcloudapi.com"
            # 实例化一个client选项
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象
            client = cls_client.ClsClient(cred, Region, clientProfile)

            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.SearchLogRequest()
            params = {
                "From": From,
                "To": To,
                "Query": Query,
                "SyntaxRule": 1,
                "TopicId": TopicId,
                "Limit": Limit
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个SearchLogResponse的实例，与请求对象对应
            resp = client.SearchLog(req)
            yield self.create_json_message(json.loads(resp.to_json_string()))
        except Exception as e:
            raise InvokeServerUnavailableError(str(e))

