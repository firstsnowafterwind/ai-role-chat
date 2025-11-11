const $ = (sel) => document.querySelector(sel);

const output = $("#output");
const input = $("#message");
const sendBtn = $("#send");
const micBtn = $("#mic");
const ttsBtn = $("#tts");
const tabs = Array.from(document.querySelectorAll('.chat-tab'));

// 前端保存两个会话的消息
const chats = { chat1: [], chat2: [] };
let activeChat = 'chat1';
const DEFAULT_TAB_AVATAR = '/static/img/user.svg';
const tabAvatarMap = {};

const AVATARS = {
  me: { default: '/static/img/user.svg' },
  bot: '/static/img/bot.svg'
};

function createMsgRow(text, who) {
  const row = document.createElement('div');
  row.className = `msg-row ${who}`;
  const bubble = document.createElement('div');
  bubble.className = `msg ${who}`;
  bubble.textContent = text;
  const img = document.createElement('img');
  img.className = 'avatar';
  img.alt = who === 'me' ? '我' : '助手';
  const userAvatar = tabAvatarMap[activeChat] || AVATARS.me.default;
  img.src = who === 'me' ? userAvatar : AVATARS.bot;
  if (who === 'bot') row.append(img, bubble); else row.append(bubble, img);
  return row;
}

function appendMessage(text, who = "me") {
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
  appendMessage(text, "me");
  chats[activeChat].push({ who: 'me', text });
  input.value = "";
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, chat: activeChat }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "请求失败");
    appendMessage(data.reply, "bot");
    chats[activeChat].push({ who: 'bot', text: data.reply });
    // 朗读机器人回复
    if (tts && tts.isEnabled && tts.isEnabled()) {
      tts.speak(data.reply);
    }
  } catch (err) {
    appendMessage(`出错: ${err.message}`, "bot");
  }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

// 初始化语音输入（如果浏览器支持）
if (typeof setupVoiceInput === "function") {
  const controller = setupVoiceInput({ input, button: micBtn, lang: "zh-CN", autoSend: false });
  input.addEventListener("voice:autoSend", () => sendMessage());
}

// 初始化侧边栏头像（无配置时使用默认头像）
function initTabAvatars() {
  tabs.forEach(btn => {
    const id = btn.getAttribute('data-chat');
    const img = btn.querySelector('.chat-avatar');
    if (!img) return;
    const src = btn.dataset.avatar || DEFAULT_TAB_AVATAR;
    img.src = src;
    tabAvatarMap[id] = src;
  });
}
initTabAvatars();

// 切换会话
tabs.forEach(btn => {
  btn.addEventListener('click', () => {
    const id = btn.getAttribute('data-chat');
    if (!id || id === activeChat) return;
    tabs.forEach(b => b.classList.toggle('active', b === btn));
    activeChat = id;
    renderChat(activeChat);
  });
});

// 初始渲染
renderChat(activeChat);

// 初始化朗读
let tts = null;
if (typeof createTTS === 'function') {
  tts = createTTS({ lang: 'zh-CN', enabled: true });
  if (!tts.supported) {
    ttsBtn.disabled = true; ttsBtn.title = '当前浏览器不支持朗读';
  } else {
    ttsBtn.classList.add('tts-on');
    ttsBtn.addEventListener('click', () => {
      const on = !(tts && tts.isEnabled && tts.isEnabled());
      tts.setEnabled(on);
      ttsBtn.classList.toggle('tts-on', on);
    });
  }
}

