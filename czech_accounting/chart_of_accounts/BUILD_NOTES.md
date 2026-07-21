# Czech CoA — build notes (Stream 1)

`cz_coa.json` is generated from `docs/plans/research/coa-normalized.json` by
`scripts/build_cz_coa.py`. It targets ERPNext's `create_charts(company, custom_chart=<tree>)`:
top-level keys are the five root_type groups; Czech classes nest under the root matching each
account's own root_type (classes 2/3/4 are split across roots). Current output: 5 roots,
73 group nodes, 305 posting accounts.

## Gaps found by the transform (fix before sign-off)
- **Missing group 61 — Změna stavu zásob vlastní činnosti (611–614).** REQUIRED: `611`
  (nedokončená výroba) and `613` (výrobky) drive the build-to-sell developer WIP change-in-state
  (MD 121 / D 611). The client's source chart omits the whole 61 group. Add it (výnosový/Income).
- **Missing group 62 — Aktivace (621–624).** Needed for capitalizing own work. Add (Income).
- **343 DPH** is a single Liability synthetic. Add analytics `343.100` (na vstupu) /
  `343.200` (na výstupu) per the contract.
- **Class 7** closing/off-balance accounts fall back to the Equity root — review with the
  accountant (no clean ERPNext root).
- Minor: source carries `600/640/660/690` header-level synthetics (non-standard); review.

## Stream 1 status — DONE (verified on the bench)
1. [x] Augment chart: 61x/62x + 343.100/.200 added; 221001 present. (Sign-off still pending.)
2. [x] Account Category taxonomy: 133 `CZ-` categories, every posting account tagged.
3. [x] `setup/coa.py::apply_czech_coa(company)` — zero-GL guard + ERPNext reset + create_charts.
4. [x] `cz_ico` custom field on Company/Customer/Supplier; DIČ = native `tax_id`.
5. [x] `enable_immutable_ledger = 1` via migrate patch.
6. [x] `hooks.py` fixtures skeleton (all three streams).

Follow-up (non-blocking): `set_default_accounts` leaves ~2 ERPNext default accounts uncategorized
(Stream 2 VAT templates supersede); optional unmapped-posting-account report. No-posting-to-group
is enforced natively by ERPNext.

## Review (advisory, not a blocking gate)
The chart, the added accounts, and the statement-row mapping are worth an accountant eye, but
the hard control is draft-only posting (`docstatus = 0`, human submits) — no sign-off gate.

## Verify
Create a throwaway company on the VPS (`bench console`), run `apply_czech_coa`, count accounts,
run the category-completeness check, then delete it. Accountant sign-off gates real use.
