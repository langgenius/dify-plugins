from typing import Any, Mapping
from werkzeug import Request, Response
from dify_plugin import Endpoint
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import traceback
import hmac
import hashlib
import base64

class LineEndpoint(Endpoint):

    def _invoke(self, request: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the endpoint with the given request.
        """
        if not request:
            return Response(status=200, response="ok")
        
        signature = request.headers.get('X-Line-Signature')
        if not signature:
            return Response(status=200, response="ok")
        
        # 獲取請求體作為文本
        body = request.get_data(as_text=True)
        if not body:
            return Response(status=200, response="ok")
        # 獲取Dify plugin變數
        lineChannelSecret = settings.get('channel_secret')
        lineChannelAccessToken = settings.get('channel_access_token')
        if not (lineChannelSecret and lineChannelAccessToken):
            return Response(status=200, response="ok")

        # 使用 Channel Secret 生成 HMAC-SHA256 簽名
        hash = hmac.new(
            lineChannelSecret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).digest()
        computed_signature = base64.b64encode(hash).decode('utf-8')
        # 比對簽名
        if signature != computed_signature:
            raise InvalidSignatureError("signature error")
        # 初始化 LINE Bot API
        handler = WebhookHandler(lineChannelSecret)
        line_bot_api = LineBotApi(lineChannelAccessToken)

        # 註冊 TextMessage Event
        @handler.add(MessageEvent, message=TextMessage)
        def handle_message(event):    
            # Line 傳來的 Message
            user_id = event.source.user_id
            user_message = event.message.text
            try:
                conversation_id = self.session.storage.get(user_id)          
                invoke_params = {
                    "app_id" : settings["app"]["app_id"],
                    "query" : user_message,
                    "inputs" : {},
                    "response_mode" : "blocking"
                }
                if conversation_id is not None:
                    invoke_params['conversation_id'] = conversation_id.decode('utf-8')
                
                response = self.session.app.chat.invoke(**invoke_params)
                answer = response.get("answer")
                conversation_id = response.get("conversation_id")
                if conversation_id is not None:
                    self.session.storage.set(user_id, conversation_id.encode('utf-8'))
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=answer)
                )

                return Response(
                    status=200,
                    response="ok",
                    content_type="text/plain",
                )

            except Exception as e:
                err = traceback.format_exc()
                return Response(
                    status=500,
                    response=err,
                    content_type="text/plain",
                )
            
        # 處理 webhook
        try:
            handler.handle(body, signature)
            return Response(
                status=200,
                response="ok",
                content_type="text/plain",
            )
        except InvalidSignatureError:
            err = traceback.format_exc()
            return Response(
                status=400,
                response=err,
                content_type="text/plain",
            )
        except Exception as e:
            err = traceback.format_exc()
            return Response(
                status=500,
                response=err,
                content_type="text/plain",
            )
    