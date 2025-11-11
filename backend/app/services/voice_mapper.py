from typing import Tuple, Dict

# 每个会话（声线）的配置：基线与最大调制幅度
VOICE_CFG: Dict[str, Dict[str, object]] = {
    "chat1": {  # 少年/男童风
        "voice": "zh-CN-YunxiNeural",
        "base_rate_pct": 0,      # 基础语速偏移
        "base_pitch_hz": 0,      # 基础音高偏移
        # 最大调制幅度（极端情绪时的附加值）
        "rate_pos_max": +12,     # 极端积极时的最高加速（%）
        "rate_neg_max": -18,     # 极端消极时的最慢（%）
        "pitch_pos_max": +20,    # 极端积极时的最高升调（Hz）
        "pitch_neg_max": -12,    # 极端消极时的最低降调（Hz）
    },
    "chat2": {  # 女声风格
        "voice": "zh-CN-XiaoxiaoNeural",
        "base_rate_pct": 0,
        "base_pitch_hz": 0,
        "rate_pos_max": +10,
        "rate_neg_max": -16,
        "pitch_pos_max": +16,
        "pitch_neg_max": -10,
    },
}

def _clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x

def _deadband_nonlinear(e: float, deadband: float = 0.12, gamma: float = 1.25) -> float:
    """
    情绪 e∈[-1,1] → s∈[-1,1]
    - deadband: |e| 小于该阈值视为 0，避免轻微波动
    - gamma>1: 非线性缓和，接近 0 变化更小、极端更明显
    """
    e = _clamp(e, -1.0, 1.0)
    if abs(e) <= deadband:
        return 0.0
    # 去除死区后再归一化到 [-1,1]
    sign = 1.0 if e > 0 else -1.0
    mag = (abs(e) - deadband) / (1.0 - deadband)  # ∈[0,1]
    mag = mag ** gamma                             # 非线性
    return sign * mag

def map_tts_params(chat_type: str, emotion: float) -> Tuple[str, str, str]:
    """
    输入:
        chat_type: "chat1" / "chat2"（未知则用 chat1）
        emotion:  [-1,1] 极端消极=-1，极端积极=+1，普通情绪在区间内
    输出:
        (voice, rate, pitch)  —— 适用于 edge-tts 的字符串
    规则:
        - 轻微情绪 → 不改变（死区）
        - 消极 → 降速 & 降调（幅度略大于正向，更自然）
        - 积极 → 小幅提速 & 升调
    """
    key = (chat_type or "chat1").lower()
    cfg = VOICE_CFG.get(key, VOICE_CFG["chat1"])

    # 处理情绪：钳制 + 死区 + 非线性
    s = _deadband_nonlinear(emotion, deadband=0.12, gamma=1.25)  # s∈[-1,1]

    # 语速：正负向不对称映射
    if s >= 0:
        rate_delta = s * cfg["rate_pos_max"]   # 0 → +rate_pos_max
        pitch_delta = s * cfg["pitch_pos_max"]
    else:
        rate_delta = (-s) * cfg["rate_neg_max"]  # 注意 rate_neg_max 是负数
        pitch_delta = (-s) * cfg["pitch_neg_max"]

    # 叠加基线并四舍五入到整数（edge-tts 支持整数% / Hz）
    rate_pct = int(round(cfg["base_rate_pct"] + rate_delta))
    pitch_hz = int(round(cfg["base_pitch_hz"] + pitch_delta))

    voice = cfg["voice"]
    rate = f"{rate_pct:+d}%"
    pitch = f"{pitch_hz:+d}Hz"
    return voice, rate, pitch
