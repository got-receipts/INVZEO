from __future__ import annotations

from sqlalchemy import or_

from app.models import PublicDataSource


DEFAULT_PUBLIC_SOURCES = [
    {
        "name": "CDC Overdose Data to Action",
        "source_url": "https://www.cdc.gov/overdose-prevention/php/data-research/index.html",
        "search_url": "https://data.cdc.gov/",
        "record_type": "Overdose Data",
        "county": "National",
        "agency": "Centers for Disease Control and Prevention",
        "notes": "Official CDC open data and program references for overdose surveillance.",
        "requires_auth": False,
        "requires_payment": False,
    },
    {
        "name": "New York State Open Data",
        "source_url": "https://data.ny.gov/",
        "search_url": "https://data.ny.gov/",
        "record_type": "Open Data Portal",
        "county": "New York",
        "agency": "New York State",
        "notes": "Official New York open data portal with public health, safety, and community datasets.",
        "requires_auth": False,
        "requires_payment": False,
    },
    {
        "name": "Albany County GIS Public Viewer",
        "source_url": "https://albanyny.mapgeo.io/",
        "search_url": "https://albanyny.mapgeo.io/",
        "record_type": "Property Records",
        "county": "Albany",
        "agency": "Albany County",
        "notes": "Official county property viewer. Search is performed on the public county site.",
        "requires_auth": False,
        "requires_payment": False,
    },
    {
        "name": "Rensselaer County Public Records",
        "source_url": "https://rensco.com/",
        "search_url": "https://rensco.com/",
        "record_type": "County Records",
        "county": "Rensselaer",
        "agency": "Rensselaer County",
        "notes": "Official county portal for publicly accessible services and records references.",
        "requires_auth": False,
        "requires_payment": False,
    },
    {
        "name": "New York State eCourts",
        "source_url": "https://iapps.courts.state.ny.us/webcivil/ecourtsMain",
        "search_url": "https://iapps.courts.state.ny.us/webcivil/ecourtsMain",
        "record_type": "Court Records",
        "county": "New York",
        "agency": "New York State Unified Court System",
        "notes": "Official court search. If the portal presents CAPTCHA or manual verification, users must complete it on the official site.",
        "requires_auth": False,
        "requires_payment": False,
    },
    {
        "name": "New York DMV Records Requests",
        "source_url": "https://dmv.ny.gov/records",
        "search_url": "https://dmv.ny.gov/records",
        "record_type": "Vehicle Records",
        "county": "New York",
        "agency": "New York State DMV",
        "notes": "Official DMV portal. Identity verification, payment, or authorization may be required by the agency.",
        "requires_auth": True,
        "requires_payment": True,
    },
    {
        "name": "NHTSA VIN Decoder",
        "source_url": "https://vpic.nhtsa.dot.gov/",
        "search_url": "https://vpic.nhtsa.dot.gov/decoder/",
        "record_type": "Vehicle Records",
        "county": "National",
        "agency": "National Highway Traffic Safety Administration",
        "notes": "Official public VIN decoding source for make, model, year, manufacturer, and vehicle attributes.",
        "requires_auth": False,
        "requires_payment": False,
    },
    {
        "name": "MobilePatrol",
        "source_url": "https://www.mobilepatrol.com/",
        "search_url": "https://www.mobilepatrol.com/",
        "record_type": "Arrest and Booking Records",
        "county": "Authorized Coverage",
        "agency": "MobilePatrol",
        "notes": "Vendor platform for participating public safety agencies. Use official or contracted access only.",
        "requires_auth": True,
        "requires_payment": False,
    },
    {
        "name": "LexisNexis Risk Solutions",
        "source_url": "https://risk.lexisnexis.com/",
        "search_url": "https://risk.lexisnexis.com/",
        "record_type": "Public Records",
        "county": "National",
        "agency": "LexisNexis Risk Solutions",
        "notes": "Commercial public-records platform. Searches require authorized account access and applicable permissible purpose.",
        "requires_auth": True,
        "requires_payment": True,
    },
]


def search_public_sources(filters: dict[str, str]):
    query = PublicDataSource.query.order_by(PublicDataSource.name.asc())
    name = filters.get("name")
    county = filters.get("county")
    agency = filters.get("agency")
    record_type = filters.get("record_type")
    case_reference = filters.get("case_reference")
    address = filters.get("address")

    if name:
        query = query.filter(PublicDataSource.name.ilike(f"%{name}%"))
    if county:
        query = query.filter(PublicDataSource.county.ilike(f"%{county}%"))
    if agency:
        query = query.filter(PublicDataSource.agency.ilike(f"%{agency}%"))
    if record_type:
        query = query.filter(PublicDataSource.record_type.ilike(f"%{record_type}%"))
    if case_reference or address:
        search_term = case_reference or address
        query = query.filter(
            or_(
                PublicDataSource.notes.ilike(f"%{search_term}%"),
                PublicDataSource.name.ilike(f"%{search_term}%"),
            )
        )

    return query.all()
