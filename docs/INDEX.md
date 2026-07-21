---
title: Knowledge Base Index
kind: index
status: maintained
evidence_grade: structural
scope: Frappe v16 and ERPNext v16
last_verified: 2026-07-21
---

# Knowledge Base Index

## Verified source baseline

| Component | Release or snapshot | Exact commit | Local evidence snapshot |
|---|---|---|---|
| Frappe Framework | `v16.27.1` | `f33ac3f00ab818e21b25ddbec93efb653fd9aa1b` | `work/kb-source-snapshots/frappe` |
| ERPNext | `v16.28.0` | `de591661b9ba0bd3f62ac25b99b5c85c723515f6` | `work/kb-source-snapshots/erpnext` |
| Frappe Docker | `v3.2.1` | `d4a310089f5d6fc38ed1317b898d75b9c74901db` | `work/kb-source-snapshots/frappe_docker` |
| Frappe MCP | `main`, captured 2026-07-21 | `11d5076b1bf4483b2ff6751a13e0736f5396b1e6` | `work/kb-source-snapshots/mcp` |

The local paths are research provenance for agents working in this workspace. They are not intended to become links in the final project repository.

## Coverage

| Area | State | Entry point |
|---|---|---|
| Frappe DocTypes | Accepted, source-verified benchmark | [DocType reference index](framework/doctypes/INDEX.md) |
| Frappe developer architecture | Accepted, source-verified | [Frappe Developer Architecture](framework/architecture/INDEX.md) |
| Frappe apps, sites, hooks, permissions, API, jobs, tests | Accepted, source-verified | [Frappe Developer Architecture](framework/architecture/INDEX.md) |
| ERPNext Accounting architecture | Accepted, source-verified | [ERPNext Accounting](erpnext/accounting/INDEX.md) |
| Czech accounting requirements | Accepted official-source inventory | [Czech Accounting Requirements](czech-accounting/INDEX.md) |
| Docker and operations | Not yet accepted | Expansion after technical foundation |

No topic is called verified merely because it exists in this folder.

## Governance

- [Agent Instructions](AGENTS.md)
- [Purpose and usage](README.md)
- [Evidence Standard](governance/EVIDENCE_STANDARD.md)
- [Reference Note Template](governance/REFERENCE_NOTE_TEMPLATE.md)
- [Research and Audit Log](governance/RESEARCH_LOG.md)
- [Source Registry](sources/INDEX.md)
