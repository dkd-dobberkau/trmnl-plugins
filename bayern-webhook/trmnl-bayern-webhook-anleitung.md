# TRMNL Private Plugin: Haben die Bayern wieder verloren? (Webhook)

## Übersicht

Diese Variante nutzt die **Webhook-Strategie** statt Polling. Ein Python-Script holt die Daten von OpenLigaDB, bereitet sie auf und pusht sie an TRMNL. Das Liquid-Template zeigt nur noch die fertigen Variablen an.

**Vorteile gegenüber der Polling-Variante:**
- Datenaufbereitung im Script (kein komplexes Liquid nötig)
- Bundesliga-Filterung und JA/NEIN/JEIN-Logik serverseitig
- Keine Probleme mit JSON-Array-Variablen in Liquid
- Volle Kontrolle über Datenformat und Update-Zeitpunkt

---

## Voraussetzungen

- TRMNL-Gerät mit Developer Edition oder Developer Add-on
- Python 3.9+ (keine externen Dependencies nötig)
- Ein Rechner/Server der das Script periodisch ausführt (Cronjob, systemd-Timer, etc.)

---

## Schritt 1: Private Plugin anlegen

1. Gehe in deinem TRMNL-Account auf **Plugins** → suche nach **"Private Plugin"**
2. Vergib einen Namen, z.B. `Haben die Bayern verloren?`
3. Wähle als **Strategy**: `Webhook`
4. Klicke auf **Save**
5. Notiere die **Webhook URL** – sie enthält deine Plugin UUID:
   `https://trmnl.com/api/custom_plugins/DEINE-UUID-HIER`

---

## Schritt 2: Markup einfügen

Klicke auf **"Edit Markup"** und füge den Inhalt der Datei `bayern-trmnl-markup.html` ein.

---

## Schritt 3: Script einrichten

### Umgebungsvariable setzen

```bash
export TRMNL_PLUGIN_UUID=deine-uuid-aus-schritt-1
```

### Manuell testen

```bash
python3 push-bayern.py
```

Erwartete Ausgabe:
```
Ergebnis: NEIN! – Dortmund 2:3 Bayern
OK – Daten an TRMNL gepusht (200)
```

### Als Cronjob einrichten (Empfehlung: alle 30 Minuten)

```bash
crontab -e
```

```cron
*/30 * * * * TRMNL_PLUGIN_UUID=deine-uuid /usr/bin/python3 /pfad/zu/push-bayern.py >> /var/log/bayern-trmnl.log 2>&1
```

TRMNL erlaubt max. 12 Requests/Stunde (30 mit TRMNL+). Ein Update alle 30 Minuten passt.

---

## Schritt 4: Testen

1. Führe `python3 push-bayern.py` aus
2. Prüfe die Vorschau im TRMNL-Interface unter Plugins → dein Private Plugin
3. Beim nächsten Refresh-Zyklus erscheint die Anzeige auf deinem TRMNL-Gerät

---

## Merge Variables

Das Script pusht folgende Variablen an TRMNL:

| Variable | Typ | Beispiel | Beschreibung |
|----------|-----|----------|-------------|
| `answer` | String | `"NEIN!"` | JA (Niederlage), NEIN (Sieg), JEIN (Unentschieden) |
| `score` | String | `"Dortmund 2:3 Bayern"` | Ergebnis mit Teamnamen |
| `matchday_name` | String | `"24. Spieltag"` | Spieltag-Bezeichnung |
| `date` | String | `"28.02.2026"` | Datum des Spiels |
| `history` | Array | siehe unten | Letzte 3 Bundesliga-Spiele |

### History-Einträge

| Variable | Typ | Beispiel |
|----------|-----|----------|
| `history[n].matchday` | Number | `23` |
| `history[n].score` | String | `"Bayern 3:2 Frankfurt"` |
| `history[n].outcome` | String | `"S"` (Sieg), `"N"` (Niederlage), `"U"` (Unentschieden) |

---

## Konfiguration

| Umgebungsvariable | Standard | Beschreibung |
|-------------------|----------|-------------|
| `TRMNL_PLUGIN_UUID` | – | Plugin UUID aus der Webhook-URL (Pflicht) |
| `BAYERN_TEAM_ID` | `40` | OpenLigaDB Team-ID |
| `BAYERN_HISTORY` | `3` | Anzahl Historie-Einträge |

### Andere Teams

Ändere `BAYERN_TEAM_ID`:

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

**"TRMNL_PLUGIN_UUID nicht gesetzt"?** Exportiere die Variable: `export TRMNL_PLUGIN_UUID=deine-uuid`

**"Fehler beim Abrufen der OpenLigaDB Daten"?** Prüfe deine Internetverbindung. Teste die API direkt: `curl https://api.openligadb.de/getmatchesbyteamid/40/1/0`

**"TRMNL API Fehler: 429"?** Rate-Limit erreicht. Reduziere die Cronjob-Frequenz.

**"Keine Ergebnisse" auf dem Display?** Das Script hat möglicherweise keine beendeten Bundesliga-Spiele gefunden. Prüfe die Ausgabe von `python3 push-bayern.py`.

---

## Referenzen

- TRMNL Webhook Docs: https://docs.trmnl.com/go/private-plugins/webhooks
- TRMNL Framework Docs: https://trmnl.com/framework
- TRMNL Screen Templating: https://docs.trmnl.com/go/private-plugins/templates
- OpenLigaDB API: https://www.openligadb.de
- Liquid Template Language: https://shopify.github.io/liquid/
- Inspiration: https://www.habendiebayernwiederverloren.de/
