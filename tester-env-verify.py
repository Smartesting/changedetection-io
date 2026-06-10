#!/usr/bin/env python3
import json
import os
import urllib.error
import urllib.request


BASE_URL = os.environ.get("TESTER_ENV_URL", "http://127.0.0.1:5029").rstrip("/")
EXPECTED_TITLES = {"Northwind Coffee product pricing", "Northwind Coffee checkout banner", "Acme Wholesale availability feed", "Harbor Freight surcharge notice", "California privacy policy update", "Accessibility statement monitor"}
EXPECTED_TAGS = {"Retail Intelligence", "Vendor Portals", "Compliance"}
PAUSED_TITLES = {"Northwind Coffee checkout banner", "Accessibility statement monitor"}


def request_json(path, api_key=None):
    headers = {"x-api-key": api_key} if api_key else {}
    req = urllib.request.Request(BASE_URL + path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"GET {path} failed: {exc.code} {exc.read().decode('utf-8', 'replace')}")


def main():
    token = os.environ.get("TESTER_ENV_API_KEY")
    if not token:
        raise SystemExit("Missing TESTER_ENV_API_KEY")

    tags = request_json("/api/v1/tags", token)
    tag_titles = {tag["title"] for tag in tags.values()}
    if tag_titles != EXPECTED_TAGS:
        raise SystemExit(f"Unexpected tags: {sorted(tag_titles)}")

    watches = request_json("/api/v1/watch", token)
    titles = {watch["title"] for watch in watches.values()}
    if titles != EXPECTED_TITLES:
        raise SystemExit(f"Unexpected watches: {sorted(titles)}")

    paused = set()
    tag_use_count = {tag_uuid: 0 for tag_uuid in tags}
    for uuid in watches:
        detail = request_json(f"/api/v1/watch/{uuid}", token)
        if detail.get("paused"):
            paused.add(detail["title"])
        for tag_uuid in detail.get("tags", []):
            tag_use_count[tag_uuid] = tag_use_count.get(tag_uuid, 0) + 1

    if paused != PAUSED_TITLES:
        raise SystemExit(f"Unexpected paused watches: {sorted(paused)}")
    if sorted(tag_use_count.values()) != [2, 2, 2]:
        raise SystemExit(f"Expected two watches per tag, got {tag_use_count}")

    html = urllib.request.urlopen(BASE_URL + "/", timeout=10).read().decode("utf-8", "replace")
    for text in sorted(EXPECTED_TITLES | EXPECTED_TAGS):
        if text not in html:
            raise SystemExit(f"Dashboard HTML missing visible seed text: {text}")

    print("Seed verify passed: 6 watches, 3 tags, 2 paused, 2 watches per tag.")


if __name__ == "__main__":
    main()
