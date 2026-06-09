from __future__ import annotations

import os

from sqlalchemy.dialects.postgresql import insert

from app.extensions import db
from app.models import Department, PublicDataSource, Role, User
from app.services.public_data import DEFAULT_PUBLIC_SOURCES


DEFAULT_DEPARTMENTS = [
    {
        "name": "Albany Police Department",
        "county": "Albany",
        "address": "165 Henry Johnson Blvd, Albany, NY 12210",
        "phone": "518-438-4000",
        "email": "records@albanypdny.gov",
        "agency_contact": "Duty Supervisor",
        "notes": "Capital District municipal agency seeded for intake associations.",
    },
    {
        "name": "Schenectady Police Department",
        "county": "Schenectady",
        "address": "531 Liberty St, Schenectady, NY 12305",
        "phone": "518-382-5200",
        "email": "info@schenectadypd.com",
        "agency_contact": "Operations Desk",
        "notes": "Capital District municipal agency seeded for intake associations.",
    },
    {
        "name": "Troy Police Department",
        "county": "Rensselaer",
        "address": "55 State St, Troy, NY 12180",
        "phone": "518-270-4421",
        "email": "police@troyny.gov",
        "agency_contact": "Front Desk",
        "notes": "Capital District municipal agency seeded for intake associations.",
    },
    {
        "name": "Rensselaer County Sheriffs Office",
        "county": "Rensselaer",
        "address": "4000 Main Street, Troy, NY 12180",
        "phone": "518-266-1900",
        "email": "sheriff@rensco.com",
        "agency_contact": "Investigations",
        "notes": "Primary county sheriff agency seeded for INVZEO case intake.",
    },
    {
        "name": "Saratoga Springs Police Department",
        "county": "Saratoga",
        "address": "5 Lake Ave, Saratoga Springs, NY 12866",
        "phone": "518-584-1800",
        "email": "sspdtips@saratoga-springs.org",
        "agency_contact": "Shift Commander",
        "notes": "Capital District municipal agency seeded for intake associations.",
    },
    {
        "name": "Albany County Sheriff",
        "county": "Albany",
        "address": "16 Eagle St, Albany, NY 12207",
        "phone": "518-487-5440",
        "email": "sheriff@albanycountyny.gov",
        "agency_contact": "Records Division",
        "notes": "County law enforcement agency seeded for intake associations.",
    },
]


def _default_admin_password() -> str:
    password = os.getenv("DEFAULT_ADMIN_PASSWORD", "").strip()
    if password:
        return password
    return "Google1595!"


def _enabled(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def seed_default_admin() -> None:
    password = _default_admin_password()
    if not password:
        return

    email = os.getenv("DEFAULT_ADMIN_EMAIL", "kzeoli@invzeo.local").strip().lower()
    username = os.getenv("DEFAULT_ADMIN_USERNAME", "kzeoli").strip().lower()
    full_name = os.getenv("DEFAULT_ADMIN_FULL_NAME", "K Zeoli").strip()
    department_name = os.getenv("DEFAULT_ADMIN_DEPARTMENT", "Rensselaer County Sheriffs Office").strip()

    existing = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing:
        changed = False
        if existing.role != Role.ADMIN.value:
            existing.role = Role.ADMIN.value
            changed = True
        if not existing.is_active_user:
            existing.is_active_user = True
            changed = True
        if _enabled(os.getenv("DEFAULT_ADMIN_RESET_PASSWORD", "true")):
            existing.set_password(password)
            changed = True
        if changed:
            db.session.commit()
        return

    department = Department.query.filter_by(name=department_name).first()
    admin = User(
        full_name=full_name,
        username=username,
        email=email,
        role=Role.ADMIN.value,
        department_id=department.id if department else None,
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()


def seed_reference_data() -> None:
    for department_data in DEFAULT_DEPARTMENTS:
        db.session.execute(
            insert(Department.__table__)
            .values(**department_data)
            .on_conflict_do_nothing(index_elements=["name"])
        )

    for source_data in DEFAULT_PUBLIC_SOURCES:
        db.session.execute(
            insert(PublicDataSource.__table__)
            .values(**source_data)
            .on_conflict_do_nothing(index_elements=["name"])
        )

    db.session.commit()
    seed_default_admin()
