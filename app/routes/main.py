from flask import Blueprint, current_app, jsonify, redirect, render_template, send_from_directory, url_for
from flask_login import current_user, login_required

from app.models import Role, User

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
@login_required
def dashboard():
    if User.query.count() == 0:
        return redirect(url_for("auth.bootstrap_admin"))

    dashboard_cards = [
        {"title": "Open New Case", "endpoint": url_for("cases.new_case"), "icon": "plus"},
        {"title": "My Cases", "endpoint": url_for("cases.list_cases"), "icon": "folder"},
        {"title": "Departments", "endpoint": url_for("departments.list_departments"), "icon": "shield"},
        {"title": "Reports", "endpoint": url_for("reports.list_reports"), "icon": "doc"},
        {"title": "Public Data", "endpoint": url_for("public.data_sources"), "icon": "globe"},
        {"title": "Public Records Search", "endpoint": url_for("public.records_search"), "icon": "search"},
        {"title": "Messages", "endpoint": url_for("messages.inbox"), "icon": "chat"},
        {"title": "Settings", "endpoint": url_for("settings.index"), "icon": "gear"},
    ]
    return render_template("dashboard.html", dashboard_cards=dashboard_cards, role=Role, user=current_user)


@main_bp.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@main_bp.get("/manifest.webmanifest")
def manifest():
    return send_from_directory(current_app.static_folder, "manifest.webmanifest")


@main_bp.get("/service-worker.js")
def service_worker():
    return send_from_directory(current_app.static_folder, "service-worker.js")


@main_bp.app_context_processor
def inject_roles():
    return {"Role": Role}