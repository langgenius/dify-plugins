async function getUserInfo() {
  const res = await fetch(`/trtc/get-info`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
  if (!res.ok) throw new Error('get-info failed');
  return res.json();
}

async function initChatConfig() {
  const userInfo = await getUserInfo();
  return { userInfo };
}

async function startAIConversation(data) {
  const res = await fetch(`/trtc/start`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: data });
  if (!res.ok) throw new Error('start failed');
  return res.json();
}

async function stopAIConversation(data) {
  const res = await fetch(`/trtc/stop`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: data });
  if (!res.ok) throw new Error('stop failed');
  return res.json();
}

