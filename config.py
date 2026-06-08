from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_STORAGE_ROOT = Path(os.getenv("APP_STORAGE_ROOT", BASE_DIR / "runtime"))


def require_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL", "").strip()
    if not raw_url:
        raise RuntimeError("DATABASE_URL must be set to a PostgreSQL connection string.")
    return raw_url


def normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgresql://") and "+psycopg" not in raw_url:
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url


def postgres_database_url() -> str:
    database_url = normalize_database_url(require_database_url())
    if not database_url.startswith(("postgresql+psycopg://", "postgresql://", "postgres://")):
        raise RuntimeError("DATABASE_URL must point to a PostgreSQL database.")
    return database_url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    APP_ENCRYPTION_KEY = os.getenv("APP_ENCRYPTION_KEY", SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = postgres_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PREFERRED_URL_SCHEME = "https"
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = str(DEFAULT_STORAGE_ROOT / "sessions")
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    STORAGE_ROOT = str(DEFAULT_STORAGE_ROOT)
    UPLOAD_FOLDER = str(DEFAULT_STORAGE_ROOT / "uploads")
    EXPORT_FOLDER = str(DEFAULT_STORAGE_ROOT / "exports")
    WTF_CSRF_TIME_LIMIT = None
    APP_NAME = "Confidential Informant Help Desk"
    PUBLIC_DATA_TIMEOUT = 10


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
