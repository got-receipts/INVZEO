from __future__ import annotations

from sqlalchemy.dialects.postgresql import insert

from app.extensions import db
from app.models import Department, PublicDataSource
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
