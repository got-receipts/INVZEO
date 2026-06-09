from __future__ import annotations

from sqlalchemy import text

from app.extensions import db


CASE_COLUMN_UPDATES = (
    (
        "case_caption",
        "VARCHAR(160) NOT NULL DEFAULT 'The People Of The State Of NY'",
    ),
    ("subject_full_name", "VARCHAR(120) NOT NULL DEFAULT 'N/A'"),
    ("subject_aliases", "VARCHAR(255) NOT NULL DEFAULT 'N/A'"),
    ("subject_dob", "VARCHAR(40) NOT NULL DEFAULT 'N/A'"),
    ("subject_age", "VARCHAR(40) NOT NULL DEFAULT 'N/A'"),
    ("subject_sex", "VARCHAR(80) NOT NULL DEFAULT 'N/A'"),
    ("subject_race", "VARCHAR(80) NOT NULL DEFAULT 'N/A'"),
    ("subject_ethnicity", "VARCHAR(80) NOT NULL DEFAULT 'N/A'"),
    ("subject_height", "VARCHAR(40) NOT NULL DEFAULT 'N/A'"),
    ("subject_weight", "VARCHAR(40) NOT NULL DEFAULT 'N/A'"),
    ("subject_hair_color", "VARCHAR(80) NOT NULL DEFAULT 'N/A'"),
    ("subject_eye_color", "VARCHAR(80) NOT NULL DEFAULT 'N/A'"),
    ("subject_address", "VARCHAR(255) NOT NULL DEFAULT 'N/A'"),
    ("subject_phone", "VARCHAR(80) NOT NULL DEFAULT 'N/A'"),
    ("subject_email", "VARCHAR(255) NOT NULL DEFAULT 'N/A'"),
    ("subject_license_number", "VARCHAR(120) NOT NULL DEFAULT 'N/A'"),
    ("subject_license_state", "VARCHAR(40) NOT NULL DEFAULT 'N/A'"),
    ("vehicle_plate", "VARCHAR(40) NOT NULL DEFAULT 'N/A'"),
    ("vehicle_state", "VARCHAR(40) NOT NULL DEFAULT 'NY'"),
    ("vehicle_vin", "VARCHAR(80) NOT NULL DEFAULT 'N/A'"),
    ("subject_notes", "TEXT NOT NULL DEFAULT 'N/A'"),
)


def apply_schema_updates() -> None:
    for column_name, column_definition in CASE_COLUMN_UPDATES:
        db.session.execute(
            text(f"ALTER TABLE cases ADD COLUMN IF NOT EXISTS {column_name} {column_definition}")
        )
    db.session.commit()
