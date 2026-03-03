# TRMNL Plugins

Private plugins for [TRMNL](https://usetrmnl.com) e-ink displays.

## Plugins

### Redmine – Meine Tickets

Displays your open Redmine issues sorted by priority on the TRMNL screen.

- **Strategy:** Polling (TRMNL queries the Redmine REST API directly)
- **Auth:** Redmine API Key via header
- **Folder:** [`redmine/`](redmine/)

### Haben die Bayern wieder verloren?

Shows FC Bayern Munich's latest Bundesliga result: **JA** (loss), **NEIN** (win), or **JEIN** (draw), plus a 3-match history.

Data source: [OpenLigaDB](https://www.openligadb.de) (free, no auth required).

Available in two variants:

| Variant | Strategy | Folder | Description |
|---------|----------|--------|-------------|
| Polling | TRMNL polls OpenLigaDB directly | [`bayern/`](bayern/) | Simple setup, all logic in Liquid |
| Webhook | Python script pushes to TRMNL | [`bayern-webhook/`](bayern-webhook/) | Server-side processing, simpler template |

### TYPO3 Release Dashboard

Shows all current TYPO3 versions (v10–v14) with latest release, last security release, PHP compatibility, and support status (Active/ELTS/EOL).

Data source: [get.typo3.org API](https://get.typo3.org/) (free, no auth required).

Available in two variants:

| Variant | Strategy | Folder | Description |
|---------|----------|--------|-------------|
| Polling | TRMNL polls get.typo3.org directly | [`typo3/`](typo3/) | Version names + support dates only |
| Webhook | Python script pushes to TRMNL | [`typo3-webhook/`](typo3-webhook/) | Full dashboard: releases, security, PHP |

## Setup

Each plugin folder contains:

- `*-trmnl-markup.html` – Liquid template to paste into TRMNL's Markup Editor
- `*-trmnl-preview.html` – Local preview with sample data (open in browser)
- `*-anleitung.md` – Step-by-step setup guide (German)

You need a TRMNL device with the Developer Edition or Developer Add-on.

## Data Sources

| Plugin | API | Auth |
|--------|-----|------|
| Redmine | Your Redmine instance REST API | API Key |
| Bayern | [OpenLigaDB](https://api.openligadb.de) | None |
| TYPO3 | [get.typo3.org](https://get.typo3.org/api/v1/major/) | None |

## License

[MIT](LICENSE)
