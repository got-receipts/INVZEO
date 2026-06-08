from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_STORAGE_ROOT = Path(os.getenv("APP_STORAGE_ROOT", BASE_DIR / "runtime"))

DATABASE_URL_ENV_NAMES = (
    "DATABASE_URL",
    "DATABASE_PRIVATE_URL",
    "DATABASE_PUBLIC_URL",
    "POSTGRES_URL",
    "POSTGRESQL_URL",
)

PG_ENV_ALIASES = {
    "host": ("PGHOST", "POSTGRES_HOST", "DATABASE_HOST"),
    "port": ("PGPORT", "POSTGRES_PORT", "DATABASE_PORT"),
    "user": ("PGUSER", "POSTGRES_USER", "DATABASE_USER"),
    "password": ("PGPASSWORD", "POSTGRES_PASSWORD", "DATABASE_PASSWORD"),
    "database": ("PGDATABASE", "POSTGRES_DB", "POSTGRES_DATABASE", "DATABASE_NAME"),
}


def _first_env_value(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _database_url_from_pg_vars() -> str:
    host = _first_env_value(*PG_ENV_ALIASES["host"])
    user = _first_env_value(*PG_ENV_ALIASES["user"])
    password = _first_env_value(*PG_ENV_ALIASES["password"])
    database = _first_env_value(*PG_ENV_ALIASES["database"])
    port = _first_env_value(*PG_ENV_ALIASES["port"]) or "5432"

    if not all([host, user, password, database]):
        return ""

    encoded_user = quote(user, safe="")
    encoded_password = quote(password, safe="")
    encoded_database = quote(database, safe="")
    return f"postgresql+psycopg://{encoded_user}:{encoded_password}@{host}:{port}/{encoded_database}"


def require_database_url() -> str:
    raw_url = _first_env_value(*DATABASE_URL_ENV_NAMES) or _database_url_from_pg_vars()
    if raw_url:
        return raw_url

    accepted_url_vars = ", ".join(DATABASE_URL_ENV_NAMES)
    accepted_pg_vars = ", ".join(
        " / ".join(names)
        for names in PG_ENV_ALIASES.values()
    )
    raise RuntimeError(
        "PostgreSQL configuration is missing. Set one full connection URL "
        f"({accepted_url_vars}) or provide PG-style fields ({accepted_pg_vars}). "
        "On Railway, add a reference variable on the web service such as "
        "DATABASE_URL=${{Postgres.DATABASE_URL}}, then redeploy."
    )


def normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgresql://") and "+psycopg" not in raw_url:
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url


def postgres_database_url() -> str:
    database_url = normalize_database_url(require_database_url())
    if not database_url.startswith(("postgresql+psycopg://", "postgresql://", "postgres://")):
        raise RuntimeError("The configured database URL must point to PostgreSQL.")
    return database_url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    APP_ENCRYPTION_KEY = os.getenv("APP_ENCRYPTION_KEY", SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = postgres_database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
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
    APP_NAME = "INVZEO Investigations"
    PUBLIC_DATA_TIMEOUT = 10
    DB_CONNECT_RETRIES = int(os.getenv("DB_CONNECT_RETRIES", "20"))
    DB_CONNECT_RETRY_SECONDS = float(os.getenv("DB_CONNECT_RETRY_SECONDS", "2"))


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
