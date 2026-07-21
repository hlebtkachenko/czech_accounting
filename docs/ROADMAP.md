# Roadmap

Phased build plan for `czech_accounting`. Each phase lists deliverables and acceptance
criteria. Statutory rules are effective-dated and versioned; legal outputs require
accountant sign-off before real use. Base legal frame: Act 563/1991 Coll. (Accounting),
Decree 500/2002 Coll. (entrepreneurs, double-entry), Czech Accounting Standards, and Act
235/2004 Coll. (VAT) for registered entities.

## Phase A — Czech Chart of Accounts (first, unblocks everything)

A Company's chart of accounts is fixed at creation, so this must exist before any real
company is created.

Deliverables:
- Versioned Czech CoA template based on the directional chart in Annex 4 of Decree
  500/2002 Coll. (account classes 0-7 and groups; the entity defines the detailed plan).
- Account numbers, account types, parent groups, currency behavior, and ERPNext account
  types.
- Mechanism to make the template selectable when creating a Company (custom chart source).
- Mapping from each ledger account to Czech Balance Sheet and Profit & Loss rows.
- Validation: no posting to group accounts; detect unmapped posting accounts.

Acceptance:
- A new Company created with the Czech CoA gets the full account tree.
- Every posting account maps to a statement row.
- The account tree matches an accountant-approved reference for a representative entity.

## Phase B — Czech company foundation

Deliverables:
- IČO, DIČ, Czech address and bank fields on Company / Customer / Supplier.
- Number series (variable/constant/specific symbol handling), fiscal year, CZK base
  currency, rounding accounts, payment terms.
- Recreate the initial placeholder company with the Czech CoA (delete it while empty
  first, since a Company's CoA is fixed at creation), then add the client companies.

Acceptance:
- All posting accounts mapped; opening trial balance agrees with the approved source.
- Each client company is isolated by Company field and permissions.

## Phase C — Accounting books and statutory statements

Deliverables:
- Czech accounting journal (chronological) and general ledger (by account).
- Analytical and off-balance-sheet books where applicable.
- Czech Balance Sheet and Profit & Loss in the statutory layout (relevant annex to Decree
  500/2002 Coll.); Czech trial balance.
- Drill-down from every report row to the source voucher and attachment.
- Period-close checks and archival export.

Acceptance:
- Debit = credit at voucher, period, and ledger totals.
- Opening balance + period turnover = closing balance per account.
- All statement amounts reconcile to the trial balance; accountant approves samples.

## Phase D — VAT / DPH

Deliverables:
- Effective-dated VAT templates, rates, and document classifications; reverse charge and
  EU treatment; corrective tax documents.
- VAT reconciliation from source invoices through GL to return rows.
- XML generation for DPHDP3 (return), DPHKH1 (control statement), DPHSHV (VIES) where
  applicable; validation against the current official EPO XSD; a readable reconciliation
  report with every export.

Acceptance:
- XML passes the official schema validator.
- Every reported line reconciles to source documents and GL accounts.
- Reference-period results agree with an accountant-approved calculation.

## Phase E — Integrations

Deliverables:
- ARES lookup by IČO for supplier/customer master data (suggestion only, never silent
  overwrite).
- ISDOC 6.0.2 import (received invoices) and export (issued invoices).
- Optional Czech National Bank exchange-rate import after the accounting policy is set.

Acceptance:
- Imports are idempotent; source documents stay attached and traceable.
- Invalid documents produce actionable errors and no partial submitted entries.

## Phase F — Assisted data entry (agent access)

Deliverables:
- Dedicated ERPNext user + minimally-scoped custom role; no Administrator/SQL/shell.
- Narrow whitelisted methods for invoice staging, validation, and draft creation with
  duplicate detection and batch reporting.

Acceptance:
- The role cannot submit, cancel, delete, run SQL, or access unrelated private records.
- Repeating a batch creates no duplicates; every draft traces to source file, batch,
  parser version, and agent user.

## Not in scope yet

Baked production image + CI, full restore rehearsal, encrypted off-box backups, remote
access convenience layer. These come after the accounting behavior is correct.
