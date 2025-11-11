from flask import Blueprint, jsonify, request
from ..services.chat_service import generate_reply
from ..utils.logger import get_logger


chat_bp = Blueprint("chat", __name__, url_prefix="/api")
logger = get_logger(__name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        chat = (data.get("chat") or "chat1").strip() or "chat1"
        if not message:
            return jsonify({"error": "message is required"}), 400

        reply = generate_reply(message, chat)
        # 避免使用 logging 的保留字段名（如 'message'），否则会抛异常
        logger.info("/api/chat ok | chat=%s msg=%r reply=%r", chat, message, reply)
        return jsonify({"reply": reply, "chat": chat})
    except Exception as exc:
        logger.exception("Unhandled error in /api/chat: %s", exc)
        return jsonify({"error": "internal server error"}), 500
