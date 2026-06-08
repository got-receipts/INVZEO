from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import CaseForm, CaseNoteForm, ReportForm
from app.models import Case, CaseNote, Department, Report, Role
from app.services.reporting import build_report_summary, generate_pdf
from app.services.security import (
    ensure_case_access,
    generate_case_number,
    load_decrypted_bytes,
    log_audit,
    record_case_activity,
    save_encrypted_upload,
)


cases_bp = Blueprint("cases", __name__, url_prefix="/cases")


def _visible_cases():
    query = Case.query.order_by(Case.created_at.desc())
    if current_user.role == Role.INFORMANT.value:
        query = query.filter_by(owner_id=current_user.id)
    return query


@cases_bp.get("")
@login_required
def list_cases():
    cases = _visible_cases().all()
    return render_template("cases/list.html", cases=cases)


@cases_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_case():
    form = CaseForm()
    departments = Department.query.order_by(Department.name.asc()).all()
    form.set_department_choices(departments)
    if request.method == "GET":
        form.user_name.data = current_user.full_name

    if form.validate_on_submit():
        case = Case(
            case_number=generate_case_number(),
            user_name=form.user_name.data,
            primary_department_id=form.primary_department_id.data,
            officer_contact=form.officer_contact.data,
            case_type=form.case_type.data,
            incident_location=form.incident_location.data,
            narrative=form.narrative.data,
            status=form.status.data,
            priority=form.priority.data,
            owner_id=current_user.id,
        )
        case.departments = [
            department for department in departments if department.id in set(form.department_ids.data)
        ]
        if case.primary_department not in case.departments:
            primary_department = next(
                department for department in departments if department.id == form.primary_department_id.data
            )
            case.departments.append(primary_department)

        db.session.add(case)
        db.session.flush()
        record_case_activity(case, "Case opened", details="Initial intake submitted")

        for upload in request.files.getlist("attachments"):
            attachment = save_encrypted_upload(upload, case)
            if attachment:
                db.session.add(attachment)

        db.session.commit()
        log_audit("case_created", user=current_user, case=case, details=f"Created {case.case_number}")
        flash(f"Case {case.case_number} opened.", "success")
        return redirect(url_for("cases.case_detail", case_id=case.id))

    return render_template("cases/new.html", form=form)


@cases_bp.route("/<int:case_id>", methods=["GET", "POST"])
@login_required
def case_detail(case_id: int):
    case = Case.query.get_or_404(case_id)
    ensure_case_access(case)
    note_form = CaseNoteForm()
    report_form = ReportForm()

    if note_form.validate_on_submit():
        note = CaseNote(case=case, author=current_user, body=note_form.body.data)
        db.session.add(note)
        record_case_activity(case, "Note added", details=note.body)
        db.session.commit()
        log_audit("case_note_added", user=current_user, case=case, details="Case note added")
        flash("Note added.", "success")
        return redirect(url_for("cases.case_detail", case_id=case.id))

    log_audit("case_viewed", user=current_user, case=case, details=f"Viewed {case.case_number}")
    return render_template(
        "cases/detail.html",
        case=case,
        note_form=note_form,
        report_form=report_form,
    )


@cases_bp.post("/<int:case_id>/attachments")
@login_required
def upload_attachment(case_id: int):
    case = Case.query.get_or_404(case_id)
    ensure_case_access(case)

    added = 0
    for upload in request.files.getlist("attachments"):
        attachment = save_encrypted_upload(upload, case)
        if attachment:
            db.session.add(attachment)
            added += 1

    if added:
        record_case_activity(case, "Attachment uploaded", details=f"{added} file(s) uploaded")
        db.session.commit()
        log_audit("attachment_uploaded", user=current_user, case=case, details=f"Uploaded {added} file(s)")
        flash(f"Uploaded {added} file(s).", "success")
    else:
        flash("No valid attachments were uploaded.", "warning")
    return redirect(url_for("cases.case_detail", case_id=case.id))


@cases_bp.get("/<int:case_id>/attachments/<int:attachment_id>/download")
@login_required
def download_attachment(case_id: int, attachment_id: int):
    case = Case.query.get_or_404(case_id)
    ensure_case_access(case)
    attachment = next((item for item in case.attachments if item.id == attachment_id), None)
    if attachment is None:
        return redirect(url_for("cases.case_detail", case_id=case.id))

    log_audit("attachment_downloaded", user=current_user, case=case, details=attachment.original_filename)
    return send_file(
        load_decrypted_bytes(attachment),
        as_attachment=True,
        download_name=attachment.original_filename,
        mimetype=attachment.mime_type,
    )


@cases_bp.post("/<int:case_id>/reports")
@login_required
def generate_case_report(case_id: int):
    case = Case.query.get_or_404(case_id)
    ensure_case_access(case)
    form = ReportForm()
    if not form.validate_on_submit():
        flash("Report title is required.", "danger")
        return redirect(url_for("cases.case_detail", case_id=case.id))

    report_record = Report(
        case=case,
        author=current_user,
        title=form.title.data,
        summary=form.summary.data or build_report_summary(case),
    )
    db.session.add(report_record)
    db.session.flush()
    report_record.export_path = generate_pdf(case, report_record, current_app.config["EXPORT_FOLDER"])
    record_case_activity(case, "Report generated", details=report_record.title)
    db.session.commit()
    log_audit("report_generated", user=current_user, case=case, details=report_record.title)
    flash("Report generated.", "success")
    return redirect(url_for("reports.report_detail", report_id=report_record.id))