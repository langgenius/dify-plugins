import time
from collections.abc import Generator
import requests
from dify_plugin import Tool
from tenacity import retry, stop_after_attempt, wait_exponential


class lark_text(Tool):
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

    def _split_message(self, message: str, chunk_size: int = 500) -> list[str]:
        """智能分段消息，保持段落完整性"""
        if len(message) <= chunk_size:
            return [message]
            
        chunks = []
        current_chunk = []
        current_length = 0
        
        # 按行分割，尽量保持完整段落
        for line in message.split('\n'):
            if current_length + len(line) + 1 <= chunk_size:
                current_chunk.append(line)
                current_length += len(line) + 1
            else:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = len(line)
                
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _send_text_message(self, webhook_key: str, message: str) -> Generator:
        """发送文本消息，支持长文本分段发送，带重试机制"""
        chunks = self._split_message(message)
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

            success, error_msg = self._send_request(webhook_key, payload)
            if not success:
                yield self.create_text_message(f"第{index}条消息发送失败: {error_msg}")
                return

            if index < total_chunks:
                time.sleep(1)  # 消息发送间隔，避免触发限制

        sent_msg = "消息已分{num}条发送完成📨" if total_chunks > 1 else "消息已送达📨"
        yield self.create_text_message(sent_msg.format(num=total_chunks))

    def _invoke(self, params: dict) -> Generator:
        """处理文本消息发送请求"""
        webhook_key = self.runtime.credentials['webhook_key']
        message = params['message']

        # 验证消息内容
        if not message or not message.strip():
            yield self.create_text_message("消息内容不能为空")
            return

        if len(message) > 5000:  # 飞书消息长度限制
            yield self.create_text_message("消息内容超过长度限制(5000字符)")
            return

        yield from self._send_text_message(webhook_key, message)
