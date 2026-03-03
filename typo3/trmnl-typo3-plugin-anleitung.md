# TRMNL Private Plugin: TYPO3 Releases (Polling)

## Übersicht

Zeigt die aktuellen TYPO3-Versionen (v10–v14) mit Maintenance- und ELTS-Enddaten auf dem TRMNL E-Ink Display an.

Datenquelle: [get.typo3.org API](https://get.typo3.org/api/v1/major/) – kostenlos, ohne Authentifizierung.

**Hinweis:** Diese Polling-Variante zeigt nur Versionsnamen und Support-Zeiträume. Für aktuelle Release-Nummern, Security-Releases und PHP-Versionen siehe die Webhook-Variante in `typo3-webhook/`.

---

## Schritt 1: Private Plugin anlegen

1. Gehe in deinem TRMNL-Account auf **Plugins** → **"Private Plugin"**
2. Vergib einen Namen, z.B. `TYPO3 Releases`
3. Wähle als **Strategy**: `Polling`

---

## Schritt 2: Polling konfigurieren

### Polling URL

```
https://get.typo3.org/api/v1/major/
```

### Polling Verb

```
GET
```

### Polling Headers

Leer lassen – keine Authentifizierung nötig.

---

## Schritt 3: Markup einfügen

Klicke auf **"Edit Markup"** und füge den Inhalt der Datei `typo3-trmnl-markup.html` ein.

---

## Schritt 4: Testen

1. Klicke auf **Save**, dann **"Force Refresh"**
2. Prüfe die Vorschau im TRMNL-Interface

---

## Hinweis zur Array-Antwort

Die API liefert ein JSON-Array. Im Liquid-Template wird `data` als Variablenname verwendet. Falls TRMNL die Variable anders benennt, passe `{% for v in data reversed %}` entsprechend an.

---

## Referenzen

- TYPO3 Release API: https://get.typo3.org/api/v1/major/
- TRMNL Framework Docs: https://trmnl.com/framework
- TRMNL Screen Templating: https://docs.trmnl.com/go/private-plugins/templates
