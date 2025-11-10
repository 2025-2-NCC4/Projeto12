import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from .config import Config
from .extensions import db, login_manager, cache   # ✅ cache importado
from .models import Usuario
from .data import data_bp

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Define cache se não definido em Config
    app.config.setdefault("CACHE_TYPE", "simple")
    app.config.setdefault("CACHE_DEFAULT_TIMEOUT", 300)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # === INIT EXTENSIONS ===
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)  # ✅ adicionamos o cache

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # === BLUEPRINTS ===
    from .auth import auth_bp
    from .dashboards import dash_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(data_bp)

    # === HEALTH CHECK ===
    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    # === CREATE TABLES ===
    with app.app_context():
        db.create_all()

    return app
