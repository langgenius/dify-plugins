import time
import hashlib
import logging
from typing import Mapping
from werkzeug import Request, Response
from dify_plugin import Endpoint

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)


class WechatGet(Endpoint):
    """微信公众号服务器验证端点"""
    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        处理微信公众号的token验证请求
        """
        # 获取微信发送的参数
        signature = r.args.get('signature', '')
        timestamp = r.args.get('timestamp', '')
        nonce = r.args.get('nonce', '')
        echostr = r.args.get('echostr', '')
        
        # 获取配置中的token
        token = settings.get('wechat_token', '')
        
        if not token:
            logger.error("微信Token未配置")
            return Response("微信Token未配置", status=500)
        
        # 检查是否是加密模式
        encoding_aes_key = settings.get('encoding_aes_key', '')
        is_encrypted_mode = bool(encoding_aes_key)
        
        # 检查是否有msg_signature参数
        msg_signature = r.args.get('msg_signature', '')
        
        # 处理加密模式下的验证
        if is_encrypted_mode and msg_signature:
            app_id = settings.get('app_id', '')
            
            if not app_id:
                logger.error("加密模式下缺少app_id配置")
                return Response("配置错误", status=500)
                
            # 加密模式下的验证逻辑
            try:
                from endpoints.wechat.crypto import WechatCrypto
                crypto = WechatCrypto(token, encoding_aes_key, app_id)
                
                # 解密echostr
                echostr = crypto.decrypt_message(f"<xml><Encrypt><![CDATA[{echostr}]]></Encrypt></xml>", 
                                                msg_signature, timestamp, nonce)
                
                # 返回解密后的echostr
                return Response(echostr, status=200)
            except Exception as e:
                logger.error(f"解密echostr失败: {str(e)}")
                return Response("验证失败", status=403)
        else:
            # 常规验证模式            
            # 按照微信的验证规则进行验证
            # 1. 将token、timestamp、nonce三个参数进行字典序排序
            temp_list = [token, timestamp, nonce]
            temp_list.sort()
            
            # 2. 将三个参数字符串拼接成一个字符串进行sha1加密
            temp_str = ''.join(temp_list)
            hash_object = hashlib.sha1(temp_str.encode('utf-8'))
            hash_str = hash_object.hexdigest()
            
            # 3. 将加密后的字符串与signature对比，如果相同则返回echostr
            if hash_str == signature:
                return Response(echostr, status=200)
            else:
                logger.warning(f"验证失败: 计算签名={hash_str}, 接收签名={signature}")
                return Response("验证失败", status=403)
