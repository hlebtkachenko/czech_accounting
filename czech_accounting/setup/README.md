# Stream 2 setup — VAT templates, cash/bank modes, předkontace

`vat_templates.py` materialises the **company-scoped** Czech VAT config that a
static fixture cannot express (one site, up to 13 companies, per-company `Account`
records). Custom fields and naming series ship as fixtures instead (see
`../fixtures/`).

## Run (after Stream 1 has built a company's chart of accounts)

```
bench --site <site> execute czech_accounting.setup.vat_templates.setup_all_companies
```

Or for one company: `... setup_company_vat --kwargs "{'company': 'ACME s.r.o.'}"`.
Idempotent — safe to re-run; it skips templates that already exist and updates the
Mode of Payment account row in place.

## What it creates per company

Accounts are synthetic-only (3-digit). Input and output VAT both post to the
single synthetic **343**; the input/output split for DPH/KH is carried by the tax
rows, not by separate accounts. Titles are bare (ERPNext's autoname appends the
company abbreviation to the record name):

| Template | Rows | Account |
|---|---|---|
| Sales `DPH 21 %` / `DPH 12 %` | output VAT on net | 343 |
| Sales `DPH 0 % (osvobozeno / vývoz)` | 0 % line | 343 |
| Purchase `DPH 21 %` / `DPH 12 %` | input VAT on net | 343 |
| Purchase `DPH 0 % (osvobozeno / dovoz)` | 0 % line | 343 |
| Purchase `PDP 21 %` / `PDP 12 %` | Add + Deduct on 343, nets to zero | 343 |

Modes of Payment: `Cash` → 211, `Bank` → 221.

Rates are effective-dated (`VAT_RATES_2024_01_01`, Act 349/2023): 21 standard,
12 reduced, since 2024-01-01. No 15 %. No statutory 0 % rate — the "0 %" template
means osvobozeno s nárokem / export / mimo předmět.

## Předkontace per agenda (acceptance reference)

Legend: MD = debit, D = credit. Base (5xx/6xx/311/321/211/221) posts from
ERPNext's native voucher engine (party + item accounts); Stream 2 supplies the
343 VAT rows via the tax templates above.

**Faktura přijatá (Purchase Invoice, `FP-.YYYY.-`)**
- Plátce buyer: `5xx`/`042` + `343` (VAT) / `321` (gross).
- Neplátce buyer: gross to `5xx`/`042` / `321` — no 343.
- Payment: `321` / `221` (or `211`).

**Faktura vydaná (Sales Invoice, `FV-.YYYY.-`)**
- `311` / `6xx` + `343` (VAT).
- Advance received: `221` / `324`, then `324` / `343`; final invoice offsets 324.

**Banka (Bank Transaction → Payment Entry / Reconciliation, `BV-.YYYY.-`)**
- Incoming: `221` / `311` (or `324`).  Outgoing: `321` / `221`.
- Bank fee: `568` / `221` (VAT-exempt).  Interest: `221` / `662`.
- Own-account transfer via transit `261` (zero at month-end).  FX: `563` / `663`.

**Pokladna (Payment Entry, Mode of Payment Cash → 211, `PO-.YYYY.-`)**
- Příjmový: `211` / `6xx` + `343`.  Výdajový: `5xx` + `343` / `211`.
- Cash ↔ bank: Internal Transfer via `261`.

**Interní doklad (Journal Entry, `ID-.YYYY.-`)**
- PDP samovyměření: Add + Deduct on `343` (net zero).
- Aktivace: `042` / `62x`.  Odpisy: `551` / `08x`.  FX, časové rozlišení.
- WIP change of state (build-to-sell): `121` / `611` — bookable via this ID-series
  JE; the WIP valuation / monthly automation is **Stream 3** (assets), not here.

## hooks.py entries Stream 1 must declare (Stream 2 does not edit hooks.py)

```python
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Czech Accounting"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Czech Accounting"]]},
    # ... Stream 1 / Stream 3 entries
]

doc_events = {
    "Sales Invoice": {"validate": "czech_accounting.doc_events.validate_sales_invoice"},
    "Purchase Invoice": {"validate": "czech_accounting.doc_events.validate_purchase_invoice"},
}
```

Custom fields and Property Setters (naming series) **import** on `bench migrate`
via the fixtures-directory glob regardless; these entries are needed so
`bench export-fixtures` re-exports Stream 2's records. The `doc_events` block wires
the boundary validators in `../doc_events.py`. The VAT setup runs by `bench execute`
(or an optional future `Company` `after_insert` doc_event) — it is **not** a
fixture, because tax templates are company-scoped.
