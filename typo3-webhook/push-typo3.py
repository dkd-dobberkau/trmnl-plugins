#!/usr/bin/env python3
"""
TRMNL Webhook: TYPO3 Release Dashboard

Holt aktuelle TYPO3-Versionsdaten von get.typo3.org und pusht
aufbereitete Daten an ein TRMNL Private Plugin (Webhook-Strategie).

Verwendung:
    python push-typo3.py

Umgebungsvariablen:
    TRMNL_PLUGIN_UUID  - Plugin Settings UUID aus der TRMNL Webhook-URL (Pflicht)
    TYPO3_MIN_VERSION  - Kleinste Major-Version die angezeigt wird (Standard: 10)
"""

import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError

API_BASE = "https://get.typo3.org/api/v1"
TRMNL_WEBHOOK_URL = "https://trmnl.com/api/custom_plugins/{uuid}"

MIN_VERSION = int(os.environ.get("TYPO3_MIN_VERSION", "10"))


def api_get(path: str) -> dict | list | None:
    url = f"{API_BASE}{path}"
    req = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except (URLError, json.JSONDecodeError) as e:
        print(f"  Warnung: {url} – {e}", file=sys.stderr)
        return None


def format_date(iso_str: str | None) -> str:
    if not iso_str:
        return "–"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d.%m.%Y")
    except ValueError:
        return "–"


def format_month_year(iso_str: str | None) -> str:
    if not iso_str:
        return "–"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%m/%Y")
    except ValueError:
        return "–"


def is_maintained(iso_str: str | None) -> bool:
    if not iso_str:
        return False
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt > datetime.now(dt.tzinfo)
    except ValueError:
        return False


def get_php_range(major_version: int) -> str:
    data = api_get(f"/major/{major_version}/requirements")
    if not data:
        return "–"
    for req in data:
        if req.get("category") == "php" and req.get("name") == "php":
            min_v = req.get("min", "?")
            max_v = req.get("max", "?")
            # Shorten: 8.2.0 -> 8.2, 8.5.99 -> 8.5
            min_short = ".".join(min_v.split(".")[:2])
            max_short = ".".join(max_v.split(".")[:2])
            return f"{min_short}–{max_short}"
    return "–"


def build_version_data(major: dict) -> dict:
    ver = int(major["version"])
    title = major.get("title", f"TYPO3 {ver}")

    # Determine status
    maintained = is_maintained(major.get("maintained_until"))
    elts_active = is_maintained(major.get("elts_until"))

    if maintained:
        status = "Active"
    elif elts_active:
        status = "ELTS"
    else:
        status = "EOL"

    entry = {
        "version": ver,
        "title": title,
        "status": status,
        "maintained_until": format_month_year(major.get("maintained_until")),
        "elts_until": format_month_year(major.get("elts_until")),
        "latest": "–",
        "latest_date": "–",
        "latest_type": "–",
        "security": "–",
        "security_date": "–",
        "php": "–",
    }

    # Fetch latest release
    latest = api_get(f"/major/{ver}/release/latest")
    if latest:
        entry["latest"] = latest.get("version", "–")
        entry["latest_date"] = format_date(latest.get("date"))
        entry["latest_type"] = latest.get("type", "–")

    # Fetch latest security release
    security = api_get(f"/major/{ver}/release/latest/security")
    if security:
        entry["security"] = security.get("version", "–")
        entry["security_date"] = format_date(security.get("date"))

    # Fetch PHP requirements
    entry["php"] = get_php_range(ver)

    return entry


def build_merge_variables() -> dict:
    majors = api_get("/major/")
    if not majors:
        return {"versions": [], "updated": "–"}

    # Filter and sort: newest first, only >= MIN_VERSION
    relevant = [m for m in majors if int(m.get("version", 0)) >= MIN_VERSION]
    relevant.sort(key=lambda m: m["version"], reverse=True)

    versions = []
    for major in relevant:
        print(f"  Verarbeite {major.get('title', '?')}...")
        versions.append(build_version_data(major))

    return {
        "versions": versions,
        "updated": datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC"),
    }


def push_to_trmnl(uuid: str, merge_variables: dict) -> None:
    url = TRMNL_WEBHOOK_URL.format(uuid=uuid)
    payload = json.dumps({"merge_variables": merge_variables}).encode()
    req = Request(url, data=payload, method="POST", headers={
        "Content-Type": "application/json",
    })
    with urlopen(req, timeout=10) as resp:
        status = resp.status
        body = resp.read().decode()

    if status >= 400:
        print(f"TRMNL API Fehler: {status} – {body}", file=sys.stderr)
        sys.exit(1)

    print(f"OK – Daten an TRMNL gepusht ({status})")


def main():
    uuid = os.environ.get("TRMNL_PLUGIN_UUID")
    if not uuid:
        print("Fehler: TRMNL_PLUGIN_UUID nicht gesetzt.", file=sys.stderr)
        print("  export TRMNL_PLUGIN_UUID=dein-uuid-hier", file=sys.stderr)
        sys.exit(1)

    print("Hole TYPO3-Versionsdaten...")
    merge_variables = build_merge_variables()

    for v in merge_variables.get("versions", []):
        print(f"  {v['title']}: {v['latest']} ({v['status']})")

    push_to_trmnl(uuid, merge_variables)


if __name__ == "__main__":
    main()
