# Stream 1 — Foundation & Chart of Accounts

Branch `stream/1-foundation-coa`. **Merges first.** This is the base Streams 2 and 3 depend
on. Read `00-master.md` (the shared contract) first. Owns only the files listed for Stream 1
in the contract's file-ownership map — do not touch document or report files.

## Goal
A versioned Czech chart of accounts, every posting account mapped to a statement row, plus
the party fields and VAT accounts the other streams reference by number.

## Inputs
- `research/coa-normalized.json` — 368 nodes (305 synthetic + 1 analytical), `root_type`
  from the `Typ` column. This is the source; transform it, do not re-derive from scratch.
- `research/coa-analysis.md` — the class→root_type table, the 17 mixed nodes to re-parent,
  and the converter verdict (reuse its schema + split algorithm, not its data).

## Tasks
1. **Build the CoA tree.** Transform `coa-normalized.json` into an ERPNext chart tree
   (class → group → synthetic → analytical) with `root_type`, `account_type`, `is_group`,
   `parent`, `account_number`.
   - Re-parent the 17 mixed nodes (classes 2/3/4, groups 33/37/38) so each subtree has one
     `root_type` (ERPNext rule). Handle class-7 closing and contra/impairment (09x/19x/29x/39x).
   - Set `account_type` where it matters: Bank (221), Cash (211), Receivable (311), Payable
     (321), Tax (343), Fixed Asset (02x), Accumulated Depreciation (08x), Stock, COGS, etc.
   - Drop abolished accounts (e.g. `011 Zřizovací výdaje`).
   - Keep the standard synthetic set; add only the agreed analytics (`343.100`/`343.200`,
     `221001`). Analyticals are skippable where not needed.
2. **Ship + create.** Store the tree JSON in the app and create `Account` records
   **programmatically** (`after_install` + an idempotent patch), NOT via the CoA Importer
   (destructive, zero-transaction only). Re-runnable without duplicating accounts.
3. **Account Category taxonomy (the seam to Stream 3).** Assign every posting account a
   category code that maps it to a Rozvaha row (Decree 500/2002 Příloha 1) and a VZZ-druhové
   row (Příloha 2). Ship as `fixtures/account_category*.json`. This is the contract Stream 3
   consumes — freeze the code set and document it.
4. **Party/company fields.** `cz_ico` custom field on Company/Customer/Supplier via fixtures;
   confirm `tax_id` carries DIČ. (Document invoice/payment fields belong to Stream 2 — only
   the party fields here.)
5. **VAT accounts + base config.** Create 343 with analytics `343.100` (na vstupu) /
   `343.200` (na výstupu); CZK base; rounding accounts. (Tax *templates* are Stream 2.)
6. **hooks.py fixtures skeleton.** Pre-declare the full `fixtures` list (Custom Field,
   Account Category, Financial Report Template, Naming Series, Mode of Payment, Asset
   Category, Finance Book) so Streams 2 and 3 add JSON files without editing hooks.py.
7. **Validation.** Block posting to group accounts; a report that detects any posting account
   with no statement category; confirm class-7/off-balance handled.
8. **Reuse review.** Skim `research/coa-analysis.md` converter section — adopt the CSV schema
   and mixed-class split logic, reject its miscoded account_types (`389`, forced party ledgers).

## Acceptance
- A fresh test company created on the Czech CoA gets the full synthetic tree (305 accounts).
- Every posting account resolves to exactly one statement category (completeness report green).
- `bench migrate` clean; account creation is idempotent (re-run adds nothing).
- Accountant sign-off on the chart before real use.

## Verify
Create a throwaway company on the Czech CoA over SSH (`bench console`), count accounts, run
the category-completeness check, then delete it.
