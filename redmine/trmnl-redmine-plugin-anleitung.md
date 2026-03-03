# TRMNL Private Plugin: Redmine Issues auf dem E-Ink Display

## Übersicht

Dieses Plugin zeigt deine offenen Redmine-Tickets direkt auf dem TRMNL E-Ink Display an. Es nutzt die **Polling-Strategie** – TRMNL fragt periodisch die Redmine REST API ab und rendert die Ergebnisse als Tabelle mit Ticket-Nr, Subject, Priorität und Status.

---

## Voraussetzungen

- TRMNL-Gerät mit Developer Edition oder Developer Add-on
- Redmine-Instanz mit aktivierter REST API (Administration → Settings → API → "Enable REST API")
- Dein persönlicher Redmine API Key (unter "My Account" → rechte Spalte → "API access key")

---

## Schritt 1: Private Plugin anlegen

1. Gehe in deinem TRMNL-Account auf **Plugins** → suche nach **"Private Plugin"**
2. Vergib einen Namen, z.B. `Redmine – Meine Tickets`
3. Wähle als **Strategy**: `Polling`

---

## Schritt 2: Polling konfigurieren

### Polling URL

```
https://DEINE-REDMINE-URL/issues.json?assigned_to_id=me&status_id=open&sort=priority:desc,updated_on:desc&limit=10
```

Ersetze `DEINE-REDMINE-URL` durch die tatsächliche Adresse deiner Redmine-Instanz.

**URL-Parameter im Detail:**

| Parameter | Wert | Beschreibung |
|-----------|------|-------------|
| `assigned_to_id` | `me` | Nur dir zugewiesene Tickets |
| `status_id` | `open` | Nur offene Tickets |
| `sort` | `priority:desc,updated_on:desc` | Sortierung: Priorität absteigend, dann letzte Aktualisierung |
| `limit` | `10` | Maximal 10 Tickets (empfohlen für 800×480 Display) |

### Polling Verb

```
GET
```

### Polling Headers

```
X-Redmine-API-Key=DEIN_API_KEY
```

Ersetze `DEIN_API_KEY` durch deinen persönlichen API-Schlüssel aus Redmine.

### Polling Body

Leer lassen (nicht benötigt bei GET).

---

## Schritt 3: Markup einfügen

Klicke auf **"Edit Markup"** und füge folgendes Liquid-Template ein:

```html
<div class="layout layout--col">
  <div class="columns">
    <div class="column">
      <span class="title title--small">Meine offenen Tickets</span>

      {% if issues.size > 0 %}
      <table class="table" data-table-overflow="true">
        <thead>
          <tr>
            <th>#</th>
            <th>Ticket</th>
            <th>Priorität</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {% for issue in issues %}
          <tr>
            <td>{{ issue.id }}</td>
            <td>{{ issue.subject | truncate: 38 }}</td>
            <td>{{ issue.priority.name }}</td>
            <td>{{ issue.status.name }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% else %}
      <span class="label">Keine offenen Tickets – Zeit für einen Kaffee ☕</span>
      {% endif %}

      <span class="label label--small">{{ issues.size }} offene Tickets</span>
    </div>
  </div>
</div>

<div class="title_bar">
  <img class="image" src="https://trmnl.com/images/plugins/trmnl--render.svg" />
  <span class="title">Redmine</span>
  <span class="instance">Meine Tickets</span>
</div>
```

---

## Schritt 4: Testen

1. Klicke auf **Save** in den Plugin-Einstellungen
2. Klicke auf **"Force Refresh"** um sofort einen neuen Screen zu generieren
3. Prüfe die Vorschau im TRMNL-Interface unter Plugins → dein Private Plugin
4. Beim nächsten Refresh-Zyklus erscheint die Anzeige auf deinem TRMNL-Gerät

---

## Redmine API – Antwortformat

Die Redmine REST API liefert JSON in diesem Format. Die Liquid-Variablen im Markup greifen auf die verschachtelten Objekte zu:

```json
{
  "issues": [
    {
      "id": 4821,
      "subject": "TYPO3 Solr: Vector Search Index Config",
      "priority": { "id": 5, "name": "Urgent" },
      "status": { "id": 2, "name": "In Arbeit" },
      "tracker": { "id": 1, "name": "Bug" },
      "project": { "id": 3, "name": "Kundenprojekt X" },
      "assigned_to": { "id": 1, "name": "Olivier Dobberkau" },
      "updated_on": "2026-03-01T14:22:00Z"
    }
  ],
  "total_count": 7,
  "limit": 10,
  "offset": 0
}
```

**Mapping Liquid → JSON:**

| Liquid-Variable | JSON-Pfad | Beispielwert |
|-----------------|-----------|-------------|
| `{{ issue.id }}` | `issues[n].id` | `4821` |
| `{{ issue.subject }}` | `issues[n].subject` | `TYPO3 Solr: Vector Search…` |
| `{{ issue.priority.name }}` | `issues[n].priority.name` | `Urgent` |
| `{{ issue.status.name }}` | `issues[n].status.name` | `In Arbeit` |

---

## Anpassungen und Varianten

### Tickets eines bestimmten Projekts

Ersetze die Polling-URL durch:

```
https://DEINE-REDMINE-URL/issues.json?project_id=PROJEKT_ID&status_id=open&sort=priority:desc&limit=10
```

### Zusätzlich den Tracker anzeigen (Bug, Feature, Task)

Füge eine weitere Spalte in die Tabelle ein:

```html
<th>Typ</th>
<!-- ... und im tbody: -->
<td>{{ issue.tracker.name }}</td>
```

### Nur Tickets mit hoher Priorität

Ergänze den URL-Parameter:

```
&priority_id=4,5
```

(Die IDs hängen von deiner Redmine-Konfiguration ab – prüfe unter Administration → Enumerations → Issue Priorities.)

### Custom Fields abfragen

Für benutzerdefinierte Felder, die als Filter aktiviert sind:

```
&cf_FELD_ID=WERT
```

### Form Fields für flexible Konfiguration

Du kannst die Plugin-Einstellungen dynamisch machen, indem du TRMNL Form Fields nutzt. Füge im Plugin unter "Form Fields" folgendes YAML ein:

```yaml
- keyname: redmine_url
  field_type: text
  name: Redmine URL
  description: Basis-URL deiner Redmine-Instanz
  help_text: "z.B. https://redmine.dkd.de"
- keyname: api_key
  field_type: text
  name: API Key
  description: Dein persönlicher Redmine API Key
  help_text: Findest du unter My Account
- keyname: ticket_limit
  field_type: select
  options:
    - '5'
    - '8'
    - '10'
    - '15'
  name: Anzahl Tickets
  description: Wie viele Tickets sollen angezeigt werden?
```

Dann nutze in der Polling-URL die Interpolation:

```
##{{ redmine_url }}/issues.json?assigned_to_id=me&status_id=open&sort=priority:desc&limit=##{{ ticket_limit }}
```

Und in den Polling Headers:

```
X-Redmine-API-Key=##{{ api_key }}
```

---

## Troubleshooting

**Kein Inhalt auf dem Screen?** Prüfe, ob die Redmine REST API aktiviert ist und dein API Key korrekt ist. Teste die URL direkt im Browser: `https://DEINE-REDMINE-URL/issues.json?key=DEIN_API_KEY&assigned_to_id=me&limit=1`

**Tabelle wird abgeschnitten?** Das Attribut `data-table-overflow="true"` sorgt dafür, dass TRMNL automatisch einen "and X more"-Hinweis anzeigt, wenn mehr Zeilen vorhanden sind als auf den Screen passen. Reduziere ggf. den `limit`-Parameter.

**JavaScript im Markup funktioniert nicht?** Wickle JS-Code immer in `document.addEventListener("DOMContentLoaded", function(e) { ... })` ein.

**Sonderzeichen werden nicht korrekt angezeigt?** Stelle sicher, dass dein Redmine UTF-8 als Encoding nutzt. Die Liquid-Engine von TRMNL unterstützt Unicode.

---

## Referenzen

- TRMNL Framework Docs: https://trmnl.com/framework
- TRMNL API Docs: https://docs.trmnl.com/go/
- TRMNL Screen Templating: https://docs.trmnl.com/go/private-plugins/templates
- Redmine REST API: https://www.redmine.org/projects/redmine/wiki/Rest_api
- Redmine Issues API: https://www.redmine.org/projects/redmine/wiki/Rest_Issues
- Liquid Template Language: https://shopify.github.io/liquid/
