from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.models import Case, Report


def build_report_summary(case: Case) -> str:
    department_names = ", ".join(department.name for department in case.departments) or case.primary_department.name
    timeline = " | ".join(
        f"{activity.created_at.strftime('%Y-%m-%d %H:%M')} {activity.action}"
        for activity in sorted(case.activities, key=lambda item: item.created_at)
    ) or "No activity recorded."
    notes = "\n".join(f"- {note.body}" for note in case.notes[-5:]) or "No notes recorded."
    return (
        f"Case {case.case_number} for {case.user_name}. "
        f"Type: {case.case_type}. Status: {case.status}. Priority: {case.priority}. "
        f"Primary department: {case.primary_department.name}. Associated departments: {department_names}.\n\n"
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
    text.textLine(f"Case Number: {case.case_number}")
    text.textLine(f"Created: {case.created_at.strftime('%Y-%m-%d %H:%M UTC')}")
    text.textLine(f"User: {case.user_name}")
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