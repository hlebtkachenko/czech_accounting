# Agent rules for this repository

## Scope

This repo is the Czech accounting extension app for ERPNext. Two kinds of agent work can
touch this system; keep them separate.

### Developer agent (works in this repo)
- Edit only `czech_accounting` source. Never modify upstream `frappe` or `erpnext`.
- Extend via hooks, Custom DocTypes, Custom Fields, fixtures, patches, and reports.
  Do not fork core to work around a missing extension point without recording the reason
  and adding regression tests.
- Conventional Commits. Tests are mandatory for non-trivial logic.
- English only in files, code, and comments (exception: official Czech statutory names
  where legal meaning requires them).

### Accounting assistant (later milestone, not yet built)
- Reaches ERPNext through a dedicated user with a custom, minimally-scoped role.
- Never receives Administrator, shell, direct SQL, or arbitrary Python.
- Creates **draft** documents only (`docstatus = 0`). Submit, Cancel, Delete, and amend
  stay human actions.
- Every bulk operation is idempotent and traceable to its input batch.

## Safety

- This repository is public and contains source only. Never commit credentials, `.env`
  files, keys, backups, or any accounting or customer data.
- Run `git status` before every push and confirm only source files are staged.
