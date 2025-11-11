from backend.app.main import app


if __name__ == "__main__":
    # Simple local entry point
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("DEBUG", True))

