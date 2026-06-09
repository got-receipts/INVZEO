from flask import Blueprint, current_app, jsonify, redirect, render_template, send_from_directory, url_for
from flask_login import current_user, login_required
from sqlalchemy import text

from app.extensions import db
from app.models import Case, Message, Report, Role, User

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
@login_required
def dashboard():
    if User.query.count() == 0:
        return redirect(url_for("auth.bootstrap_admin"))

    case_query = Case.query
    if current_user.role == Role.INFORMANT.value:
        case_query = case_query.filter_by(owner_id=current_user.id)

    recent_cases = case_query.order_by(Case.updated_at.desc()).limit(4).all()
    report_query = Report.query.join(Case)
    if current_user.role == Role.INFORMANT.value:
        report_query = report_query.filter(Case.owner_id == current_user.id)
    unread_count = Message.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    stats = [
        {"label": "Open", "value": case_query.filter(Case.status != "Closed").count()},
        {"label": "Critical", "value": case_query.filter_by(priority="Critical").count()},
        {"label": "Reports", "value": report_query.count()},
        {"label": "Unread", "value": unread_count},
    ]
    dashboard_cards = [
        {"title": "New Case", "endpoint": url_for("cases.new_case"), "icon": "plus"},
        {"title": "Cases", "endpoint": url_for("cases.list_cases"), "icon": "folder"},
        {"title": "Agencies", "endpoint": url_for("departments.list_departments"), "icon": "shield"},
        {"title": "Reports", "endpoint": url_for("reports.list_reports"), "icon": "doc"},
        {"title": "Public Data", "endpoint": url_for("public.data_sources"), "icon": "globe"},
        {"title": "Source Search", "endpoint": url_for("public.records_search"), "icon": "search"},
        {"title": "Vehicle Search", "endpoint": url_for("public.vehicle_search"), "icon": "car"},
        {"title": "Provider Search", "endpoint": url_for("public.authorized_records"), "icon": "database"},
        {"title": "Messages", "endpoint": url_for("messages.inbox"), "icon": "chat"},
        {"title": "Settings", "endpoint": url_for("settings.index"), "icon": "gear"},
    ]
    return render_template(
        "dashboard.html",
        dashboard_cards=dashboard_cards,
        recent_cases=recent_cases,
        role=Role,
        stats=stats,
        unread_count=unread_count,
        user=current_user,
    )


@main_bp.get("/health")
def health_check():
    db.session.execute(text("SELECT 1"))
    return jsonify({"database": "ok", "status": "ok"})


@main_bp.get("/manifest.webmanifest")
def manifest():
    return send_from_directory(current_app.static_folder, "manifest.webmanifest")


@main_bp.get("/service-worker.js")
def service_worker():
    return send_from_directory(current_app.static_folder, "service-worker.js")


@main_bp.app_context_processor
def inject_roles():
    return {"Role": Role}
