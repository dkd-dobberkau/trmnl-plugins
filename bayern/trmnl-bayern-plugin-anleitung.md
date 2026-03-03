# TRMNL Private Plugin: Haben die Bayern wieder verloren?

## Übersicht

Dieses Plugin zeigt das letzte Bundesliga-Ergebnis des FC Bayern München auf dem TRMNL E-Ink Display an. Groß und deutlich: **JA** (Niederlage), **NEIN** (Sieg) oder **JEIN** (Unentschieden). Dazu die letzten 3 Spiele als kompakte Historie.

Datenquelle: [OpenLigaDB](https://www.openligadb.de) – kostenlos, ohne Authentifizierung.

---

## Voraussetzungen

- TRMNL-Gerät mit Developer Edition oder Developer Add-on
- Internetzugang (OpenLigaDB API ist öffentlich, keine API-Keys nötig)

---

## Schritt 1: Private Plugin anlegen

1. Gehe in deinem TRMNL-Account auf **Plugins** → suche nach **"Private Plugin"**
2. Vergib einen Namen, z.B. `Haben die Bayern verloren?`
3. Wähle als **Strategy**: `Polling`

---

## Schritt 2: Polling konfigurieren

### Polling URL

```
https://api.openligadb.de/getmatchesbyteamid/40/6/0
```

**URL-Parameter im Detail:**

| Parameter | Wert | Beschreibung |
|-----------|------|-------------|
| `40` | Team-ID | FC Bayern München |
| `6` | Vergangene Spiele | Letzte 6 Spiele (alle Wettbewerbe) |
| `0` | Zukünftige Spiele | Keine zukünftigen Spiele laden |

### Polling Verb

```
GET
```

### Polling Headers

Leer lassen – OpenLigaDB benötigt keine Authentifizierung.

### Polling Body

Leer lassen (nicht benötigt bei GET).

---

## Schritt 3: Markup einfügen

Klicke auf **"Edit Markup"** und füge den Inhalt der Datei `bayern-trmnl-markup.html` ein.

Das Liquid-Template:
- Iteriert die API-Antwort rückwärts (neuestes Spiel zuerst)
- Filtert nur beendete Bundesliga-Spiele (`leagueShortcut == "bl1"`)
- Bestimmt ob Bayern Heim- oder Auswärtsmannschaft war
- Zeigt das Endergebnis (`resultTypeID == 2`)
- Berechnet Sieg/Niederlage/Unentschieden

---

## Schritt 4: Testen

1. Klicke auf **Save** in den Plugin-Einstellungen
2. Klicke auf **"Force Refresh"** um sofort einen neuen Screen zu generieren
3. Prüfe die Vorschau im TRMNL-Interface unter Plugins → dein Private Plugin
4. Beim nächsten Refresh-Zyklus erscheint die Anzeige auf deinem TRMNL-Gerät

---

## OpenLigaDB API – Antwortformat

Die API liefert ein JSON-Array mit Spielobjekten:

```json
[
  {
    "matchID": 77466,
    "matchDateTime": "2026-02-28T18:30:00",
    "matchIsFinished": true,
    "leagueShortcut": "bl1",
    "leagueName": "1. Fußball-Bundesliga 2025/2026",
    "group": {
      "groupName": "24. Spieltag",
      "groupOrderID": 24
    },
    "team1": {
      "teamId": 7,
      "teamName": "Borussia Dortmund",
      "shortName": "Dortmund"
    },
    "team2": {
      "teamId": 40,
      "teamName": "FC Bayern München",
      "shortName": "Bayern"
    },
    "matchResults": [
      {
        "resultTypeID": 1,
        "resultName": "Halbzeit",
        "pointsTeam1": 1,
        "pointsTeam2": 0
      },
      {
        "resultTypeID": 2,
        "resultName": "Endergebnis",
        "pointsTeam1": 2,
        "pointsTeam2": 3
      }
    ]
  }
]
```

**Mapping Liquid → JSON:**

| Liquid-Variable | JSON-Pfad | Beispielwert |
|-----------------|-----------|-------------|
| `match.team1.teamId` | `[n].team1.teamId` | `7` |
| `match.team1.shortName` | `[n].team1.shortName` | `Dortmund` |
| `match.matchIsFinished` | `[n].matchIsFinished` | `true` |
| `match.leagueShortcut` | `[n].leagueShortcut` | `bl1` |
| `match.group.groupName` | `[n].group.groupName` | `24. Spieltag` |
| `r.resultTypeID` | `[n].matchResults[m].resultTypeID` | `2` (Endergebnis) |
| `r.pointsTeam1` | `[n].matchResults[m].pointsTeam1` | `2` |

---

## Hinweis zur Array-Antwort

Die OpenLigaDB API liefert ein **JSON-Array** (nicht ein Objekt mit benannten Schlüsseln wie bei Redmine). Im Liquid-Template wird das Array über die Variable `data` iteriert. Falls TRMNL die Variable anders benennt, passe die `{% for match in data reversed %}` Zeile im Markup entsprechend an.

---

## Anpassungen und Varianten

### Mehr Historie anzeigen

Ändere in der Polling-URL die `6` auf eine höhere Zahl (z.B. `10`):

```
https://api.openligadb.de/getmatchesbyteamid/40/10/0
```

Und im Markup die Zeile `match_num < 4` auf z.B. `match_num < 6` für 5 Historie-Einträge.

### Alle Wettbewerbe anzeigen (nicht nur Bundesliga)

Entferne im Markup die Bedingung `and match.leagueShortcut == "bl1"` aus der for-Schleife. Dann werden auch Champions League und DFB-Pokal Spiele angezeigt.

### Andere Teams

Ersetze die Team-ID `40` in der Polling-URL und im Markup. Einige IDs:

| Team | ID |
|------|-----|
| FC Bayern München | 40 |
| Borussia Dortmund | 7 |
| Bayer Leverkusen | 6 |
| RB Leipzig | 1635 |
| Eintracht Frankfurt | 91 |
| VfB Stuttgart | 16 |

---

## Troubleshooting

**Kein Inhalt auf dem Screen?** Teste die API-URL direkt im Browser: `https://api.openligadb.de/getmatchesbyteamid/40/1/0` – du solltest ein JSON-Array mit mindestens einem Spielobjekt sehen.

**"Keine Bundesliga-Ergebnisse verfügbar"?** Möglicherweise sind die letzten 6 Spiele alle aus anderen Wettbewerben (CL, Pokal). Erhöhe die Anzahl in der URL (z.B. auf `10`).

**Liquid-Variablenname stimmt nicht?** Die API liefert ein Array. TRMNL macht dieses ggf. unter einem bestimmten Variablennamen verfügbar. Prüfe in der TRMNL-Vorschau, welche Merge-Variablen verfügbar sind, und passe `{% for match in data reversed %}` entsprechend an.

**Datum wird nicht korrekt formatiert?** Falls `{{ match.matchDateTime | date: "%d.%m.%Y" }}` nicht funktioniert, kann man das Datum per String-Manipulation extrahieren: `{{ match.matchDateTime | slice: 8, 2 }}.{{ match.matchDateTime | slice: 5, 2 }}.{{ match.matchDateTime | slice: 0, 4 }}`

---

## Referenzen

- TRMNL Framework Docs: https://trmnl.com/framework
- TRMNL API Docs: https://docs.trmnl.com/go/
- TRMNL Screen Templating: https://docs.trmnl.com/go/private-plugins/templates
- OpenLigaDB API: https://www.openligadb.de
- OpenLigaDB GitHub: https://github.com/OpenLigaDB/OpenLigaDB-Samples
- Liquid Template Language: https://shopify.github.io/liquid/
- Inspiration: https://www.habendiebayernwiederverloren.de/
