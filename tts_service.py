"""
tts_service.py
职责：在后端集中管理“要朗读的文本”与“朗读参数”，供前端 Web Speech API 使用。
不做语音合成（浏览器负责）。
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

DEFAULT_TTS_OPTIONS = {
    "lang": "zh-CN",   # 浏览器 TTS 的语言（如 zh-CN / en-US）
    "rate": 1.0,       # 语速 0.5~2.0（浏览器端将做最终约束）
    "pitch": 1.0,      # 音高 0.0~2.0
    "voice": None      # 可选：浏览器语音名称（匹配不到则忽略，用 lang）
}

def normalize_tts_options(options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """合并默认值并做简单范围裁剪。"""
    opts = dict(DEFAULT_TTS_OPTIONS)
    if isinstance(options, dict):
        if "lang" in options and isinstance(options["lang"], str):
            opts["lang"] = options["lang"]
        if "rate" in options:
            try:
                r = float(options["rate"])
                opts["rate"] = min(max(r, 0.5), 2.0)
            except Exception:
                pass
        if "pitch" in options:
            try:
                p = float(options["pitch"])
                opts["pitch"] = min(max(p, 0.0), 2.0)
            except Exception:
                pass
        if "voice" in options:
            v = options["voice"]
            opts["voice"] = v if (v is None or isinstance(v, str)) else None
    return opts

@dataclass
class TTSState:
    text: str = ""                                  # 要朗读的文本
    options: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_TTS_OPTIONS))

# 简单的进程内状态（比赛/作业足够；生产请持久化或用缓存）
_state = TTSState()

def set_current(text: str, options: Optional[Dict[str, Any]] = None) -> None:
    """更新“当前要朗读的文本及其 TTS 参数”。"""
    _state.text = text or ""
    _state.options = normalize_tts_options(options)

def get_current() -> TTSState:
    """获取当前的朗读文本与参数。"""
    return _state
