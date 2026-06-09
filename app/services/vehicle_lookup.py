from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


NHTSA_DECODE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{vin}?format=json"


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _provider_request(url: str, api_key: str, payload: dict[str, str]) -> dict:
    delimiter = "&" if "?" in url else "?"
    request_url = f"{url}{delimiter}{urlencode(payload)}"
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = Request(request_url, headers=headers)
    with urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def decode_vin(vin: str) -> dict:
    clean_vin = _clean(vin).upper()
    if not clean_vin or clean_vin == "N/A":
        return {"status": "not_requested", "message": "Enter a VIN to decode public vehicle data."}

    try:
        request_url = NHTSA_DECODE_URL.format(vin=quote(clean_vin))
        with urlopen(request_url, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"status": "error", "message": f"VIN decode failed: {exc}"}

    result = (payload.get("Results") or [{}])[0]
    return {
        "status": "ok",
        "vin": clean_vin,
        "year": result.get("ModelYear") or "N/A",
        "make": result.get("Make") or "N/A",
        "model": result.get("Model") or "N/A",
        "trim": result.get("Trim") or "N/A",
        "body_class": result.get("BodyClass") or "N/A",
        "vehicle_type": result.get("VehicleType") or "N/A",
        "manufacturer": result.get("Manufacturer") or "N/A",
    }


def lookup_plate(plate: str, state: str) -> dict:
    clean_plate = _clean(plate).upper()
    clean_state = (_clean(state) or "NY").upper()
    if not clean_plate or clean_plate == "N/A":
        return {"status": "not_requested", "message": "Enter a plate to run an authorized plate lookup."}

    provider_url = os.getenv("PLATE_LOOKUP_API_URL", "").strip()
    provider_key = os.getenv("PLATE_LOOKUP_API_KEY", "").strip()
    if not provider_url:
        return {
            "status": "not_configured",
            "message": "Plate-to-VIN provider is not configured. Add PLATE_LOOKUP_API_URL and PLATE_LOOKUP_API_KEY for an authorized provider.",
            "plate": clean_plate,
            "state": clean_state,
        }

    try:
        provider_payload = _provider_request(
            provider_url,
            provider_key,
            {"plate": clean_plate, "state": clean_state},
        )
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"status": "error", "message": f"Authorized plate provider failed: {exc}"}

    vin = (
        provider_payload.get("vin")
        or provider_payload.get("VIN")
        or provider_payload.get("vehicle", {}).get("vin")
        or "N/A"
    )
    return {
        "status": "ok",
        "plate": clean_plate,
        "state": clean_state,
        "vin": vin,
        "raw": provider_payload,
    }


def run_vehicle_search(plate: str, state: str, vin: str) -> dict:
    return {
        "plate": lookup_plate(plate, state),
        "vin": decode_vin(vin),
    }
