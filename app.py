import os
import uuid
from flask import Flask, request, jsonify, send_file
from asr_service import transcribe_file
from text_process import process_text
from tts_service import set_current, get_current

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "未收到音频数据"}), 400

    file = request.files["audio"]
    role = request.form.get("role", "c1")

    ext = ".webm"
    os.makedirs("uploads", exist_ok=True)
    temp_path = os.path.join("uploads", f"rec_{uuid.uuid4().hex}{ext}")
    file.save(temp_path)

    try:
        raw_text = transcribe_file(temp_path)
        print(f"[ASR 原文] {raw_text}")

        processed_text, tts_options = process_text(raw_text, role)
        set_current(processed_text, tts_options, role=role)


        return jsonify({
            "raw_text": raw_text,
            "processed_text": processed_text,
            "tts": get_current().options
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.remove(temp_path)
        except:
            pass

@app.route("/api/tts_audio", methods=["GET"])
def api_tts_audio():
    state = get_current()
    if not state.audio_path or not os.path.exists(state.audio_path):
        return jsonify({"error": "No audio generated"}), 404
    return send_file(state.audio_path, mimetype="audio/mpeg")

@app.route("/api/reset", methods=["POST"])
def api_reset():
    set_current("", {})
    return jsonify({"status": "success", "message": "对话已清空"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
