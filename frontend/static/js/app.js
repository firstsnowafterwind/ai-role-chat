/*
App chat UI script
- Message bubbles style/size/color: see CSS selectors `.msg`, `.msg.user`, `.msg.bot`.
- Sidebar chat name font: `.chat-name` (currently 1.3em, centered).
- Avatars: message area `.avatar`, sidebar `.chat-avatar`.
*/

const $ = (sel) => document.querySelector(sel);

const output = $("#output");
const input = $("#message");
const sendBtn = $("#send");
const micBtn = $("#mic");
const ttsBtn = $("#tts");
const tabs = Array.from(document.querySelectorAll('.chat-tab'));

// In‑memory chat histories
const chats = { chat1: [], chat2: [] };
let activeChat = 'chat1';
const DEFAULT_TAB_AVATAR = '/static/img/user.svg';
const tabAvatarMap = {};
// Preferred browser voices
const CHAT_VOICE_PREF = { chat1: '', chat2: '' };

// Avatars
const AVATARS = {
  user: { default: '/static/img/user.svg' },
  bot: { default: '/static/img/bot.svg', chat1: '/static/img/lbxx_chat.png' }
};

function createMsgRow(text, who) {
  const row = document.createElement('div');
  row.className = `msg-row ${who}`;
  const bubble = document.createElement('div');
  bubble.className = `msg ${who}`;
  bubble.textContent = text; // font controlled by CSS `.msg`
  const img = document.createElement('img');
  img.className = 'avatar';
  img.alt = who === 'user' ? 'user' : 'bot';
  const userAvatar = AVATARS.user.default;
  const botAvatar = AVATARS.bot[activeChat] || AVATARS.bot.default;
  img.src = who === 'user' ? userAvatar : botAvatar;
  if (who === 'bot') row.append(img, bubble); else row.append(bubble, img);
  return row;
}

function appendMessage(text, who = 'user') {
  const row = createMsgRow(text, who);
  output.appendChild(row);
  output.scrollTop = output.scrollHeight;
}

function renderChat(chatId) {
  output.innerHTML = '';
  (chats[chatId] || []).forEach(item => {
    output.appendChild(createMsgRow(item.text, item.who));
  });
  output.scrollTop = output.scrollHeight;
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  appendMessage(text, 'user');
  chats[activeChat].push({ who: 'user', text });
  input.value = '';
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, chat: activeChat }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '请求失败');
    appendMessage(data.reply, 'bot');
    chats[activeChat].push({ who: 'bot', text: data.reply });
    // chat1 使用服务端 edge-tts，chat2 仍用浏览器 TTS
    if (activeChat === 'chat1' && typeof playServerTTS === 'function') {
      const ok = await playServerTTS(data.reply, 'zh-CN-YunxiNeural', '-10%', '+2Hz');
      if (!ok && tts && tts.isEnabled && tts.isEnabled()) {
        tts.speak(data.reply, CHAT_VOICE_PREF[activeChat]);
      }
    } else if (tts && tts.isEnabled && tts.isEnabled()) {
      tts.speak(data.reply, CHAT_VOICE_PREF[activeChat]);
    }
  } catch (err) {
    appendMessage(`出错: ${err.message}`, 'bot');
  }
}

sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendMessage();
});

// Voice input init (if supported)
if (typeof setupVoiceInput === 'function') {
  setupVoiceInput({ input, button: micBtn, lang: 'zh-CN', autoSend: false });
  input.addEventListener('voice:autoSend', () => sendMessage());
}

// Init sidebar avatars
function initTabAvatars() {
  tabs.forEach(btn => {
    const id = btn.getAttribute('data-chat');
    const img = btn.querySelector('.chat-avatar');
    if (!img) return;
    const src = btn.dataset.avatar || DEFAULT_TAB_AVATAR;
    img.src = src;
    img.onerror = () => { img.onerror = null; img.src = DEFAULT_TAB_AVATAR; };
    tabAvatarMap[id] = src;
  });
}
initTabAvatars();

// Switch chat
tabs.forEach(btn => {
  btn.addEventListener('click', () => {
    const id = btn.getAttribute('data-chat');
    if (!id || id === activeChat) return;
    tabs.forEach(b => b.classList.toggle('active', b === btn));
    activeChat = id;
    renderChat(activeChat);
  });
});

// Initial render
renderChat(activeChat);

// TTS init (browser Web Speech only)
let tts = null;
if (typeof createTTS === 'function') {
  tts = createTTS({ lang: 'zh-CN', enabled: true });
  if (!tts.supported) {
    ttsBtn.disabled = true;
    ttsBtn.title = '当前浏览器不支持朗读';
  } else {
    ttsBtn.classList.add('tts-on');
    ttsBtn.addEventListener('click', () => {
      const on = !(tts && tts.isEnabled && tts.isEnabled());
      tts.setEnabled(on);
      ttsBtn.classList.toggle('tts-on', on);
    });
    // 预选不同的浏览器 voice（可选）
    (function chooseVoicesRetry(attempt = 0) {
      if (!tts || !tts.listVoices) return;
      const voices = tts.listVoices();
      if (!voices || voices.length === 0) {
        if (attempt < 10) setTimeout(() => chooseVoicesRetry(attempt + 1), 300);
        return;
      }
      const zh = voices.filter(v => (v.lang || '').toLowerCase().includes('zh'));
      const keywords = ['child', 'kid', 'boy'];
      const males = ['male', 'man'];
      const lower = (s) => (s || '').toLowerCase();
      const has = (v, arr) => arr.some(k => lower(v.name).includes(k) || lower(v.lang).includes(k));
      const findBy = (list, arr) => list.find(v => has(v, arr));
      let v1 = findBy(zh, keywords) || findBy(zh, males) || zh[0] || voices[0];
      let v2 = (zh.find(v => v.name !== (v1 && v1.name))) || (voices.find(v => v.name !== (v1 && v1.name))) || v1;
      CHAT_VOICE_PREF.chat1 = v1 ? v1.name : '';
      CHAT_VOICE_PREF.chat2 = v2 ? v2.name : '';
    })();
  }
}
