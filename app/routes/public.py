from flask import Blueprint, render_template, request
from flask_login import login_required

from app.models import PublicDataSource
from app.services.public_data import search_public_sources


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