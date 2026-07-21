# Audit fixes — closing the Advisor's 3 gaps

Branch `fix/audit-gaps`. Closes the DONE-WITH-GAPS findings from the completeness audit.

## Gap 1 — real Czech tax depreciation (was straight-line)
- `czech_accounting/assets/tax_depreciation.py`: statutory **§ 31 rovnoměrné** (year-1 rate ≠
  year-2+) and **§ 32 zrychlené** (k1/k2), rates/coefficients per Annex 1, Act 586/1992.
  Pure + unit-tested (`test_tax_depreciation`, 7 tests: matches the KB worked examples, sums
  to cost, never a straight line).
- `cz_tax_group` + `cz_tax_method` custom fields on Asset Category.
- `czech_accounting/assets/cz_ads.py::apply_czech_tax_depreciation(asset)`: rewrites the
  **CZ-Daňové odpisy** schedule with the statutory amounts. ERPNext rebuilds the schedule
  through the whole submit lifecycle, so this must run against the committed, finalised
  schedule — wired on Asset `on_submit` via `enqueue_after_commit`. Idempotent. Verified
  manually on a committed asset (group-2 car, 300k → `[33000, 66750, 66750, 66750, 66750]`).
  Daňové odpisy are a parallel tax calc (tax return + deferred tax 592/481), not a GL posting;
  the CZ-Účetní odpisy book still posts účetní odpisy to 551/08x.

## Gap 2 — end-to-end agenda posting proof
- `test_faktura_vydana.py`: drafts + submits a Sales Invoice with Czech 21 % output VAT and
  asserts the GL předkontace **311 (debtor) / 602 (revenue) + 343 (DPH výstup)**, balanced.
  Also exercises Stream 2's DUZP validation (the invoice is rejected without `cz_duzp`).

## Gap 3 — unmapped-posting-account report
- `report/nezarazene_ucty/` (Script Report **Nezařazené účty**): lists posting accounts with no
  `CZ-` statement category, so chart drift is caught before it corrupts a statement. Tested.

## Minor
- Fixed the stale `fixtures/asset_category.json` reference in the asset test docstring.

## Test suite
27 pass, 0 fail (8 integration + 19 unit) on the dev bench.
