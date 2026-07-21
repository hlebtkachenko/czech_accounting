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
| `czech_accounting/doc_events.py` | Boundary validators: require DUZP on VAT docs; warn on reverse-charge/supply-type mismatch. Needs a Stream 1 `doc_events` hook. |
| `czech_accounting/test_doc_events.py` | Unit tests for the two validators. |
| `czech_accounting/czech_accounting/print_format/czech_tax_invoice/` | Standard Jinja print format "Czech Tax Invoice" (Sales Invoice daňový doklad): IČ/DIČ, DUZP, VS, PDP "Daň odvede zákazník", CZK VAT on FX invoices. |

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

doc_events = {
    "Sales Invoice": {"validate": "czech_accounting.doc_events.validate_sales_invoice"},
    "Purchase Invoice": {"validate": "czech_accounting.doc_events.validate_purchase_invoice"},
}
```

The `Property Setter` entry is the one to double-check — it carries Stream 2's
naming series. Import on `bench migrate` works via the fixtures glob regardless;
the entries matter for `bench export-fixtures`. The `doc_events` block wires the
Stream 2 boundary validators (`doc_events.py`) — without it the invoices still
work, just unvalidated. The print format syncs automatically from its module
folder on `bench migrate` (no hooks entry needed).

## ⚠ Account decision — synthetic-only (supersedes contract anchors)

Per user directive, Stream 2 uses **synthetic (3-digit) accounts only, no
analyticals**:

| Use | Account |
|---|---|
| VAT (input + output) | **343** (single synthetic) |
| Cash | **211** |
| Bank | **221** |

This **diverges from `00-master.md`** point 1 ("VAT `343.100` / `343.200`", "bank
`221` + `221001`") and point 5 ("minimal analytics 343.100/.200, 221001").

**Stream 1 must align:** create **343, 221, 211 as posting (leaf) synthetic
accounts** — do NOT make 343 a group with 343.100/.200 children, or 221 a group
with 221001, or posting to them fails ("no posting to group account"). The
input/output VAT split is carried by the tax rows, not by separate accounts.
Someone owning the contract should update `00-master.md` to match.

## Depends on Stream 1 (frozen identifiers, verified after Stream 1 merges)

Accounts by number: `343`, `211`, `221` (all posting leaves). The VAT setup looks
these up per company. Run once the CoA exists:

```
bench --site <site> execute czech_accounting.setup.vat_templates.setup_all_companies
```

## Deferred (out of Stream 2 acceptance)

DPH/KH/SH XML export and the normalized VAT-event ledger — later phase (fields
only now). Purchase-side print format (FP is received, not issued). GPC/ABO bank
import format.
