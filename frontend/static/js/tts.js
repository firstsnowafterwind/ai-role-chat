(function (global) {
  const synth = window.speechSynthesis;

  function createTTS({ lang = 'zh-CN', rate = 1, pitch = 1, volume = 1, enabled = true } = {}) {
    const supported = typeof synth !== 'undefined' && 'SpeechSynthesisUtterance' in global;
    let on = enabled && supported;

    function speak(text) {
      if (!supported || !on) return;
      if (!text) return;
      // 取消当前发声，避免重叠
      try { synth.cancel(); } catch (e) {}
      const u = new SpeechSynthesisUtterance(String(text));
      u.lang = lang;
      u.rate = rate;
      u.pitch = pitch;
      u.volume = volume;
      synth.speak(u);
    }

    function cancel() {
      if (!supported) return;
      try { synth.cancel(); } catch (e) {}
    }

    function setEnabled(v) { on = !!v && supported; if (!on) cancel(); }
    function isEnabled() { return on; }

    return { supported, speak, cancel, setEnabled, isEnabled };
  }

  global.createTTS = createTTS;
})(window);

