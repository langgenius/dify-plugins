import json
import random
import time
from collections.abc import Mapping

from dify_plugin import Endpoint
from werkzeug import Request, Response

from tencentcloud.trtc.v20190722 import trtc_client, models
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
try:
    from tls_sig_api_v2.tls_sig_api import TLSSigAPI as _SigClass
except ImportError:
    try:
        import TLSSigAPIv2 as _TLSSigAPIv2
        _SigClass = _TLSSigAPIv2.TLSSigAPIv2
    except ImportError:
        _SigClass = None


class TrtcAIEndpoint(Endpoint):
    def _client(self, settings: Mapping):
        secret_id = settings.get("tcloud_secret_id")
        secret_key = settings.get("tcloud_secret_key")
        region = settings.get("tcloud_region") or "ap-singapore"
        endpoint = "trtc.tencentcloudapi.com"

        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = endpoint
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        return trtc_client.TrtcClient(cred, region, client_profile)

    def _gen_sigs(self, settings: Mapping, user_id: str, robot_id: str):
        sdk_app_id_raw = settings.get("trtc_sdk_app_id")
        if not sdk_app_id_raw:
            raise ValueError("TRTC_SDK_APP_ID is required")
        try:
            sdk_app_id = int(str(sdk_app_id_raw).strip())
        except Exception:
            raise ValueError("TRTC_SDK_APP_ID must be an integer")

        secret_key = (settings.get("trtc_secret_key") or "").strip()
        if not secret_key:
            raise ValueError("TRTC_SECRET_KEY is required")

        expire = 36000
        if _SigClass is None:
            raise ValueError("tls-sig-api-v2 not installed or import name mismatch")
        api = _SigClass(sdk_app_id, secret_key)
        user_sig = api.gen_sig(user_id, expire)
        robot_sig = api.gen_sig(robot_id, expire)
        return user_sig, robot_sig

    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        action = values.get("action")
        if action == "get-info":
            return self._get_info(r, settings)
        if action == "start":
            return self._start_conversation(r, settings)
        if action == "stop":
            return self._stop_conversation(r, settings)
        if action == "server-callback":
            return self._server_callback(r)
        if action == "dify-completion":
            return self._dify_completion(r, settings)
        return Response("no action found", status=404, content_type="text/plain")

    def _get_info(self, r: Request, settings: Mapping) -> Response:
        try:
            sdk_app_id_raw = settings.get("trtc_sdk_app_id")
            if not sdk_app_id_raw:
                return Response(json.dumps({"error": "TRTC_SDK_APP_ID is required"}), status=400, content_type="application/json")
            try:
                sdk_app_id = int(str(sdk_app_id_raw).strip())
            except Exception:
                return Response(json.dumps({"error": "TRTC_SDK_APP_ID must be an integer"}), status=400, content_type="application/json")

            rnd = str(random.randint(100000, 999999))
            user_id = f"user_{rnd}"
            robot_id = f"ai_{rnd}"
            room_id = int(rnd)
            try:
                user_sig, robot_sig = self._gen_sigs(settings, user_id, robot_id)
            except ValueError as ve:
                return Response(json.dumps({"error": str(ve)}), status=400, content_type="application/json")

            body = {
                "sdkAppId": sdk_app_id,
                "userSig": user_sig,
                "robotSig": robot_sig,
                "userId": user_id,
                "robotId": robot_id,
                "roomId": room_id,
            }
            return Response(json.dumps(body), status=200, content_type="application/json")
        except Exception as e:
            return Response(json.dumps({"error": "internal_error", "detail": str(e)}), status=500, content_type="application/json")

    def _start_conversation(self, r: Request, settings: Mapping) -> Response:
        try:
            data = r.get_json() or {}
            user_info = data.get("userInfo") or {}
            ai_config = data.get("aiConfig") or {}

            sdk_app_id = int(user_info["sdkAppId"])  # from get-info
            room_id = str(user_info["roomId"])       # string per API
            robot_id = user_info["robotId"]
            robot_sig = user_info["robotSig"]
            target_user_id = user_info["userId"]

            # LLM via Dify proxy inside plugin
            base_url = r.host_url.rstrip("/")
            endpoint_api_key = settings.get("dify_endpoint_api_key") or ""
            LLMConfig = {
                "LLMType": "openai",
                "Model": "dify-app",
                "APIUrl": f"{base_url}/trtc/dify-completion",
                "APIKey": endpoint_api_key,
                "History": 5,
                "Timeout": 8,
                "Streaming": True,
                "SystemPrompt": "",
            }

            # TTS / STT from settings; allow frontend override if provided
            tts_cfg_text = settings.get("tts_config") or "{}"
            stt_cfg_text = settings.get("stt_config") or "{}"
            try:
                tts_cfg = json.loads(tts_cfg_text)
            except Exception:
                tts_cfg = {}
            try:
                stt_cfg_raw = json.loads(stt_cfg_text)
            except Exception:
                stt_cfg_raw = {}

            # STTConfig requires Language/VadSilenceTime/CustomParam
            frontend_stt = ai_config.get("stt") or {}
            # Preference order: plugin setting stt_language > frontend provided > default 'en'
            stt_language = (settings.get("stt_language") or frontend_stt.get("language") or "en").strip()

            # If settings did not provide STTType, try to fallback to frontend-provided type/apiKey/model
            if not stt_cfg_raw.get("STTType") and frontend_stt.get("type"):
                # Map frontend keys to expected backend keys
                mapped = {
                    "STTType": frontend_stt.get("type"),
                }
                if frontend_stt.get("apiKey"):
                    mapped["ApiKey"] = frontend_stt.get("apiKey")
                if frontend_stt.get("model"):
                    mapped["Model"] = frontend_stt.get("model")
                # Merge into stt_cfg_raw
                stt_cfg_raw.update({k: v for k, v in mapped.items() if v})

            stt = {
                "Language": stt_language,
                "VadSilenceTime": 800,
                "CustomParam": json.dumps(stt_cfg_raw),
            }

            req = models.StartAIConversationRequest()
            payload = {
                "SdkAppId": sdk_app_id,
                "RoomId": room_id,
                "AgentConfig": {
                    "UserId": robot_id,
                    "UserSig": robot_sig,
                    "TargetUserId": target_user_id,
                    "WelcomeMessage": "Hello, I'm your AI assistant",
                    "InterruptMode": 2,
                    "TurnDetectionMode": 3,
                    "InterruptSpeechDuration": 200,
                    "WelcomeMessagePriority": 1,
                },
                "STTConfig": stt,
                "LLMConfig": json.dumps(LLMConfig),
                "TTSConfig": json.dumps(tts_cfg),
            }
            req.from_json_string(json.dumps(payload))

            client = self._client(settings)
            resp = client.StartAIConversation(req)
            return Response(resp.to_json_string(), status=200, content_type="application/json")
        except Exception as e:
            # Provide detailed error information for easier debugging
            err_code = getattr(e, "code", None)
            err_msg = getattr(e, "message", None) or str(e)
            req_id = getattr(e, "requestId", None) or getattr(e, "request_id", None)
            err_obj = {"error": err_msg}
            if err_code is not None:
                err_obj["code"] = err_code
            if req_id is not None:
                err_obj["requestId"] = req_id
            return Response(json.dumps(err_obj), status=500, content_type="application/json")

    def _stop_conversation(self, r: Request, settings: Mapping) -> Response:
        try:
            data = r.get_json() or {}
            req = models.StopAIConversationRequest()
            req.from_json_string(json.dumps(data))
            client = self._client(settings)
            resp = client.StopAIConversation(req)
            return Response(resp.to_json_string(), status=200, content_type="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), status=500, content_type="application/json")

    def _server_callback(self, r: Request) -> Response:
        try:
            _ = r.get_json() or {}
            return Response(json.dumps({"code": 0}), status=200, content_type="application/json")
        except Exception as e:
            return Response(json.dumps({"code": -1, "error": str(e)}), status=500, content_type="application/json")

    def _dify_completion(self, r: Request, settings: Mapping) -> Response:
        try:
            ep_key = settings.get("dify_endpoint_api_key") or ""
            auth = r.headers.get("Authorization")
            if ep_key and auth != f"Bearer {ep_key}":
                return Response(json.dumps({"error": "Unauthorized"}), status=401, content_type="application/json")

            data = r.get_json() or {}
            messages = data.get("messages") or []
            if not messages:
                return Response(json.dumps({"error": "messages required"}), status=400, content_type="application/json")
            user_msgs = [m for m in messages if m.get("role") == "user"]
            if not user_msgs:
                return Response(json.dumps({"error": "no user message"}), status=400, content_type="application/json")
            query = user_msgs[-1].get("content") or ""

            app = settings.get("dify_app") or {}
            app_id = app.get("app_id") if isinstance(app, dict) else None
            if not app_id:
                error_msg = "dify_app.app_id is required but not found in settings"
                print(f"[ERROR] {error_msg}, settings.dify_app={app}")
                return Response(json.dumps({"error": error_msg}), status=400, content_type="application/json")

            conv_id = data.get("conversation_id")

            def sse():
                try:
                    created = int(time.time())
                    print(f"[DEBUG] Streaming from Dify: app_id={app_id}, conv_id={conv_id}, q_len={len(query)}")
                    stream = self.session.app.chat.invoke(
                        app_id=app_id,
                        query=query,
                        inputs={},
                        conversation_id=conv_id,
                        response_mode="streaming",
                    )

                    for chunk in stream:
                        piece = ""
                        if isinstance(chunk, dict):
                            piece = chunk.get("answer") or chunk.get("text") or chunk.get("content") or ""
                        elif isinstance(chunk, str):
                            piece = chunk
                        if not piece:
                            continue

                        payload = {
                            "id": "chatcmpl-dify",
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": data.get("model") or "dify-app",
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"role": "assistant", "content": piece},
                                    "finish_reason": None,
                                }
                            ],
                        }
                        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

                    done = {
                        "id": "chatcmpl-dify",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": data.get("model") or "dify-app",
                        "choices": [
                            {
                                "index": 0,
                                "delta": {},
                                "finish_reason": "stop",
                            }
                        ],
                    }
                    yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    err = {"error": str(e)}
                    print(f"[ERROR] Streaming error: {e}")
                    yield f"data: {json.dumps(err)}\n\n"
                    yield "data: [DONE]\n\n"

            return Response(sse(), status=200, content_type="text/event-stream")
        except Exception as e:
            error_detail = str(e)
            print(f"[ERROR] Exception in _dify_completion: {error_detail}")
            import traceback
            traceback.print_exc()
            return Response(json.dumps({"error": error_detail}), status=500, content_type="application/json")


