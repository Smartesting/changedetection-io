#!/usr/bin/env python3
import json
import os
import time
import urllib.error
import urllib.request


BASE_URL = os.environ.get("TESTER_ENV_URL", "http://127.0.0.1:5029").rstrip("/")

TAGS = ["Retail Intelligence", "Vendor Portals", "Compliance"]

WATCHES = [
    {"title": "Northwind Coffee product pricing", "url": "https://example.com/northwind-coffee-pricing", "tag": "Retail Intelligence", "paused": False, "time_between_check_use_default": False, "time_between_check": {"weeks": 0, "days": 0, "hours": 6, "minutes": 0, "seconds": 0}},
    {"title": "Northwind Coffee checkout banner", "url": "https://example.com/northwind-checkout-banner", "tag": "Retail Intelligence", "paused": True, "time_between_check_use_default": False, "time_between_check": {"weeks": 0, "days": 1, "hours": 0, "minutes": 0, "seconds": 0}},
    {"title": "Acme Wholesale availability feed", "url": "https://example.com/acme-wholesale-availability", "tag": "Vendor Portals", "paused": False, "time_between_check_use_default": False, "time_between_check": {"weeks": 0, "days": 0, "hours": 2, "minutes": 30, "seconds": 0}},
    {"title": "Harbor Freight surcharge notice", "url": "https://example.com/harbor-freight-surcharge", "tag": "Vendor Portals", "paused": False, "time_between_check_use_default": False, "time_between_check": {"weeks": 0, "days": 0, "hours": 12, "minutes": 0, "seconds": 0}},
    {"title": "California privacy policy update", "url": "https://example.com/california-privacy-policy", "tag": "Compliance", "paused": False, "time_between_check_use_default": False, "time_between_check": {"weeks": 1, "days": 0, "hours": 0, "minutes": 0, "seconds": 0}},
    {"title": "Accessibility statement monitor", "url": "https://example.com/accessibility-statement", "tag": "Compliance", "paused": True, "time_between_check_use_default": False, "time_between_check": {"weeks": 2, "days": 0, "hours": 0, "minutes": 0, "seconds": 0}},
]


def request_json(path, method="GET", payload=None, api_key=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"content-type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    req = urllib.request.Request(BASE_URL + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body and body[:1] in "[{" else body
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"{method} {path} failed: {exc.code} {exc.read().decode('utf-8', 'replace')}")


def wait_ready():
    for _ in range(60):
        try:
            urllib.request.urlopen(BASE_URL + "/", timeout=2).read()
            return
        except Exception:
            time.sleep(1)
    raise SystemExit(f"App not ready at {BASE_URL}")


def main():
    wait_ready()
    token = os.environ.get("TESTER_ENV_API_KEY")
    if not token:
        raise SystemExit("Missing TESTER_ENV_API_KEY")

    for uuid in list(request_json("/api/v1/watch", api_key=token).keys()):
        request_json(f"/api/v1/watch/{uuid}", method="DELETE", api_key=token)
    for uuid in list(request_json("/api/v1/tags", api_key=token).keys()):
        request_json(f"/api/v1/tag/{uuid}", method="DELETE", api_key=token)

    for title in TAGS:
        request_json("/api/v1/tag", method="POST", payload={"title": title}, api_key=token)

    for watch in WATCHES:
        payload = dict(watch)
        paused = payload.pop("paused")
        created = request_json("/api/v1/watch", method="POST", payload=payload, api_key=token)
        if paused:
            request_json(f"/api/v1/watch/{created['uuid']}?paused=paused", api_key=token)

    print("Seeded 3 tags and 6 watches for Northwind Digital Merchandising.")


if __name__ == "__main__":
    main()
