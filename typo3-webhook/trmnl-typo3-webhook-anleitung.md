# TRMNL Private Plugin: TYPO3 Release Dashboard (Webhook)

## Übersicht

Zeigt alle aktuellen TYPO3-Versionen (v10–v14) mit vollständigen Release-Informationen auf dem TRMNL E-Ink Display:

- Aktuelle Versionsnummer + Release-Datum
- Letztes Security-Release
- PHP-Kompatibilität
- Support-Status (Active / ELTS / EOL)

Datenquelle: [get.typo3.org API](https://get.typo3.org/) – kostenlos, ohne Authentifizierung.

---

## Voraussetzungen

- TRMNL-Gerät mit Developer Edition oder Developer Add-on
- Python 3.9+ (keine externen Dependencies)
- Ein Rechner/Server der das Script periodisch ausführt

---

## Schritt 1: Private Plugin anlegen

1. Gehe in deinem TRMNL-Account auf **Plugins** → **"Private Plugin"**
2. Vergib einen Namen, z.B. `TYPO3 Release Dashboard`
3. Wähle als **Strategy**: `Webhook`
4. Klicke auf **Save**
5. Notiere die **Webhook URL** (enthält deine Plugin UUID)

---

## Schritt 2: Markup einfügen

Klicke auf **"Edit Markup"** und füge den Inhalt der Datei `typo3-trmnl-markup.html` ein.

---

## Schritt 3: Script einrichten

### Umgebungsvariable setzen

```bash
export TRMNL_PLUGIN_UUID=deine-uuid-aus-schritt-1
```

### Manuell testen

```bash
python3 push-typo3.py
```

Erwartete Ausgabe:
```
Hole TYPO3-Versionsdaten...
  Verarbeite TYPO3 14...
  Verarbeite TYPO3 13 LTS...
  Verarbeite TYPO3 12 LTS...
  Verarbeite TYPO3 11 ELTS...
  Verarbeite TYPO3 10 ELTS...
  TYPO3 14: 14.1.1 (Active)
  TYPO3 13 LTS: 13.4.26 (Active)
  TYPO3 12 LTS: 12.4.43 (Active)
  TYPO3 11 ELTS: 11.5.50 (ELTS)
  TYPO3 10 ELTS: 10.4.56 (ELTS)
OK – Daten an TRMNL gepusht (200)
```

### Als Cronjob einrichten

TYPO3-Releases erscheinen typischerweise alle 2 Wochen (Dienstags). Ein Update alle 6 Stunden reicht aus:

```bash
crontab -e
```

```cron
0 */6 * * * TRMNL_PLUGIN_UUID=deine-uuid /usr/bin/python3 /pfad/zu/push-typo3.py >> /var/log/typo3-trmnl.log 2>&1
```

---

## Merge Variables

Das Script pusht folgende Variablen an TRMNL:

| Variable | Typ | Beispiel |
|----------|-----|----------|
| `updated` | String | `"03.03.2026 18:01 UTC"` |
| `versions` | Array | Siehe unten |

### Pro Version

| Variable | Typ | Beispiel |
|----------|-----|----------|
| `versions[n].title` | String | `"TYPO3 13 LTS"` |
| `versions[n].version` | Number | `13` |
| `versions[n].status` | String | `"Active"`, `"ELTS"`, `"EOL"` |
| `versions[n].latest` | String | `"13.4.26"` |
| `versions[n].latest_date` | String | `"20.02.2026"` |
| `versions[n].latest_type` | String | `"regular"`, `"security"` |
| `versions[n].security` | String | `"13.4.23"` |
| `versions[n].security_date` | String | `"13.01.2026"` |
| `versions[n].php` | String | `"8.2–8.5"` |
| `versions[n].maintained_until` | String | `"12/2027"` |
| `versions[n].elts_until` | String | `"12/2030"` |

---

## Konfiguration

| Umgebungsvariable | Standard | Beschreibung |
|-------------------|----------|-------------|
| `TRMNL_PLUGIN_UUID` | – | Plugin UUID aus der Webhook-URL (Pflicht) |
| `TYPO3_MIN_VERSION` | `10` | Kleinste angezeigte Major-Version |

---

## API-Endpoints

Das Script fragt pro Version 3 Endpoints ab:

| Endpoint | Daten |
|----------|-------|
| `/api/v1/major/` | Alle Versionen mit Support-Zeiträumen |
| `/api/v1/major/{v}/release/latest` | Aktuellstes Release |
| `/api/v1/major/{v}/release/latest/security` | Letztes Security-Release |
| `/api/v1/major/{v}/requirements` | PHP-Kompatibilität |

Insgesamt ~16 API-Calls pro Ausführung (1 + 3 pro Version). Alle Endpoints sind öffentlich und ohne Rate-Limit.

---

## Referenzen

- TYPO3 Release API: https://get.typo3.org/api/v1/major/
- TYPO3 API Docs: https://get.typo3.org/api/doc
- TRMNL Webhook Docs: https://docs.trmnl.com/go/private-plugins/webhooks
- TRMNL Framework Docs: https://trmnl.com/framework
