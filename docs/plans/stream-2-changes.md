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

Stream 1 shipped the `Custom Field` + `Property Setter` fixtures entries. At merge
Stream 2 added the `doc_events` block to `hooks.py` itself (Stream 1 had not), to
wire the boundary validators. The print format syncs automatically from its module
folder on `bench migrate` (no hooks entry needed).

## Account decision — analytical leaves (resolved at merge)

A synthetic-only variant was tried, but Stream 1's merged chart ships `343` and
`221` as **group** accounts with the analytical leaves `343.100` / `343.200` /
`221001` as the postable children. Posting to a group is rejected, so Stream 2
posts to the leaves — which is the original `00-master.md` contract:

| Use | Account |
|---|---|
| Input VAT | **343.100** (leaf) |
| Output VAT | **343.200** (leaf) |
| Cash | **211** (leaf) |
| Bank | **221001** (leaf) |

Reverse charge = Add 343.200 + Deduct 343.100, so the 343 group nets to zero with
the proper input/output split.

## Depends on Stream 1 (frozen identifiers, verified at merge)

Accounts by number: `343.100`, `343.200`, `211`, `221001` (all posting leaves).
The VAT setup looks these up per company. Run once the CoA exists:

```
bench --site <site> execute czech_accounting.setup.vat_templates.setup_all_companies
```

## Review fixes (thermo-review)

- Tax templates: dropped the manual `" - {abbr}"` title suffix — ERPNext's tax
  autoname already appends it, so names were doubling (`DPH 21 % - ACME - ACME`).
  Titles are now bare; the record name gets one abbr.
- Print format: removed the invoice-level Variabilní symbol cell — it derived a
  letter-prefixed, over-length VS from `doc.name` (`FV202600001`), invalid for a
  Czech VS. VS stays a payment attribute (Payment Entry / Bank Transaction).

## Deferred (out of Stream 2 acceptance)

DPH/KH/SH XML export and the normalized VAT-event ledger — later phase (fields
only now). Purchase-side print format (FP is received, not issued). GPC/ABO bank
import format.
