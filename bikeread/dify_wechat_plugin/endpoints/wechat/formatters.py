import time
from .models import WechatMessage

class ResponseFormatter:
    """响应格式化器"""
    @staticmethod
    def format_xml(message: WechatMessage, content: str) -> str:
        """
        格式化XML响应
        
        参数:
            message: 微信消息对象
            content: 回复内容
            
        返回:
            符合微信公众平台规范的XML响应字符串
        """
        current_timestamp = int(time.time())
        return f"""<xml>
<ToUserName><![CDATA[{message.from_user}]]></ToUserName>
<FromUserName><![CDATA[{message.to_user}]]></FromUserName>
<CreateTime>{current_timestamp}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""

    @staticmethod
    def format_error_xml(from_user: str, to_user: str, content: str) -> str:
        """
        格式化错误响应的XML
        
        参数:
            from_user: 发送者OpenID
            to_user: 接收者ID
            content: 错误信息
            
        返回:
            错误响应的XML字符串
        """
        current_timestamp = int(time.time())
        return f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{current_timestamp}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>""" 