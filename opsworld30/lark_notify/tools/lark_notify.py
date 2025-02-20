import time
from collections.abc import Generator
from typing import  Optional
import requests
from dify_plugin import Tool

class LarkNotifyTool(Tool):
    def _send_request(self, webhook_key: str, payload: dict) -> dict:
        response = requests.post(
            f"https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_key}",
            json=payload,
            timeout=10
        )
        result = response.json() if response.status_code == 200 else None
        if result and result.get('code') != 0:
            return None
        return result

    def _send_text_message(self, webhook_key: str, message: str) -> Generator:
        chunk_size = 500
        chunks = [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]
        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks, 1):
            sequence_text = f"[{index}/{total_chunks}] " if total_chunks > 1 else ""
            chunk_text = sequence_text + chunk

            payload = {
                "msg_type": "text",
                "content": {
                    "text": chunk_text
                }
            }

            if not self._send_request(webhook_key, payload):
                yield self.create_text_message(f"第{index}条消息发送失败")
                return

            if index < total_chunks:
                time.sleep(1)

        sent_msg = "消息已分{num}条发送完成📨" if total_chunks > 1 else "消息已送达📨"
        yield self.create_text_message(sent_msg.format(num=total_chunks))

    def _send_card_message(self, webhook_key: str, message: str, title: Optional[str] = None, 
                         card_type: str = "info", card_layout: str = "horizontal",
                         show_meta: bool = True) -> Generator:
        """发送卡片消息"""
        color_map = {
            "info": "blue",
            "warning": "orange",
            "success": "green",
            "error": "red"
        }

        layout_config = {
            "horizontal": {"enable_forward": True, "update_multi": False},
            "vertical": {"enable_forward": True, "update_multi": True},
            "bisected": {"enable_forward": True, "update_multi": True, "enable_sidebar": True}
        }
        
        message_elements = []
        
        message_elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": message
            }
        })
        
        if show_meta:
            message_elements.append({
                "tag": "hr"
            })
            message_elements.append({
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "发送时间：" + time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                ]
            })
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True,
                    **layout_config.get(card_layout, layout_config["horizontal"])
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title or "消息通知"
                    },
                    "template": color_map.get(card_type, "blue")
                },
                "elements": message_elements
            }
        }

        if not self._send_request(webhook_key, payload):
            yield self.create_text_message("卡片消息发送失败")
            return
        
        yield self.create_text_message("卡片消息已送达📨")

    def _invoke(self, params: dict) -> Generator:
        webhook_key = self.runtime.credentials['webhook_key']
        message = params['message']
        msg_type = params.get('msg_type', 'text')
        title = params.get('title')
        card_type = params.get('card_type', 'info')
        card_layout = params.get('card_layout', 'horizontal')
        show_meta = params.get('show_meta', True)

        if msg_type == 'text':
            yield from self._send_text_message(webhook_key, message)
        elif msg_type == 'card':
            yield from self._send_card_message(webhook_key, message, title, card_type, card_layout,
                                            show_meta)
        else:
            yield self.create_text_message(f"不支持的消息类型: {msg_type}")