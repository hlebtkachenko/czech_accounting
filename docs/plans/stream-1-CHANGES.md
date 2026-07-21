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

## Pending on this branch
- Account Category taxonomy + per-account assignment (codes will be listed here).
- `setup/coa.py::apply_czech_coa(company)`; `cz_ico` custom-field fixture;
  `enable_immutable_ledger = 1`; `hooks.py` fixtures skeleton (declares fixture doctypes for all
  three streams — full list posted here once set).
