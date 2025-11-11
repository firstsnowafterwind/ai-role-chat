(function (global) {
  const HAS_SR = "SpeechRecognition" in global || "webkitSpeechRecognition" in global;

  function createRecognizer({ lang = "zh-CN", interimResults = false }) {
    const SR = global.SpeechRecognition || global.webkitSpeechRecognition;
    if (!SR) return null;
    const r = new SR();
    r.lang = lang;
    r.interimResults = interimResults;
    r.continuous = false;
    return r;
  }

  function setupVoiceInput({ input, button, lang = "zh-CN", autoSend = false, onText }) {
    if (!input || !button) return { supported: false };
    if (!HAS_SR) {
      button.disabled = true;
      button.title = "当前浏览器不支持语音识别";
      return { supported: false };
    }

    const recognizer = createRecognizer({ lang });
    let running = false;

    function start() {
      if (!recognizer || running) return;
      running = true;
      button.classList.add("recording");
      try { recognizer.start(); } catch (e) { /* already started */ }
    }

    function stop() {
      if (!recognizer || !running) return;
      running = false;
      button.classList.remove("recording");
      try { recognizer.stop(); } catch (e) { /* ignore */ }
    }

    recognizer.addEventListener("result", (ev) => {
      const last = ev.results[ev.results.length - 1];
      if (!last) return;
      const text = last[0].transcript.trim();
      if (text) {
        input.value = text;
        if (onText) onText(text);
      }
    });

    recognizer.addEventListener("end", () => {
      running = false;
      button.classList.remove("recording");
      if (autoSend && input.value.trim()) {
        const evt = new CustomEvent("voice:autoSend");
        input.dispatchEvent(evt);
      }
    });

    recognizer.addEventListener("error", () => {
      running = false;
      button.classList.remove("recording");
    });

    button.addEventListener("click", () => {
      if (running) stop(); else start();
    });

    return { supported: true, start, stop };
  }

  global.setupVoiceInput = setupVoiceInput;
})(window);

