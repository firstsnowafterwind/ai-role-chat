import os
import uuid
import asyncio
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import edge_tts  # ✅ 使用 edge-tts

DEFAULT_TTS_OPTIONS = {
    "rate": "+0%",  # 语速
    "volume": "+0%",
    "voice": "zh-CN-XiaoxiaoNeural"  # 默认 voice
}

# 角色和 voice 映射
ROLE_VOICE_MAP = {
    "c1": "zh-CN-XiaoxiaoNeural",
    "c2": "zh-CN-YunjianNeural",
    "c3": "zh-CN-YunxiNeural",
    "c4": "en-US-AriaNeural",
    "c5": "en-US-GuyNeural",
    "c6": "en-US-JennyNeural"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, "tts_audio")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

@dataclass
class TTSState:
    text: str = ""
    options: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_TTS_OPTIONS))
    audio_path: Optional[str] = None

_state = TTSState()

async def synthesize_async(text: str, options: Dict[str, Any], voice: str) -> str:
    """使用 edge-tts 合成语音"""
    communicate = edge_tts.Communicate(text, voice=voice, rate=options.get("rate", "+0%"))
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
    await communicate.save(filepath)
    return filepath

def synthesize(text: str, options: Dict[str, Any], role: str) -> str:
    """同步封装"""
    voice = ROLE_VOICE_MAP.get(role, options.get("voice", DEFAULT_TTS_OPTIONS["voice"]))
    return asyncio.run(synthesize_async(text, options, voice))

def set_current(text: str, options: Optional[Dict[str, Any]] = None, role: str = "c1") -> None:
    global _state
    _state.text = text or ""
    opts = options or dict(DEFAULT_TTS_OPTIONS)
    _state.options = opts
    _state.audio_path = synthesize(_state.text, opts, role)

def get_current() -> TTSState:
    return _state
