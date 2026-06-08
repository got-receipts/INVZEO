from __future__ import annotations

import os
from pathlib import Path

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from config import config_map

from app.extensions import bcrypt, csrf, db, login_manager, migrate, server_session, talisman
from app.routes import register_blueprints
from app.services.seed import seed_reference_data


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    selected_config = config_name or os.getenv("FLASK_ENV", "default")
    app.config.from_object(config_map[selected_config])

    Path(app.config["STORAGE_ROOT"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["EXPORT_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["SESSION_FILE_DIR"]).mkdir(parents=True, exist_ok=True)

    csp = {
        "default-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "font-src": ["'self'", "data:"],
    }

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    server_session.init_app(app)
    talisman.init_app(
        app,
        content_security_policy=csp,
        force_https=os.getenv("FLASK_ENV") == "production",
    )

    register_blueprints(app)

    with app.app_context():
        from app import models

        db.create_all()
        seed_reference_data()

    return app