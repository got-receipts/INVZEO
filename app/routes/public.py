from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app.models import PublicDataSource
from app.services.authorized_sources import PROVIDERS, run_authorized_search
from app.services.public_data import search_public_sources
from app.services.security import log_audit
from app.services.vehicle_lookup import run_vehicle_search


public_bp = Blueprint("public", __name__)


@public_bp.get("/public-data")
@login_required
def data_sources():
    sources = PublicDataSource.query.order_by(PublicDataSource.record_type.asc(), PublicDataSource.name.asc()).all()
    return render_template("public/data.html", sources=sources)


@public_bp.get("/public-records")
@login_required
def records_search():
    filters = {
        "name": request.args.get("name", "").strip(),
        "address": request.args.get("address", "").strip(),
        "county": request.args.get("county", "").strip(),
        "agency": request.args.get("agency", "").strip(),
        "case_reference": request.args.get("case_reference", "").strip(),
        "record_type": request.args.get("record_type", "").strip(),
    }
    results = search_public_sources(filters) if any(filters.values()) else []
    return render_template("public/search.html", filters=filters, results=results)


@public_bp.route("/vehicle-search", methods=["GET", "POST"])
@login_required
def vehicle_search():
    source = request.form if request.method == "POST" else request.args
    filters = {
        "plate": source.get("plate", "").strip(),
        "state": source.get("state", "NY").strip() or "NY",
        "vin": source.get("vin", "").strip(),
    }
    results = None
    should_search = request.method == "POST" or request.args.get("run") == "1"
    if should_search and (filters["plate"] or filters["vin"]):
        results = run_vehicle_search(filters["plate"], filters["state"], filters["vin"])
        log_audit(
            "vehicle_search",
            user=current_user,
            details=f"Plate={filters['plate']} State={filters['state']} VIN={filters['vin']}",
        )
    return render_template("public/vehicle.html", filters=filters, results=results)


@public_bp.route("/authorized-records", methods=["GET", "POST"])
@login_required
def authorized_records():
    source = request.form if request.method == "POST" else request.args
    filters = {
        "provider": source.get("provider", "mobilepatrol").strip(),
        "name": source.get("name", "").strip(),
        "dob": source.get("dob", "").strip(),
        "county": source.get("county", "").strip(),
        "state": source.get("state", "NY").strip() or "NY",
        "case_reference": source.get("case_reference", "").strip(),
        "record_type": source.get("record_type", "").strip(),
    }
    provider_id = filters["provider"] if filters["provider"] in PROVIDERS else "mobilepatrol"
    filters["provider"] = provider_id
    results = None
    query_filters = {key: value for key, value in filters.items() if key != "provider"}
    should_search = request.method == "POST" or request.args.get("run") == "1"
    if should_search and any(query_filters.values()):
        results = run_authorized_search(provider_id, query_filters)
        log_audit(
            "authorized_records_search",
            user=current_user,
            details=f"Provider={provider_id}; Query={query_filters}",
        )
    return render_template(
        "public/authorized.html",
        filters=filters,
        providers=PROVIDERS,
        results=results,
    )
