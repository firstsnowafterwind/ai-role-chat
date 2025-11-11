import asyncio
from flask import Blueprint, jsonify, request, Response
from ..services.text_analyzer import analyze_emotion
from ..services.voice_mapper import map_tts_params


tts_bp = Blueprint("tts", __name__, url_prefix="/api/tts")


async def _edge_tts_bytes(text: str, voice: str, rate: str | None = None, pitch: str | None = None) -> bytes:
    """Call edge-tts to synthesize audio and return mp3 bytes (no file IO)."""
    import edge_tts  # lazy import; requires network during synthesis

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)


@tts_bp.post("")
def synthesize():
    """Synthesize speech for the given text using chat+emotion mapping.

    Request JSON:
      - text: required
      - chat: optional, defaults to "chat1"
      - emotion: optional float [-1, 1]; if missing, backend estimates
    """
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    chat = (data.get("chat") or "chat1").strip()
    emotion = data.get("emotion")

    if not text:
        return jsonify({"error": "text is required"}), 400

    try:
        emo = float(emotion)
    except (TypeError, ValueError):
        emo = analyze_emotion(text)
    emo = max(-1.0, min(1.0, emo))

    # Unified mapping: chat_type + emotion -> voice/rate/pitch
    voice, rate, pitch = map_tts_params(chat, emo)

    try:
        audio = asyncio.run(_edge_tts_bytes(text=text, voice=voice, rate=rate, pitch=pitch))
        if not audio:
            return jsonify({"error": "synthesis failed"}), 500
        return Response(audio, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": f"synthesis error: {e}"}), 500
