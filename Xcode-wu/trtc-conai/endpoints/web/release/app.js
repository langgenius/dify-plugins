let taskId = null;
let muteState = false;
let aiConfig = { tts: {}, stt: {} };

function loadConfigFromForm() {
  try {
    const ttsEl = document.getElementById('tts-config');
    const sttEl = document.getElementById('stt-config');
    const ttsText = ttsEl ? (ttsEl.value || '').trim() : '';
    const sttText = sttEl ? (sttEl.value || '').trim() : '';
    if (ttsText) aiConfig.tts = JSON.parse(ttsText);
    if (sttText) aiConfig.stt = JSON.parse(sttText);
  } catch (e) {
    addSystemMessage('Config parse error: ' + e.message);
    return false;
  }
  return true;
}
function saveConfig() { if (loadConfigFromForm()) localStorage.setItem('aiConfig', JSON.stringify(aiConfig)); }
function loadConfig() {
  const saved = localStorage.getItem('aiConfig');
  if (saved) { aiConfig = JSON.parse(saved); updateConfigForm(); }
}
function updateConfigForm() {
  const ttsEl = document.getElementById('tts-config');
  const sttEl = document.getElementById('stt-config');
  if (ttsEl && aiConfig.tts) ttsEl.value = JSON.stringify(aiConfig.tts, null, 2);
  if (sttEl && aiConfig.stt) sttEl.value = JSON.stringify(aiConfig.stt, null, 2);
}
function loadSampleConfig() {
  aiConfig = { tts: { type: 'cartesia', apiKey: 'ssk_car_xxx', apiUrl: 'https://api.cartesia.ai', model: 'sonic-3', voiceId: 'e07c00bc-...' }, stt: { type: 'deepgram', apiKey: 'sk_xxx', model: 'nova-2', language: 'en' } };
  updateConfigForm();
}

async function startConversation() { if (!loadConfigFromForm()) return; startButton.disabled = true; updateStatus('room', 'Connecting...'); try { const { userInfo } = await initChatConfig(); const { sdkAppId, userSig, userId, roomId, robotId } = userInfo; setUserIds(userId, robotId); await enterTRTCRoom({ roomId, sdkAppId, userId, userSig }); updateStatus('room', '✅ Connected'); const resp = await startAIConversation(JSON.stringify({ userInfo, aiConfig })); taskId = resp.TaskId; endButton.disabled = false; sendButton.disabled = false; interruptButton.disabled = false; muteButton.disabled = false; } catch (e) { addSystemMessage('Start failed: ' + e.message); startButton.disabled = false; updateStatus('room', 'Connection Failed'); } }
async function stopConversation() { endButton.disabled = true; sendButton.disabled = true; interruptButton.disabled = true; muteButton.disabled = true; muteButton.textContent = 'Mute'; muteButton.classList.remove('muted'); muteState = false; updateStatus('room', 'Disconnecting...'); try { if (taskId) await stopAIConversation(JSON.stringify({ TaskId: taskId })); } catch (_) {} try { await exitTRTCRoom(); } catch (_) {} /* hide metrics on end per request */ /* displayLatencyStatistics(); */ destroyTRTCClient(); taskId = null; resetMetrics(); resetUI(); }
function handleSendMessage() { if (sendCustomTextMessage(textInput.value)) { textInput.value = ''; } }
async function handleToggleMute() { muteState = !muteState; const ok = await toggleMute(muteState); if (ok) { muteButton.textContent = muteState ? 'Unmute' : 'Mute'; muteState ? muteButton.classList.add('muted') : muteButton.classList.remove('muted'); } }
function initializeApp() { loadConfig(); startButton.addEventListener('click', startConversation); endButton.addEventListener('click', stopConversation); sendButton.addEventListener('click', handleSendMessage); interruptButton.addEventListener('click', sendInterruptSignal); muteButton.addEventListener('click', handleToggleMute); const sc = document.getElementById('save-config'); if (sc) sc.addEventListener('click', saveConfig); const ls = document.getElementById('load-sample'); if (ls) ls.addEventListener('click', loadSampleConfig); textInput.addEventListener('keypress', (e) => { if (e.key === 'Enter' && !sendButton.disabled) handleSendMessage(); }); }
document.addEventListener('DOMContentLoaded', initializeApp);

