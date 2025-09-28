"""
asr_service.py
职责：把音频文件转成文本（Whisper）。
对外暴露：transcribe_file(audio_path: str, **kwargs) -> str
可选参数（白名单）会透传给 whisper.transcribe，如 language/task/temperature/beam_size 等。
"""

import whisper
import os
from opencc import OpenCC
cc_t2s = OpenCC('t2s')  # 繁→简

# 只加载一次模型，避免每次请求都下载/初始化
MODEL_NAME = os.environ.get("WHISPER_MODEL", "medium")  # 可 tiny/base/small/medium/large
_model = whisper.load_model(MODEL_NAME)

def _parse_transcribe_kwargs(user_kwargs: dict) -> dict:
    """
    安全解析 & 白名单过滤，把外部 kwargs 转成可透传给 whisper.transcribe 的参数。
    你可按需扩展范围校验。
    """
    if not isinstance(user_kwargs, dict):
        return {}

    allowed = {
        "language": str,          # 例如: 'zh'/'en'；不传=自动检测
        "task": str,              # 'transcribe' or 'translate'
        "temperature": float,     # 0.0 ~ 1.0
        "beam_size": int,         # 1 ~ 10
        "best_of": int,           # 1 ~ 5
        "patience": float,        # 0.0 ~ 2.0
        "initial_prompt": str,    # 可作为前置提示
        "fp16": lambda v: bool(str(v).lower() in ("1", "true", "yes")),
        "without_timestamps": lambda v: bool(str(v).lower() in ("1", "true", "yes")),
    }
    out = {}
    for k, caster in allowed.items():
        if k not in user_kwargs:
            continue
        raw = user_kwargs[k]
        try:
            val = caster(raw)
        except Exception:
            continue  # 转换失败直接忽略，避免抛异常
        # 简单范围校验（按需细化）
        if k == "temperature" and not (0.0 <= val <= 1.0): continue
        if k == "beam_size" and not (1 <= val <= 10): continue
        if k == "best_of" and not (1 <= val <= 5): continue
        if k == "patience" and not (0.0 <= val <= 2.0): continue
        if k == "task" and val not in ("transcribe", "translate"): continue
        out[k] = val
    return out

def transcribe_file(audio_path: str, **kwargs) -> str:
    """
    使用 Whisper 把本地音频文件转成文本。
    参数：
      audio_path: 音频文件路径；需 ffmpeg 可解码的格式(webm/mp4/aac/wav/…)
      **kwargs:   可选的 whisper.transcribe 参数（会先经过白名单过滤）
    返回：
      识别出的文本（str），失败返回 ""。
    """
    if not audio_path or not os.path.exists(audio_path):
        return ""

    safe_kwargs = _parse_transcribe_kwargs(kwargs)

    # 默认固定中文可加速；若你要自动检测语言，删除 language 配置即可
    safe_kwargs.setdefault("language", "zh")

    try:
        result = _model.transcribe(audio_path, **safe_kwargs)
        text = (result.get("text") or "").strip()
        text_simplified = cc_t2s.convert(text)
        return text_simplified
    except Exception as e:
        # 这里不抛异常，统一返回空串；上层自行决定如何处理
        print("[ASR Error]", e)
        return ""