from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROVIDERS = {
    "mobilepatrol": {
        "label": "MobilePatrol",
        "endpoint_env": "MOBILEPATROL_API_URL",
        "key_env": "MOBILEPATROL_API_KEY",
        "official_url": "https://www.mobilepatrol.com/",
    },
    "lexisnexis": {
        "label": "LexisNexis",
        "endpoint_env": "LEXISNEXIS_API_URL",
        "key_env": "LEXISNEXIS_API_KEY",
        "official_url": "https://risk.lexisnexis.com/",
    },
}


def _clean_filters(filters: dict[str, str]) -> dict[str, str]:
    return {
        key: value.strip()
        for key, value in filters.items()
        if value and value.strip()
    }


def run_authorized_search(provider_id: str, filters: dict[str, str]) -> dict:
    provider = PROVIDERS.get(provider_id)
    if provider is None:
        return {"status": "error", "message": "Unknown provider selected."}

    endpoint = os.getenv(provider["endpoint_env"], "").strip()
    api_key = os.getenv(provider["key_env"], "").strip()
    clean_filters = _clean_filters(filters)

    if not endpoint:
        return {
            "status": "not_configured",
            "message": (
                f"{provider['label']} API access is not configured. Add "
                f"{provider['endpoint_env']} and {provider['key_env']} for an authorized account."
            ),
            "official_url": provider["official_url"],
            "provider": provider,
        }

    delimiter = "&" if "?" in endpoint else "?"
    request_url = f"{endpoint}{delimiter}{urlencode(clean_filters)}"
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        request = Request(request_url, headers=headers)
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"status": "error", "message": f"{provider['label']} search failed: {exc}"}

    return {
        "status": "ok",
        "provider": provider,
        "query": clean_filters,
        "raw": payload,
    }
