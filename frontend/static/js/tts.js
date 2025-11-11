(function (global) {
  const synth = window.speechSynthesis;

  function createTTS({ lang = 'zh-CN', rate = 1, pitch = 1, volume = 1, enabled = true } = {}) {
    const supported = typeof synth !== 'undefined' && 'SpeechSynthesisUtterance' in global;
    let on = enabled && supported;
    let voices = [];

    function loadVoices() {
      try { voices = synth.getVoices() || []; } catch { voices = []; }
    }
    if (supported) {
      loadVoices();
      synth.addEventListener('voiceschanged', loadVoices);
    }

    function findVoice(nameOrLang) {
      if (!nameOrLang) return null;
      return voices.find(v => v.name === nameOrLang)
          || voices.find(v => v.lang === nameOrLang)
          || null;
    }

    function speak(text, voiceName) {
      if (!supported || !on) return;
      if (!text) return;
      // 取消当前发声，避免重叠
      try { synth.cancel(); } catch (e) {}
      const u = new SpeechSynthesisUtterance(String(text));
      u.lang = lang;
      u.rate = rate;
      u.pitch = pitch;
      u.volume = volume;
      const v = findVoice(voiceName) || voices.find(v => v.lang === lang);
      if (v) u.voice = v;
      synth.speak(u);
    }

    function cancel() {
      if (!supported) return;
      try { synth.cancel(); } catch (e) {}
    }

    function setEnabled(v) { on = !!v && supported; if (!on) cancel(); }
    function isEnabled() { return on; }
    function listVoices() { return voices.map(v => ({ name: v.name, lang: v.lang })); }

    return { supported, speak, cancel, setEnabled, isEnabled, listVoices };
  }

  global.createTTS = createTTS;

  // 服务端 TTS（edge-tts）播放：POST /api/tts，返回 mp3 字节后直接播放
  async function playServerTTS(text, optsOrVoice, rate, pitch) {
    if (!text) return false;
    try {
      let payload;
      if (typeof optsOrVoice === 'object' && optsOrVoice !== null) {
        // new signature: { chat, emotion }
        const { chat, emotion } = optsOrVoice;
        payload = { text, chat, emotion };
      } else {
        // backward-compat signature: (text, voice, rate, pitch)
        payload = { text, voice: optsOrVoice, rate, pitch };
      }

      const res = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Server TTS failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.onended = () => URL.revokeObjectURL(url);
      await audio.play();
      return true;
    } catch (e) {
      return false;
    }
  }

  global.playServerTTS = playServerTTS;
})(window);
