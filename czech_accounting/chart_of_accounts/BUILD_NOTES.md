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

## Remaining Stream 1 tasks
1. Augment the chart: add 61x/62x, the 343 analytics, `221001` (present), pending sign-off.
2. Account Category taxonomy + assign every posting account (seam to Stream 3; use the KB
   `90-meta/INDEX-by-rozvaha-row.md` / `INDEX-by-vzz-row.md` mappings).
3. `czech_accounting/setup/coa.py::apply_czech_coa(company)` — validate zero-GL, then
   `create_charts(company, custom_chart=load_cz_chart())`. Idempotent.
4. Party custom fields (`cz_ico` on Company/Customer/Supplier); confirm `tax_id` = DIČ.
5. `enable_immutable_ledger = 1` (Accounts Settings) via patch/after_install.
6. `hooks.py` fixtures skeleton covering all three streams' fixture doctypes.
7. Validation: no posting to group; unmapped-posting-account report; every posting account
   has an Account Category.

## Verify
Create a throwaway company on the VPS (`bench console`), run `apply_czech_coa`, count accounts,
run the category-completeness check, then delete it. Accountant sign-off gates real use.
