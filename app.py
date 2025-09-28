# app.py
# 职责：串起整个流程
# 前端上传音频 -> /api/transcribe
#  1) 保存临时文件
#  2) 调用 asr_service.transcribe_file 得到 raw_text
#  3) print 原始文本
#  4) 调用 process_text(raw_text) 得到 processed_text + tts_options
#  5) 更新 tts_service 当前朗读内容
#  6) 返回 JSON（供前端显示 & TTS 朗读）

import os, uuid
from flask import Flask, request, jsonify

from asr_service import transcribe_file
import tts_service as TTS

app = Flask(__name__, static_folder="static", static_url_path="")

# ========== 文本处理函数 ==========
def process_text(raw_text: str):
    """
    使用 ChatGLM3-6B 进行中文对话回复。
    返回: (processed_text: str, tts_options: dict)
    """
    input_text = raw_text.strip()
    return raw_text
# ========== 文本处理函数 END ==========

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    file = request.files["audio"]
    mimetype = (file.mimetype or "").lower()

    ext_map = {
        "audio/webm": ".webm", "audio/mp4": ".mp4",
        "audio/mpeg": ".mp3", "audio/aac": ".aac",
        "audio/wav": ".wav",  "audio/ogg": ".ogg",
        "audio/x-m4a": ".m4a", "audio/m4a": ".m4a",
    }
    ext = ext_map.get(mimetype, ".bin")

    os.makedirs("uploads", exist_ok=True)
    temp_path = os.path.join("uploads", f"rec_{uuid.uuid4().hex}{ext}")
    file.save(temp_path)

    try:
        asr_kwargs = dict(request.args)
        raw_text = transcribe_file(temp_path, **asr_kwargs)
        print(f"[ASR 原文] {raw_text}")

        processed_text, tts_options = process_text(raw_text)
        TTS.set_current(processed_text, tts_options)

        return jsonify({
            "raw_text": raw_text,
            "processed_text": processed_text,
            "tts": TTS.get_current().options
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            os.remove(temp_path)
        except:
            pass

@app.route("/api/tts", methods=["GET"])
def api_tts_get():
    state = TTS.get_current()
    return jsonify({"text": state.text, "tts": state.options})

@app.route("/api/reset", methods=["POST"])
def api_reset():
    """重置对话历史"""
    try:
        return jsonify({"status": "success", "message": "对话历史已重置"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
