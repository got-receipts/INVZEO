from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.models import Case, Report


def _subject_demographics(case: Case) -> str:
    fields = [
        ("Name", case.subject_full_name),
        ("Aliases", case.subject_aliases),
        ("DOB", case.subject_dob),
        ("Age", case.subject_age),
        ("Sex/Gender", case.subject_sex),
        ("Race", case.subject_race),
        ("Ethnicity", case.subject_ethnicity),
        ("Height", case.subject_height),
        ("Weight", case.subject_weight),
        ("Hair", case.subject_hair_color),
        ("Eyes", case.subject_eye_color),
        ("Address", case.subject_address),
        ("Phone", case.subject_phone),
        ("Email", case.subject_email),
        ("Driver ID", case.subject_license_number),
        ("License State", case.subject_license_state),
        ("Plate", f"{case.vehicle_state} {case.vehicle_plate}"),
        ("VIN", case.vehicle_vin),
    ]
    return "\n".join(f"{label}: {value}" for label, value in fields)


def build_report_summary(case: Case) -> str:
    department_names = ", ".join(department.name for department in case.departments) or case.primary_department.name
    timeline = " | ".join(
        f"{activity.created_at.strftime('%Y-%m-%d %H:%M')} {activity.action}"
        for activity in sorted(case.activities, key=lambda item: item.created_at)
    ) or "No activity recorded."
    notes = "\n".join(f"- {note.body}" for note in case.notes[-5:]) or "No notes recorded."
    return (
        f"{case.case_caption}\n"
        f"Case {case.case_number} for {case.user_name}. "
        f"Type: {case.case_type}. Status: {case.status}. Priority: {case.priority}. "
        f"Primary department: {case.primary_department.name}. Associated departments: {department_names}.\n\n"
        f"Individual demographics:\n{_subject_demographics(case)}\n\n"
        f"Additional identifiers: {case.subject_notes}\n\n"
        f"Narrative: {case.narrative}\n\n"
        f"Timeline: {timeline}\n\n"
        f"Recent notes:\n{notes}"
    )


def generate_pdf(case: Case, report_record: Report, export_folder: str) -> str:
    output_dir = Path(export_folder)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{case.case_number}-{report_record.id}.pdf"

    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    text = pdf.beginText(40, 760)
    text.setLeading(16)
    text.textLine(report_record.title)
    text.textLine("")
    text.textLine(case.case_caption)
    text.textLine("")
    text.textLine(f"Case Number: {case.case_number}")
    text.textLine(f"Created: {case.created_at.strftime('%Y-%m-%d %H:%M UTC')}")
    text.textLine(f"User: {case.user_name}")
    text.textLine(f"Individual: {case.subject_full_name}")
    text.textLine(f"DOB/Age: {case.subject_dob} / {case.subject_age}")
    text.textLine(f"Vehicle: {case.vehicle_state} {case.vehicle_plate} / VIN {case.vehicle_vin}")
    text.textLine(f"Department: {case.primary_department.name}")
    text.textLine(f"Officer Contact: {case.officer_contact}")
    text.textLine(f"Status: {case.status} / Priority: {case.priority}")
    text.textLine("")

    for line in report_record.summary.splitlines():
        chunks = [line[index:index + 95] for index in range(0, len(line), 95)] or [""]
        for chunk in chunks:
            if text.getY() < 60:
                pdf.drawText(text)
                pdf.showPage()
                text = pdf.beginText(40, 760)
                text.setLeading(16)
            text.textLine(chunk)

    pdf.drawText(text)
    pdf.showPage()
    pdf.save()
    return str(output_path)
