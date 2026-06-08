from flask import Blueprint, current_app, render_template, send_file
from flask_login import current_user, login_required

from app.models import Report, Role
from app.services.security import can_access_case, log_audit


reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.get("")
@login_required
def list_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    if current_user.role == Role.INFORMANT.value:
        reports = [report for report in reports if report.case.owner_id == current_user.id]
    return render_template("reports/list.html", reports=reports)


@reports_bp.get("/<int:report_id>")
@login_required
def report_detail(report_id: int):
    report = Report.query.get_or_404(report_id)
    if not can_access_case(current_user, report.case):
        return render_template("errors/403.html"), 403
    return render_template("reports/detail.html", report=report)


@reports_bp.get("/<int:report_id>/download")
@login_required
def download_report(report_id: int):
    report = Report.query.get_or_404(report_id)
    if not can_access_case(current_user, report.case):
        return render_template("errors/403.html"), 403
    log_audit("report_downloaded", user=current_user, case=report.case, details=report.title)
    return send_file(report.export_path, as_attachment=True, download_name=f"{report.case.case_number}.pdf")


@reports_bp.get("/<int:report_id>/print")
@login_required
def print_report(report_id: int):
    report = Report.query.get_or_404(report_id)
    if not can_access_case(current_user, report.case):
        return render_template("errors/403.html"), 403
    return render_template("reports/print.html", report=report)