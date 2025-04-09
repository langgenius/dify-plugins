from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

import json
import types
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.cls.v20201016 import cls_client, models

class ClsLogSearchProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            required_fields = ["SecretId", "SecretKey", "Region"]
            for field in required_fields:
                if field not in credentials or not credentials[field]:
                    raise ValueError(f"请填写密钥: {field}")
            
            # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey
            cred = credential.Credential(credentials["SecretId"], credentials["SecretKey"])
            # 实例化一个http选项
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cls.tencentcloudapi.com"
            # 实例化一个client选项
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象
            client = cls_client.ClsClient(cred, credentials["Region"], clientProfile)
            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.DescribeTopicsRequest()
            params = {}
            req.from_json_string(json.dumps(params))
            # 尝试获取项目信息以验证凭证是否有效
            resp = client.DescribeTopics(req)
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))