from collections.abc import Mapping
from werkzeug import Request
import hmac
import hashlib
import time


class BaseAuth:
    def verify(self, r: Request, settings: Mapping) -> bool:
        # 从请求的 query 中获取, secret 和 time_stamp
        secret = r.args.get("secret")
        time_stamp = r.args.get("time_stamp")
        # 如果 secret 和 time_stamp 为空, 则返回 False
        if not secret or not time_stamp:
            return False

        data = r.get_json()
        app_id = data.get("app_id")
        base_url = settings.get("base_url")
        app_key = settings.get("api_key")

        # 拼接 url
        url = f"{base_url}/e/{app_id}{r.path}"

        # 计算正确的secret
        hex_timestamp = int(f"0x{time_stamp}", 16)
        payload = f"{url}{hex_timestamp}"
        calculated_secret = hmac.new(
            app_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # print('url', url)
        # print('app_key', app_key)
        # print('time_stamp', time_stamp)
        # print('hex_timestamp', hex_timestamp)
        # print('payload', payload)
        # print('received_secret', secret)
        # print('calculated_secret', calculated_secret)

        # 检查 secret 是否匹配
        return secret == calculated_secret
