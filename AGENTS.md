# Agent rules for this repository

## Scope

This repo is the Czech accounting extension app for ERPNext. Two kinds of agent work
touch this system; keep them separate.

### Developer agent (works in this repo)
- Edit only `czech_accounting` source. Never modify upstream `frappe` or `erpnext`.
- Extend via hooks, Custom DocTypes, Custom Fields, fixtures, patches, reports. No fork.
- Conventional Commits. Tests are mandatory for non-trivial logic.
- English only in all files, code, and comments (exception: official Czech statutory
  names where legal meaning requires them).

### Accounting assistant (later milestone, not yet built)
- Reaches ERPNext through a dedicated user with a custom `Accounting Assistant` role.
- Never receives `Administrator`, shell, direct SQL, or arbitrary Python.
- Creates **Draft** documents only (`docstatus = 0`). Submit / Cancel / Delete / amend
  stay human actions.
- Every bulk operation is idempotent and traceable to its input batch.

## Hard safety rules

- This repository is **public**. Never commit secrets, `.env` files, keys, backups, or
  any accounting/customer data. Real credentials live on the VPS and in a password
  manager.
- Run `git status` before every push and confirm only source files are staged.
- Never fork or edit ERPNext/Frappe core to work around a missing extension point without
  recording the reason and adding regression tests.
