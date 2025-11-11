import os
from flask import Flask
from flask_cors import CORS


def create_app():
    # Resolve frontend paths first so we can attach Flask static dir correctly
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    frontend_dir = os.path.join(project_root, "frontend")
    frontend_static_dir = os.path.join(frontend_dir, "static")

    # Point Flask's built-in /static route to the frontend static directory
    app = Flask(__name__, static_url_path="/static", static_folder=frontend_static_dir)

    # Load config
    from .config import Config
    app.config.from_object(Config)

    # Enable CORS for API routes if needed
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from .routes.chat_routes import chat_bp
    app.register_blueprint(chat_bp)

    # Serve frontend index
    from flask import send_from_directory

    @app.route("/")
    def index():
        return send_from_directory(frontend_dir, "index.html")

    # 避免控制台反复出现 favicon 404
    from flask import Response

    @app.route("/favicon.ico")
    def favicon():
        return Response(status=204)

    return app
