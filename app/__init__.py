from __future__ import annotations

import os
import time
from pathlib import Path

from flask import Flask
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.middleware.proxy_fix import ProxyFix

from config import config_map

from app.extensions import bcrypt, csrf, db, login_manager, migrate, server_session, talisman
from app.routes import register_blueprints
from app.services.schema import apply_schema_updates
from app.services.seed import seed_reference_data


DATABASE_INIT_LOCK_ID = 90840261


def _validate_runtime_config(app: Flask, config_name: str) -> None:
    if config_name == "production" and app.config["SECRET_KEY"] == "change-me-in-production":
        raise RuntimeError("SECRET_KEY must be set to a strong random value in production.")


def _initialize_database(app: Flask) -> None:
    retries = app.config["DB_CONNECT_RETRIES"]
    delay = app.config["DB_CONNECT_RETRY_SECONDS"]

    with app.app_context():
        from app import models  # noqa: F401

        for attempt in range(1, retries + 1):
            try:
                db.session.execute(
                    text("SELECT pg_advisory_xact_lock(:lock_id)"),
                    {"lock_id": DATABASE_INIT_LOCK_ID},
                )
                db.create_all()
                apply_schema_updates()
                seed_reference_data()
                return
            except OperationalError as exc:
                db.session.rollback()
                if attempt == retries:
                    raise RuntimeError("PostgreSQL did not become available during app startup.") from exc
                app.logger.warning(
                    "PostgreSQL is not ready yet; retrying startup initialization (%s/%s).",
                    attempt,
                    retries,
                )
                time.sleep(delay)
            except SQLAlchemyError:
                db.session.rollback()
                raise
            finally:
                db.session.remove()


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    selected_config = config_name or os.getenv("FLASK_ENV", "default")
    app.config.from_object(config_map.get(selected_config, config_map["default"]))
    _validate_runtime_config(app, selected_config)

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
    _initialize_database(app)

    return app
