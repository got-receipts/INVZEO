from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from io import BytesIO
from pathlib import Path

from cryptography.fernet import Fernet
from flask import abort, current_app, flash, has_request_context, request
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Attachment, AuditLog, Case, CaseActivity, Role


ALLOWED_EXTENSIONS = {
    "aac",
    "doc",
    "docx",
    "gif",
    "heic",
    "jpeg",
    "jpg",
    "m4a",
    "mp3",
    "pdf",
    "png",
    "txt",
    "wav",
    "webp",
    "zip",
}


def roles_required(*roles: str):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def can_access_case(user, case: Case) -> bool:
    if user.role in {Role.ADMIN.value, Role.OFFICER.value, Role.ANALYST.value}:
        return True
    return case.owner_id == user.id


def ensure_case_access(case: Case) -> None:
    if not can_access_case(current_user, case):
        abort(403)


def generate_case_number() -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d")
    return f"CI-{stamp}-{secrets.randbelow(9000) + 1000}"


def _fernet_key() -> Fernet:
    secret = current_app.config["APP_ENCRYPTION_KEY"].encode("utf-8")
    digest = hashlib.sha256(secret).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def save_encrypted_upload(file_storage: FileStorage, case: Case) -> Attachment | None:
    if not file_storage or not file_storage.filename:
        return None

    extension = file_storage.filename.rsplit(".", 1)[-1].lower() if "." in file_storage.filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        flash(f"Skipped unsupported file type for {file_storage.filename}", "warning")
        return None

    safe_name = secure_filename(file_storage.filename)
    storage_dir = Path(current_app.config["UPLOAD_FOLDER"]) / case.case_number
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_name = f"{secrets.token_hex(8)}.bin"
    storage_path = storage_dir / storage_name
    raw_bytes = file_storage.read()
    encrypted_payload = _fernet_key().encrypt(raw_bytes)
    storage_path.write_bytes(encrypted_payload)

    return Attachment(
        case=case,
        filename=storage_name,
        original_filename=safe_name,
        mime_type=file_storage.mimetype or "application/octet-stream",
        storage_path=str(storage_path),
        encrypted_key=hashlib.sha256(current_app.config["APP_ENCRYPTION_KEY"].encode("utf-8")).hexdigest()[:16],
        file_size=len(raw_bytes),
    )


def load_decrypted_bytes(attachment: Attachment) -> BytesIO:
    encrypted_payload = Path(attachment.storage_path).read_bytes()
    return BytesIO(_fernet_key().decrypt(encrypted_payload))


def log_audit(action: str, user=None, case: Case | None = None, details: str | None = None) -> None:
    entry = AuditLog(
        user_id=user.id if user else None,
        case_id=case.id if case else None,
        action=action,
        ip_address=request.remote_addr if has_request_context() else None,
        user_agent=request.headers.get("User-Agent") if has_request_context() else None,
        details=details,
    )
    db.session.add(entry)
    db.session.commit()


def record_case_activity(case: Case, action: str, details: str | None = None, actor_name: str | None = None) -> None:
    db.session.add(
        CaseActivity(
            case=case,
            actor_name=actor_name or getattr(current_user, "full_name", "System"),
            action=action,
            details=details,
        )
    )