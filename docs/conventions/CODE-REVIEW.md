# Code review checklist

Read the diff backwards — start at the last hunk, where intent is clearest. Review for these,
in order.

## Always
- One concern. Unrelated changes belong in another PR.
- The change does what the PR says, and nothing surprising beyond it.
- No secrets, `.env`, keys, backups, or accounting/customer data staged.

## Code quality
- Simple over clever. Three similar lines beat one helper used once.
- No premature abstraction; no backwards-compat hacks; unused code deleted.
- No defensive code for scenarios that cannot happen.
- Validation only at boundaries (user input, external APIs, imported documents).
- English only (exception: official Czech statutory names).

## Tests
- Non-trivial logic has a test that covers the **failure** mode, not the happy path that
  was already debugged.
- `bench migrate` runs clean; the suite passes.

## Accounting / Frappe
- Touches a statutory output? It is effective-dated and flagged for accountant sign-off.
- Extension points only — no core edits, no fork without an ADR.
- No posting to group accounts; unmapped posting accounts are detected.
- Automated writes stay draft-only (`docstatus = 0`).
- Schema authored as files (DocType JSON / fixtures), not via the server UI.

## Architecture
- Hard-to-reverse decisions are captured in an ADR with real trade-offs.
- Reported figures remain traceable to source voucher and attachment.
