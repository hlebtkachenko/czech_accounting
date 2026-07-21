# Stream 1 — change log (for Streams 2 & 3)

What branch `stream/1-foundation-coa` adds/changes. Stream 1 merges first; Streams 2 & 3 rebase
onto it. This complements the frozen contract in `00-master.md` — read both. Updated as work lands.

## Landed
- **Czech CoA tree** `czech_accounting/czech_accounting/chart_of_accounts/cz_coa.json` (generated
  by `scripts/build_cz_coa.py`). 5 root_type roots (Aktiva/Cizí zdroje/Vlastní kapitál/Výnosy/
  Náklady); Czech classes split under them. Applied via `create_charts(company, custom_chart=...)`.
- **Accounts added** beyond the client's source chart (it omitted them):
  - `611` Změna stavu nedokončené výroby, `612` polotovarů, `613` výrobků, `614` zvířat (Income).
  - `621`–`624` Aktivace (materiálu a zboží / služeb / DNM / DHM) (Income).
  - `343.100` DPH na vstupu, `343.200` DPH na výstupu (account_type Tax; `343` is now a group).

## What other streams must use (stable)
- **VAT accounts (Stream 2):** `343.100` = na vstupu (input), `343.200` = na výstupu (output).
- **WIP / aktivace (Stream 3):** `611`/`613` for build-to-sell change-in-state (MD 121 / D 611);
  `621`–`624` for aktivace.
- **DIČ = native `tax_id`** on Customer/Supplier/Company (confirmed present — do NOT add a field).
  **IČO = new custom field `cz_ico`** (Stream 1 ships it on Company/Customer/Supplier).
- **Account Category** is a real ERPNext v16 doctype (name + root_type + description). Stream 1
  creates Czech categories and tags every posting account (`Account.account_category`). Stream 3
  builds Financial Report Templates from these categories. Category codes listed below when assigned.

## Rules (unchanged)
- Only Stream 1 edits `hooks.py` and `chart_of_accounts/`. Streams 2 & 3 drop fixture JSON files.
- Commit to your branch; merge via PR in order 1 → 2 → 3. No direct pushes to `main`.

## Verified on the bench (throwaway company)
`apply_czech_coa(company)` builds 314 Czech posting accounts (+ groups), correct root/account
types, all CZK, default receivable/payable wired, immutable ledger on. No errors.

## Account Categories (seam to Stream 3) — LANDED
- **133 Account Category records**, named `CZ-<code>`, shipped as `fixtures/account_category.json`.
  Codes are statement-row slugs: `CZ-rozvaha-aktiva-...`, `CZ-rozvaha-pasiva-...`, `CZ-vzz-...`,
  `CZ-off-...` (off-balance). Every posting account is tagged (`Account.account_category`).
- **Stream 3:** build Financial Report Templates from these categories. Full code→row map is in
  `docs/plans/research/coa-statement-mapping.json` (account_number → rozvaha_row / vzz_row / code);
  narrative + statutory-order category list in `...coa-statement-mapping.md`. The mapping follows
  the **current Decree 500/2002 (post-2016)**, not the older KB scheme.
- **Report-time logic Stream 3 must add** (the category tag alone is not enough): (1) short- vs
  long-term reclassification for 311/321/351/361/462/475… (needs a maturity input); (2) sign-based
  switching for mixed debit/credit accounts (341-347, 343.100/.200, 480/481, 373); (3) the ~55
  ERPNext `x0` group-summary placeholders; (4) the finanční-VZZ podíly-vs-securities split. See
  section 2 of `coa-statement-mapping.md`.

## hooks.py fixtures declared (do not edit hooks.py — Stream 1 owns it)
`Custom Field` + `Property Setter` + `Print Format` (filter: module = Czech Accounting);
`Account Category`, `Financial Report Template`, `Asset Category`, `Finance Book` (filter:
name like `CZ-%`). Use the `CZ-` name prefix for any Czech record in a module-less doctype, and
`module = "Czech Accounting"` on custom fields/property setters, so your fixtures export cleanly.

## Setup entry point
`czech_accounting.setup.coa.apply_czech_coa(company)` (whitelisted) — run on a zero-transaction
company to put it on the Czech chart. `enable_immutable_ledger` is set by a migrate patch.

## Follow-up (non-blocking)
- `set_default_accounts` creates ~2 ERPNext default accounts (tax template / round-off) with no
  CZ category; Stream 2's VAT templates supersede these. May trim later.
- Optional: an unmapped-posting-account validation report.
