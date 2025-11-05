const chatListElement = document.querySelector('.chat-list');
const startButton = document.getElementById('start-button');
const endButton = document.getElementById('end-button');
const textInput = document.getElementById('text-input');
const sendButton = document.getElementById('send-button');
const interruptButton = document.getElementById('interrupt-button');
const muteButton = document.getElementById('mute-button');

let messages = [];
function renderChatMessages() {
  const frag = document.createDocumentFragment();
  messages.forEach(m => {
    const el = document.createElement('div'); el.classList.add('chat-item', m.type);
    const s = document.createElement('div'); s.classList.add('chat-id'); s.textContent = m.sender;
    const c = document.createElement('div'); c.classList.add('chat-text'); c.textContent = m.content;
    el.appendChild(s); el.appendChild(c); frag.appendChild(el);
  });
  chatListElement.innerHTML = ''; chatListElement.appendChild(frag);
  // UI polish: keep recent messages visible (no logic change)
  chatListElement.scrollTop = chatListElement.scrollHeight;
}
function updateStatus(type, text) { const el = type === 'ai' ? document.getElementById('ai-state') : document.getElementById('room-status'); if (el) el.textContent = text; }
function addMessage(sender, content, type, id, end = true) {
  const exist = messages.find(x => x.id === id && x.sender === sender);
  if (exist) { exist.content = content; exist.end = end; } else { messages.unshift({ id, content, sender, type, end }); }
  renderChatMessages();
}
function addSystemMessage(content, isHTML = false) {
  const list = document.querySelector('.chat-list'); const item = document.createElement('div'); item.className = 'chat-item ai';
  const id = document.createElement('div'); id.className = 'chat-id'; id.textContent = 'System';
  const text = document.createElement('div'); text.className = 'chat-text'; if (isHTML) text.innerHTML = content; else text.textContent = content;
  item.appendChild(id); item.appendChild(text); list.insertBefore(item, list.firstChild);
}
function resetUI() { startButton.disabled = false; endButton.disabled = true; sendButton.disabled = true; interruptButton.disabled = true; updateStatus('room', 'Disconnected'); updateStatus('ai', 'AI NotReady'); }

// Visual state helpers (do not change business logic)
function setLoading(button, loading) {
  if (!button) return;
  if (loading) { button.setAttribute('aria-busy', 'true'); button.classList.add('is-loading'); }
  else { button.removeAttribute('aria-busy'); button.classList.remove('is-loading'); }
}

