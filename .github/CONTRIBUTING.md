# Contributing

Read [AGENTS.md](../AGENTS.md) first — it is the source of truth for how work is done here.
This file is the short human checklist.

## Hard rules

1. Extension, not fork. Never edit upstream `frappe` or `erpnext`.
2. English only in code, files, and comments (exception: official Czech statutory names).
3. Statutory rules are effective-dated and versioned, never hardcoded as timeless.
4. Legal outputs (CoA, statements, VAT XML) need accountant sign-off before real use.
5. Automated/agent documents are draft-only (`docstatus = 0`). Never auto-submit.
6. Public repo: never commit secrets, `.env`, keys, backups, or client/accounting data.
7. Author schema as files in this repo, never via the server browser UI.

## Workflow

- Branch from an up-to-date `main`.
- Conventional Commits ([docs/conventions/COMMITS.md](../docs/conventions/COMMITS.md)).
- One concern per PR. Fill the PR template.
- Record architectural decisions as ADRs ([docs/adr/](../docs/adr/)).

## Testing

- Non-trivial logic ships with tests that cover the failure mode.
- Run `bench --site <site> run-tests --app czech_accounting`.

## Pre-merge gates

- [ ] `bench migrate` clean, tests pass.
- [ ] No secrets or data staged (`git status`).
- [ ] Statutory changes are effective-dated and flagged for sign-off.
- [ ] Review checklist applied ([docs/conventions/CODE-REVIEW.md](../docs/conventions/CODE-REVIEW.md)).
