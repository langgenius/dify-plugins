import logging
from typing import Dict, Any

from .base import MessageHandler
from ..models import WechatMessage

logger = logging.getLogger(__name__)

class UnsupportedMessageHandler(MessageHandler):
    """不支持的消息类型处理器"""
    def handle(self, message: WechatMessage, session: Any, app_settings: Dict[str, Any]) -> str:
        """处理不支持的消息类型"""
        logger.warning(f"暂不支持的消息类型: {message.msg_type}")
        return "目前只支持文本消息" 