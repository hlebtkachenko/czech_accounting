# Stream 2 — change log (for other streams)

Branch `stream/2-agendas-vat`, off `main`. Merges **after** Stream 1. Live record
of what Stream 2 adds, so Streams 1 and 3 can see the seam without reading the diff.

## Files added (all under Stream 2 ownership)

| File | What |
|---|---|
| `czech_accounting/fixtures/custom_field_document.json` | `cz_` custom fields on the document agendas (below). |
| `czech_accounting/fixtures/naming_series.json` | Property Setters: Czech naming series on Purchase Invoice / Sales Invoice / Payment Entry / Journal Entry. |
| `czech_accounting/setup/vat_templates.py` | Idempotent per-company VAT tax templates + cash/bank Mode of Payment (company-scoped, so not a fixture). |
| `czech_accounting/setup/test_vat_templates.py` | Unit tests: reverse-charge rows net to zero; no 15 %. |
| `czech_accounting/setup/README.md` | Předkontace per agenda + run instructions. |

No edits to `hooks.py`, `chart_of_accounts/`, `report/`, or any Stream 1/3 file.

## Custom fields (frozen `cz_` registry only — no invented names)

| DocType | Fields |
|---|---|
| Purchase Invoice | `cz_duzp`, `cz_date_received`, `cz_vat_supply_type`, `cz_is_reverse_charge`, `cz_kh_section` (B1/B2/B3) |
| Sales Invoice | `cz_duzp`, `cz_vat_supply_type`, `cz_is_reverse_charge`, `cz_kh_section` (A1–A5) |
| Payment Entry | `cz_variable_symbol`, `cz_constant_symbol`, `cz_specific_symbol` |
| Bank Transaction | `cz_variable_symbol`, `cz_constant_symbol`, `cz_specific_symbol` |

Decisions vs the contract:
- `cz_date_received` (datum přijetí) is **Purchase Invoice only** — it is a
  received-invoice concept that drives §73 deduction timing; meaningless on a
  Sales Invoice.
- VS/KS/SS are **payment attributes only** (Payment Entry + Bank Transaction), per
  the LOCKED decision — not put on invoices, even though `erpnext-modeling.md`
  listed them there.
- Dobropis = native `is_return` + `return_against` (no `cz_correction_reason` — not
  in the frozen registry).
- DIČ = native `tax_id`; IČO = `cz_ico` (Stream 1 owns the party fields).

## Naming series (accountant-approved policy)

`FP-.YYYY.-` Purchase Invoice · `FV-.YYYY.-` Sales Invoice · `PO-.YYYY.-` +
`BV-.YYYY.-` Payment Entry (pokladna / banka) · `ID-.YYYY.-` Journal Entry.
Set via Property Setter on `naming_series.options`/`default`. **Replaces** the
default ERPNext series on those doctypes (dedicated Czech site).

## What Stream 1 must add to `hooks.py`

```python
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Czech Accounting"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Czech Accounting"]]},
    # ... your own entries
]
```

The `Property Setter` entry is the one to double-check — it carries Stream 2's
naming series. Import on `bench migrate` works via the fixtures glob regardless;
the entries matter for `bench export-fixtures`.

## Depends on Stream 1 (frozen identifiers, verified after Stream 1 merges)

Accounts by number: `343.100`, `343.200`, `211`, `221001`. The VAT setup looks
these up per company. Run once the CoA exists:

```
bench --site <site> execute czech_accounting.setup.vat_templates.setup_all_companies
```

## Deferred (out of Stream 2 acceptance)

Czech print format (daňový doklad layout) and DPH/KH XML export — later phases.
