let trtcClient = null;
let currentUserId = null;
let botUserId = null;

function initTRTCClient() { if (!trtcClient) trtcClient = TRTC.create(); return trtcClient; }
async function enterTRTCRoom(params) {
  const client = initTRTCClient();
  await client.enterRoom({ roomId: parseInt(params.roomId), scene: 'rtc', sdkAppId: params.sdkAppId, userId: params.userId, userSig: params.userSig });
  client.on(TRTC.EVENT.CUSTOM_MESSAGE, handleTRTCMessage);
  client.on(TRTC.EVENT.AUDIO_VOLUME, handleAudioVolume);
  client.enableAudioVolumeEvaluation(50);
  await client.startLocalAudio();
}
async function exitTRTCRoom() { if (trtcClient) await trtcClient.exitRoom(); }
function destroyTRTCClient() { if (trtcClient) { trtcClient.destroy(); trtcClient = null; } }
function setUserIds(userId, aiUserId) { currentUserId = userId; botUserId = aiUserId; }
async function toggleMute(mute) { if (!trtcClient) return false; try { await trtcClient.updateLocalAudio({ mute }); return true; } catch { return false; } }

function sendCustomTextMessage(message) { if (!trtcClient || !message.trim()) return; const payload = { type: MESSAGE_TYPES.CUSTOM_TEXT, sender: currentUserId, receiver: [botUserId], payload: { id: Date.now().toString(), message: message.trim(), timestamp: Date.now() } }; trtcClient.sendCustomMessage({ cmdId: 2, data: new TextEncoder().encode(JSON.stringify(payload)).buffer }); return true; }
function sendInterruptSignal() { if (!trtcClient) return false; const payload = { type: MESSAGE_TYPES.CUSTOM_INTERRUPT, sender: currentUserId, receiver: [botUserId], payload: { id: Date.now().toString(), timestamp: Date.now() } }; trtcClient.sendCustomMessage({ cmdId: 2, data: new TextEncoder().encode(JSON.stringify(payload)).buffer }); return true; }

function handleTRTCMessage(event) { try { const data = JSON.parse(new TextDecoder().decode(event.data)); switch (data.type) { case MESSAGE_TYPES.CONVERSATION: handleConversationMessage(data); break; case MESSAGE_TYPES.STATE_CHANGE: handleStateChangeMessage(data); break; case MESSAGE_TYPES.ERROR_CALLBACK: handleErrorCallbackMessage(data); break; case MESSAGE_TYPES.METRICS_CALLBACK: handleMetricsMessage(data); break; default: } } catch {} }
function handleConversationMessage(data) { const sender = data.sender; const text = data.payload.text; const roundId = data.payload.roundid; const isRobot = sender.includes('ai_'); const end = data.payload.end; addMessage(sender, text, isRobot ? 'ai' : 'user', roundId, end); }
function handleStateChangeMessage(data) { const state = data.payload.state; const stateText = STATE_LABELS[state] || 'Unknown State'; updateStatus('ai', stateText); }
function handleErrorCallbackMessage(data) { try { const { payload } = data; const { metric, tag } = payload; const { roundid, code, message } = tag; addSystemMessage(`${metric} (${code}): ${message}`); } catch {} }
function handleMetricsMessage(data) { try { const { payload } = data; const { metric, value, tag } = payload; recordMetric(metric, value, tag.roundid); } catch {} }

let prevUserVolume = 0; let prevAiVolume = 0; const smoothingFactor = 0.3;
function handleAudioVolume(event) { event.result.forEach(({ userId, volume }) => { const isLocal = userId === ''; if (isLocal) { const sm = (volume * (1 - smoothingFactor)) + (prevUserVolume * smoothingFactor); prevUserVolume = sm; updateVolumeBar('userVolumeBar', sm); } else if (userId === botUserId) { const sm = (volume * (1 - smoothingFactor)) + (prevAiVolume * smoothingFactor); prevAiVolume = sm; updateVolumeBar('aiVolumeBar', sm); } }); }
function updateVolumeBar(elementId, volume) { const el = document.getElementById(elementId); if (el) { let scaled; if (volume < 5) scaled = 8; else if (volume < 20) scaled = 8 + (volume * 1.5); else scaled = Math.min(volume * 2.5, 100); el.style.transition = 'width 0.12s cubic-bezier(0.4, 0, 0.2, 1)'; el.style.width = `${scaled}%`; if (volume > 5) el.classList.add('active'); else el.classList.remove('active'); } }

