import time
from collections.abc import Generator
from typing import Optional
import requests
from dify_plugin import Tool
from tenacity import retry, stop_after_attempt, wait_exponential


class lark_card(Tool):
    # 卡片类型到颜色的映射
    COLOR_MAP = {
        "info": "blue",
        "warning": "orange",
        "success": "green",
        "error": "red"
    }

    # 布局配置
    LAYOUT_CONFIG = {
        "horizontal": {"enable_forward": True, "update_multi": False},
        "vertical": {"enable_forward": True, "update_multi": True},
        "bisected": {"enable_forward": True, "update_multi": True, "enable_sidebar": True}
    }

    def _send_request(self, webhook_key: str, payload: dict) -> tuple[bool, str]:
        """发送请求到飞书机器人"""
        try:
            response = requests.post(
                f"https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_key}",
                json=payload,
                timeout=10
            )
            result = response.json()
            if result.get('code') != 0:
                return False, result.get('msg', '未知错误')
            return True, ''
        except requests.RequestException as e:
            return False, f"请求失败: {str(e)}"

    def _validate_card_params(self, message: str, card_type: str, card_layout: str) -> tuple[bool, str]:
        """验证卡片消息参数"""
        if not message or not message.strip():
            return False, "消息内容不能为空"

        if len(message) > 5000:
            return False, "消息内容超过长度限制(5000字符)"

        if card_type not in self.COLOR_MAP:
            return False, f"不支持的卡片类型: {card_type}，可选类型: {', '.join(self.COLOR_MAP.keys())}"

        if card_layout not in self.LAYOUT_CONFIG:
            return False, f"不支持的布局类型: {card_layout}，可选布局: {', '.join(self.LAYOUT_CONFIG.keys())}"

        return True, ""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _send_card_message(self, webhook_key: str, message: str, title: Optional[str] = None, 
                          card_type: str = "info", card_layout: str = "horizontal",
                          show_meta: bool = True) -> Generator:
        """发送卡片消息，带重试机制"""
        # 验证参数
        is_valid, error_msg = self._validate_card_params(message, card_type, card_layout)
        if not is_valid:
            yield self.create_text_message(error_msg)
            return

        # 处理消息内容
        message_elements = [{
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": message
            }
        }]
        
        # 添加元信息
        if show_meta:
            message_elements.extend([
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [{
                        "tag": "plain_text",
                        "content": "发送时间：" + time.strftime("%Y-%m-%d %H:%M:%S")
                    }]
                }
            ])
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True,
                    **self.LAYOUT_CONFIG[card_layout]
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title or "消息通知"
                    },
                    "template": self.COLOR_MAP[card_type]
                },
                "elements": message_elements
            }
        }

        success, error_msg = self._send_request(webhook_key, payload)
        if not success:
            yield self.create_text_message(f"卡片消息发送失败: {error_msg}")
            return
        
        yield self.create_text_message("卡片消息已送达📨")

    def _invoke(self, params: dict) -> Generator:
        """处理卡片消息发送请求"""
        webhook_key = self.runtime.credentials['webhook_key']
        message = params['message']
        title = params.get('title')
        card_type = params.get('card_type', 'info')
        card_layout = params.get('card_layout', 'horizontal')
        show_meta = params.get('show_meta', True)

        yield from self._send_card_message(
            webhook_key, message, title, 
            card_type, card_layout, show_meta
        )
