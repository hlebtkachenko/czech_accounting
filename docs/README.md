# Documentation

Map of everything under `docs/` and where to look for it.

## Start here

| I need... | Go to |
|---|---|
| The phased build plan + acceptance criteria | [ROADMAP.md](ROADMAP.md) |
| How Frappe / ERPNext / Czech accounting actually work (researched reference) | [knowledge-base/INDEX.md](knowledge-base/INDEX.md) |
| Agent working rules for this repo | [../AGENTS.md](../AGENTS.md) |
| System architecture + extension principles | [../ARCHITECTURE.md](../ARCHITECTURE.md) |
| What the app is + how to run and develop it | [../README.md](../README.md) |

## Knowledge base — `docs/knowledge-base/`

Researched, source-verified reference for **Frappe v16 + ERPNext v16 + Czech accounting**. It is a navigation layer for development, not a copy of upstream docs. Entry point: [knowledge-base/INDEX.md](knowledge-base/INDEX.md).

| Topic | Where |
|---|---|
| Frappe framework: DocTypes, architecture, hooks, permissions, API, jobs, tests | [knowledge-base/framework/](knowledge-base/framework/) |
| ERPNext accounting engine: ledger, vouchers, tax, chart of accounts, periods, imports, reports | [knowledge-base/erpnext/accounting/](knowledge-base/erpnext/accounting/) |
| Czech statutory requirements: applicability, books, retention, VAT / currency / corrections | [knowledge-base/czech-accounting/](knowledge-base/czech-accounting/) |
| Evidence standard, reference-note template, research log | [knowledge-base/governance/](knowledge-base/governance/) |
| Source registry (official sources) | [knowledge-base/sources/](knowledge-base/sources/) |

Nothing in the knowledge base is treated as verified merely because it exists; each topic carries its own evidence state (see the KB index).

## Project docs — `docs/`

| File | Purpose |
|---|---|
| [ROADMAP.md](ROADMAP.md) | Phased build plan (Phases A-F) with deliverables and acceptance criteria |
