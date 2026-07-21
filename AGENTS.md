# Agent & contributor guide

Single source of truth for how agents (Claude, Codex, Cursor) and humans work in this
repo. `CLAUDE.md` is a symlink to this file. Keep this a concise router with inline hard
rules; deep procedure lives in `docs/` and is linked by name.

This repo is `czech_accounting`: a Frappe app that adds Czech statutory accounting behavior
on top of **ERPNext** (Frappe v16 + ERPNext v16). See [ARCHITECTURE.md](ARCHITECTURE.md)
for the shape and [docs/README.md](docs/README.md) for where everything lives.

## Scope — two agent roles, kept separate

### Developer agent (works in this repo)
- Edit only `czech_accounting` source. **Never** modify upstream `frappe` or `erpnext`.
  Why: this is an extension, not a fork; core stays upgradeable.
- Extend through supported points only: hooks, Custom DocTypes, Custom Fields, fixtures,
  patches, reports. Do not fork core to work around a missing extension point without
  recording the reason (an ADR) and adding regression tests.
- Read the source before you use it. Never guess an API, field, or hook signature; the
  knowledge base ([docs/knowledge-base/](docs/knowledge-base/)) is source-verified — use it.

### Accounting assistant (later milestone, not yet built)
- Reaches ERPNext through a dedicated user with a custom, minimally-scoped role.
- Never receives Administrator, shell, direct SQL, or arbitrary Python.
- Creates **draft** documents only (`docstatus = 0`). Submit, Cancel, Delete, and amend
  stay human actions. Why: agent-created entries must never post to the ledger unreviewed.
- Every bulk operation is idempotent and traceable to its input batch (content hash, batch
  id, parser version, agent identity).

## Domain invariants (non-negotiable)
- **Extension, not fork.** Core is never edited.
- **Effective-dated rules.** Statutory behavior (VAT rates, statement layouts, required
  fields) carries an effective date and is versioned. Never hardcode a rule as timeless.
- **Draft-only automation.** Automated/agent documents are drafts; submission is human.
- **No posting to group accounts.** Detect and reject unmapped posting accounts.
- **Draft-only is the hard control.** Agent/automated documents stay `docstatus = 0`; a human
  reviews and submits. Accountant sign-off on legal outputs (CoA, statements, VAT XML) is
  advisory, not a blocking gate. Software tests prove consistency with encoded rules, not which
  legal regime applies.
- **Traceability.** Every reported figure traces back to its source voucher and attachment.

## Dev workflow — author here, the server only runs
The server is a running bench; this repo is the source of truth. Do **not** author DocTypes
in the browser UI on the server — developer mode writes them to the server tree, which this
repo never sees, splitting the source of truth. Write schema as files here.

1. Edit files in this repo (Python, DocType JSON, fixtures, reports).
2. Commit + push (Conventional Commits).
3. Apply on the server: `git pull` → `bench --site <site> migrate` → `bench --site <site> clear-cache`.
4. Restart the bench only when you change `hooks.py`, assets, or scheduler config.
5. Test via `bench --site <site> console` or `bench --site <site> run-tests --app czech_accounting`.

## Verification after changes (hard gate)
Before you call a change done:
- `bench migrate` runs clean on a dev site (no schema/patch errors).
- Tests pass for the changed area; non-trivial logic ships with a test that covers the
  **failure** mode, not just the happy path.
- No secrets or data staged: `git status` shows only source files.
- If the change touches a **statutory output**, it is effective-dated and flagged for
  accountant sign-off.

## Code standards (Python / Frappe)
- English only in code, files, and comments. Exception: official Czech statutory names
  where legal meaning requires them.
- Keep it simple. Three similar lines beat one helper used once. No premature abstraction.
- No defensive code for scenarios that cannot happen. Validate only at system boundaries
  (user input, external APIs, imported documents).
- No backwards-compat hacks; delete unused code. No unnecessary comments on unchanged code.
- Naming, imports, and layout: see [docs/conventions/code-naming.md](docs/conventions/code-naming.md).

## Commits, PRs, documentation
- Conventional Commits: `feat` `fix` `chore` `docs` `refactor` `test`. See
  [docs/conventions/COMMITS.md](docs/conventions/COMMITS.md).
- One concern per PR. Fill the PR template (risk, rollback, verification, compliance).
- Review checklist: [docs/conventions/CODE-REVIEW.md](docs/conventions/CODE-REVIEW.md).
- Architectural decisions are recorded as ADRs in [docs/adr/](docs/adr/) — an ADR with no
  trade-off (Negative) bullet is incomplete.
- When code changes a documented surface, update its doc in the same change.

## Safety
This repository is public and contains source only. Never commit credentials, `.env` files,
keys, backups, or any accounting or customer data. Run `git status` before every push and
confirm only source files are staged.
