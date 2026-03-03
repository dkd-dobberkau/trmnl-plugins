#!/usr/bin/env python3
"""
TRMNL Webhook: Haben die Bayern wieder verloren?

Holt das letzte Bundesliga-Ergebnis des FC Bayern München von OpenLigaDB
und pusht die aufbereiteten Daten an ein TRMNL Private Plugin (Webhook-Strategie).

Verwendung:
    python push-bayern.py

Umgebungsvariablen:
    TRMNL_PLUGIN_UUID  - Plugin Settings UUID aus der TRMNL Webhook-URL (Pflicht)
    BAYERN_TEAM_ID     - OpenLigaDB Team-ID (Standard: 40 = FC Bayern München)
    BAYERN_HISTORY     - Anzahl Historie-Einträge (Standard: 3)
"""

import json
import os
import sys
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

OPENLIGADB_URL = "https://api.openligadb.de/getmatchesbyteamid/{team_id}/6/0"
TRMNL_WEBHOOK_URL = "https://trmnl.com/api/custom_plugins/{uuid}"

BAYERN_TEAM_ID = int(os.environ.get("BAYERN_TEAM_ID", "40"))
HISTORY_COUNT = int(os.environ.get("BAYERN_HISTORY", "3"))


def fetch_matches(team_id: int) -> list:
    url = OPENLIGADB_URL.format(team_id=team_id)
    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def get_final_score(match: dict) -> dict | None:
    for result in match.get("matchResults", []):
        if result.get("resultTypeID") == 2:
            return result
    return None


def process_match(match: dict, team_id: int) -> dict | None:
    score = get_final_score(match)
    if not score:
        return None

    is_home = match["team1"]["teamId"] == team_id
    bayern_goals = score["pointsTeam1"] if is_home else score["pointsTeam2"]
    opponent_goals = score["pointsTeam2"] if is_home else score["pointsTeam1"]

    if bayern_goals > opponent_goals:
        outcome = "S"
        answer = "NEIN!"
    elif bayern_goals < opponent_goals:
        outcome = "N"
        answer = "JA!"
    else:
        outcome = "U"
        answer = "JEIN!"

    match_date = datetime.fromisoformat(match["matchDateTime"])

    return {
        "answer": answer,
        "outcome": outcome,
        "score": f"{match['team1']['shortName']} {score['pointsTeam1']}:{score['pointsTeam2']} {match['team2']['shortName']}",
        "matchday": match["group"]["groupOrderID"],
        "matchday_name": match["group"]["groupName"],
        "date": match_date.strftime("%d.%m.%Y"),
        "league": match.get("leagueShortcut", ""),
    }


def build_merge_variables(matches: list, team_id: int, history_count: int) -> dict:
    # Filter: beendete Bundesliga-Spiele, neueste zuerst
    bl_matches = [
        m for m in reversed(matches)
        if m.get("matchIsFinished") and m.get("leagueShortcut") == "bl1"
    ]

    if not bl_matches:
        return {"answer": "?", "score": "Keine Ergebnisse", "history": []}

    latest = process_match(bl_matches[0], team_id)
    if not latest:
        return {"answer": "?", "score": "Ergebnis nicht verfügbar", "history": []}

    history = []
    for match in bl_matches[1 : 1 + history_count]:
        entry = process_match(match, team_id)
        if entry:
            history.append({
                "matchday": entry["matchday"],
                "score": entry["score"],
                "outcome": entry["outcome"],
            })

    return {
        "answer": latest["answer"],
        "score": latest["score"],
        "matchday_name": latest["matchday_name"],
        "date": latest["date"],
        "history": history,
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
        print("Fehler: TRMNL_PLUGIN_UUID Umgebungsvariable nicht gesetzt.", file=sys.stderr)
        print("Setze die UUID aus deiner TRMNL Plugin Webhook-URL:", file=sys.stderr)
        print("  export TRMNL_PLUGIN_UUID=dein-uuid-hier", file=sys.stderr)
        sys.exit(1)

    try:
        matches = fetch_matches(BAYERN_TEAM_ID)
    except (URLError, json.JSONDecodeError) as e:
        print(f"Fehler beim Abrufen der OpenLigaDB Daten: {e}", file=sys.stderr)
        sys.exit(1)

    merge_variables = build_merge_variables(matches, BAYERN_TEAM_ID, HISTORY_COUNT)
    print(f"Ergebnis: {merge_variables['answer']} – {merge_variables['score']}")

    push_to_trmnl(uuid, merge_variables)


if __name__ == "__main__":
    main()
