---
title: Source Registry
kind: source-registry
status: maintained
evidence_grade: structural
scope: Frappe v16 and ERPNext v16
last_verified: 2026-07-21
---

# Source Registry

## Pinned repositories

| ID | Official repository | Release | Commit | Role |
|---|---|---|---|---|
| `frappe-v16` | [frappe/frappe](https://github.com/frappe/frappe) | `v16.27.1` | [`f33ac3f00ab818e21b25ddbec93efb653fd9aa1b`](https://github.com/frappe/frappe/tree/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b) | Exact Framework behavior and tests |
| `erpnext-v16` | [frappe/erpnext](https://github.com/frappe/erpnext) | `v16.28.0` | [`de591661b9ba0bd3f62ac25b99b5c85c723515f6`](https://github.com/frappe/erpnext/tree/de591661b9ba0bd3f62ac25b99b5c85c723515f6) | Exact ERPNext behavior and tests |
| `frappe-docker` | [frappe/frappe_docker](https://github.com/frappe/frappe_docker) | `v3.2.1` | [`d4a310089f5d6fc38ed1317b898d75b9c74901db`](https://github.com/frappe/frappe_docker/tree/d4a310089f5d6fc38ed1317b898d75b9c74901db) | Exact container build and Compose baseline |
| `frappe-mcp` | [frappe/mcp](https://github.com/frappe/mcp) | Captured `main` | [`11d5076b1bf4483b2ff6751a13e0736f5396b1e6`](https://github.com/frappe/mcp/tree/11d5076b1bf4483b2ff6751a13e0736f5396b1e6) | Experimental MCP source snapshot |

## Official documentation behavior

The official documentation URLs do not encode a Frappe patch version. Record the retrieval date in each note and validate version-sensitive statements against `frappe-v16` or `erpnext-v16`.

DocType benchmark pages:

- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Controllers](https://docs.frappe.io/framework/user/en/basics/doctypes/controllers)
- [Field Types](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)

## Retrieval record

- 2026-07-21: GitHub releases and commits resolved directly from the official GitHub API and repositories.
- 2026-07-21: DocType benchmark pages opened from the official Frappe documentation site.

