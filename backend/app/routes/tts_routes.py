import asyncio
from flask import Blueprint, jsonify, request, Response


tts_bp = Blueprint("tts", __name__, url_prefix="/api/tts")


async def _edge_tts_bytes(text: str, voice: str, rate: str | None = None, pitch: str | None = None) -> bytes:
    import edge_tts  # lazy import; requires network during synthesis

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)


@tts_bp.post("")
def synthesize():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    # defaults for chat1少年音色 - 蜡笔小新
    voice = (data.get("voice") or "zh-CN-YunxiNeural").strip()
    rate = (data.get("rate") or "-20%").strip()
    pitch = (data.get("pitch") or "+2Hz").strip()

    if not text:
        return jsonify({"error": "text is required"}), 400

    try:
        audio = asyncio.run(_edge_tts_bytes(text=text, voice=voice, rate=rate, pitch=pitch))
        if not audio:
            return jsonify({"error": "synthesis failed"}), 500
        return Response(audio, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": f"synthesis error: {e}"}), 500

