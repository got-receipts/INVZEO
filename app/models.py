from __future__ import annotations

from datetime import datetime
from enum import Enum

from flask_login import UserMixin

from app.extensions import bcrypt, db, login_manager


class Role(str, Enum):
    ADMIN = "admin"
    OFFICER = "officer"
    INFORMANT = "informant"
    ANALYST = "analyst"


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


case_departments = db.Table(
    "case_departments",
    db.Column("case_id", db.Integer, db.ForeignKey("cases.id"), primary_key=True),
    db.Column("department_id", db.Integer, db.ForeignKey("departments.id"), primary_key=True),
)


class Department(TimestampMixin, db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True, nullable=False)
    county = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    agency_contact = db.Column(db.String(160), nullable=False)
    notes = db.Column(db.Text)

    users = db.relationship("User", back_populates="department", lazy=True)
    primary_cases = db.relationship("Case", back_populates="primary_department", lazy=True)
    cases = db.relationship(
        "Case",
        secondary=case_departments,
        back_populates="departments",
        lazy="dynamic",
    )


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), default=Role.INFORMANT.value, nullable=False)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))

    department = db.relationship("Department", back_populates="users")
    cases = db.relationship("Case", back_populates="owner", lazy=True)
    notes = db.relationship("CaseNote", back_populates="author", lazy=True)
    reports = db.relationship("Report", back_populates="author", lazy=True)
    audit_logs = db.relationship("AuditLog", back_populates="user", lazy=True)
    messages_sent = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        lazy=True,
    )
    messages_received = db.relationship(
        "Message",
        foreign_keys="Message.recipient_id",
        back_populates="recipient",
        lazy=True,
    )

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_active(self) -> bool:
        return self.is_active_user


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return User.query.get(int(user_id))


class Case(TimestampMixin, db.Model):
    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(40), unique=True, nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    officer_contact = db.Column(db.String(160), nullable=False)
    case_type = db.Column(db.String(120), nullable=False)
    incident_location = db.Column(db.String(255), nullable=False)
    narrative = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(40), default="Open", nullable=False)
    priority = db.Column(db.String(20), default="Medium", nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    primary_department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)

    owner = db.relationship("User", back_populates="cases")
    primary_department = db.relationship("Department", back_populates="primary_cases")
    departments = db.relationship(
        "Department",
        secondary=case_departments,
        back_populates="cases",
        lazy="joined",
    )
    attachments = db.relationship(
        "Attachment",
        back_populates="case",
        cascade="all, delete-orphan",
        lazy=True,
    )
    notes = db.relationship(
        "CaseNote",
        back_populates="case",
        cascade="all, delete-orphan",
        lazy=True,
    )
    activities = db.relationship(
        "CaseActivity",
        back_populates="case",
        cascade="all, delete-orphan",
        lazy=True,
    )
    reports = db.relationship(
        "Report",
        back_populates="case",
        cascade="all, delete-orphan",
        lazy=True,
    )


class Attachment(TimestampMixin, db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(120), nullable=False)
    storage_path = db.Column(db.String(255), nullable=False)
    encrypted_key = db.Column(db.Text, nullable=False)
    file_size = db.Column(db.Integer, nullable=False, default=0)

    case = db.relationship("Case", back_populates="attachments")


class CaseNote(TimestampMixin, db.Model):
    __tablename__ = "case_notes"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)

    case = db.relationship("Case", back_populates="notes")
    author = db.relationship("User", back_populates="notes")


class CaseActivity(TimestampMixin, db.Model):
    __tablename__ = "case_activities"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    actor_name = db.Column(db.String(120), nullable=False)
    action = db.Column(db.String(160), nullable=False)
    details = db.Column(db.Text)

    case = db.relationship("Case", back_populates="activities")


class Report(TimestampMixin, db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    export_path = db.Column(db.String(255))

    case = db.relationship("Case", back_populates="reports")
    author = db.relationship("User", back_populates="reports")


class PublicDataSource(TimestampMixin, db.Model):
    __tablename__ = "public_data_sources"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True, nullable=False)
    source_url = db.Column(db.String(255), nullable=False)
    search_url = db.Column(db.String(255), nullable=False)
    record_type = db.Column(db.String(80), nullable=False)
    county = db.Column(db.String(80))
    agency = db.Column(db.String(120), nullable=False)
    notes = db.Column(db.Text)
    requires_auth = db.Column(db.Boolean, default=False, nullable=False)
    requires_payment = db.Column(db.Boolean, default=False, nullable=False)


class AuditLog(TimestampMixin, db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"))
    action = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    details = db.Column(db.Text)

    user = db.relationship("User", back_populates="audit_logs")


class Message(TimestampMixin, db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    recipient = db.relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="messages_received",
    )