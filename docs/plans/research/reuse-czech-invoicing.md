# Reuse analysis: `ojanovsky/erpnext-czech-invoicing`

Source: https://github.com/ojanovsky/erpnext-czech-invoicing (shallow clone, read-only).
Purpose: mine a personal, UNVERIFIED ERPNext Czech-invoicing app for reusable patterns for our
`czech_accounting` app (Frappe v16 + ERPNext v16.28). Treat as reference only, not a dependency.

## Repo health (verdict: reference-only, do not depend)

| Metric | Value |
|---|---|
| Stars / forks / watchers | 2 / 0 / 2 |
| Open issues | 0 |
| Created | 2019-01-05 |
| Last push (code) | 2022-01-17 |
| Target platform | ERPNext 13 (last commit message `erpnext13_04`) |
| App version | 0.0.3 |
| Repo size | 21 KB |
| License | Intends MIT (README + `hooks.app_license = "MIT"`), but `license.txt` contains only the string `License: MIT` with no license body, so GitHub reports **NOASSERTION**. Legally weak. Reference-only, do not vendor. |
| Publisher | Alarex-Group s.r.o., ondrej.janovsky@alarex.cz |

The whole app is fixtures: Custom Field, Client Script, Translation, Property Setter, and one Print
Format. **No custom DocTypes** (so no parallel-doctype model to conflict with ERPNext natives) and
**no Python business logic** (`mojeapi.py` is a 4-line `return "hello"` placeholder). It covers the
sales side only.

## Feature-by-feature

### 1. Custom fields (symbols, DUZP, IČO/DIČ, dates) — ADAPT (ideas only)

Doctypes touched: Sales Invoice, Sales Invoice Item, Customer, Company (plus junk on Task/Issue).
**No Purchase Invoice fields at all** — the app does faktury vydané only, nothing for faktury přijaté
(so no purchase DUZP, no `cz_date_received` equivalent).

| Field | Doctype | Type | Notes |
|---|---|---|---|
| `vat_date` | Sales Invoice | Date, reqd=1, default `Today`, insert_after `set_posting_time` | = DUZP. Translated cs "Datum zd. plnění". Sits in native namespace (no `cz_` prefix). |
| `company_registration_id` | Customer | Data, insert_after `tax_id` | customer IČO. cs "IČ". |
| `company_registration_id` | Sales Invoice | Data, read_only, `fetch_from customer.company_registration_id` | pulled customer IČO. |
| `registration_id` | Company | Data, insert_after `tax_id` | own IČO. |
| `company2_registration_id` | Sales Invoice | Data, hidden, `fetch_from company.registration_id` | own IČO (awkward `2` name to dodge the customer one). |
| `company_tax_id` | Sales Invoice | Data, hidden, `fetch_from company.tax_id` | own DIČ. **Collides with the ERPNext-native `company_tax_id` docfield on Sales Invoice.** |
| `vat_rate` | Sales Invoice Item | Data (free text), in_list_view | display-only rate, see VAT section. |
| `register_court_record`, `bank_accounts`, `logo` | Company | Small Text / Text Editor / Attach Image | + fetched copies on Sales Invoice. Free-text bank accounts, not linked to Bank Account doctype. |
| `kanban_column` | Task | Select, hidden | UNRELATED leftover cruft. |

- DIČ: customer side correctly uses ERPNext-**native** `tax_id` (matches our plan). Own-company DIČ via a
  custom `company_tax_id` that duplicates the native field — avoid.
- **Symbols (VS/KS/SS): no custom fields at all.** Variabilní symbol is not stored; it is *derived in the
  print format* from the invoice name (`doc.name | replace("FA-","")`) and labeled via a translation
  `Payment ID` -> `Variabilní symbol`. No konstantní and no specifický symbol anywhere.
- This *loosely supports* our position that VS/KS/SS are payment/bank-matching refs rather than statutory
  invoice fields, but their execution is broken (see naming series: the derived VS becomes `2019.0001`,
  with a dot, which is not a valid numeric VS).

Alignment with our plan: our `cz_duzp` = their `vat_date` (same idea, better name). Our
`cz_date_received` + native `bill_no`/`bill_date` have **no counterpart** here (no purchase side). Our
DIČ-via-`tax_id` matches. Our VS/KS/SS-as-payment-attributes is directionally similar but they do it worse.

### 2. VAT / DPH — AVOID

- **No tax templates in fixtures.** No Sales Taxes and Charges Template, no Item Tax Template. The app
  assumes you configure ERPNext tax templates by hand.
- `vat_rate` on Sales Invoice Item is a **free-text Data field**, populated client-side by a JS script
  that `JSON.parse`s `item_tax_rate` and copies the number in. Fragile, display-only, not a real rate.
- Only rate ever referenced is the translation string `VAT 21%` -> `DPH 21%`. So: **not using the
  abolished 15%** (good), but also **no 12%** (the 2024 merged reduced rate) and **no 0%** — it is frozen
  as a single hardcoded 21% label.
- **Reverse charge (přenesená daňová povinnost): not implemented.** The print format merely relabels the
  native `project` field as "Reverse Charge Applicable" — a cosmetic hack with zero §92 accounting, no
  add/deduct rows, no account 343. Our planned net-zero Add+Deduct-on-343 template is strictly better and
  has no analogue here.
- No VAT accounts defined.

### 3. Číselné řady / naming series — AVOID

- Property Setter sets Sales Invoice `naming_series` default to `FA-2019.####` — a **hardcoded literal
  year 2019**, not the dynamic `FA-.YYYY.####`. Frozen in 2019; needs manual editing every year, and it
  poisons the derived variabilní symbol with a dot (`2019.0001`).
- The fixture also rewrites naming series for many unrelated doctypes (Purchase Order `PO-`, Sales Order
  `SO-`, Customer `CUST-`, Purchase Invoice `PINV-`, Payment Entry `PE-`, Item, Supplier, ...). Importing
  this wholesale would clobber our and the site's defaults.

### 4. Print formats — ADAPT (layout cues only)

- One Print Format Builder format "czech invoice", **Sales Invoice only**. Reasonable Czech layout: logo,
  supplier/customer blocks, IČ/DIČ, DUZP ("Datum zd. plnění"), issue date, due date, item table with a
  `vat_rate` column, taxes, grand/rounded total, terms. "- daňový doklad" suffix on non-draft heading.
- Sloppiness: a section literally labeled `efwfwfewfe`; the `project` field shown as reverse charge; a
  `update_billed_amount_in_sales_order` checkbox shown under a "Returns" section.
- **No QR platba / QR code / SPAYD / SWIFT-QR.** No purchase print format.

### 5. DPHDP3 / KH1 / ISDOC / ARES — ABSENT

Zero occurrences of any of these across the whole repo. No DPHDP3 or kontrolní hlášení (KH1) XML export,
no ISDOC generation/import, no ARES lookup. Nothing to reuse; we build these ourselves (our `isdoc` skill
already covers ISDOC 6.0.1 far better).

### 6. Code quality — AVOID as code

Low quality, unmaintained, debug cruft throughout:
- Client Scripts contain `console.log("...ypiiiivapapapa")`, `"YYYYY"`, `"xxx"` debug spam.
- One Client Script binds to `"Sales invoice"` (lowercase `invoice`) — wrong doctype name, so it is dead.
- A Client Script on **Issue** calls `product_issue.product_issue.doctype.product_issues.api.mojefunc`,
  a method from a *different, unrelated app* — copy-paste leftover.
- `mojeapi.py` / `mojefunc` returning `"hello"` — placeholder never removed.
- No custom DocTypes = the one genuine plus: no parallel data model fighting ERPNext natives. The only
  native-namespace risks are the `company_tax_id` collision and prefix-less `vat_date` / `vat_rate`.

---

## Bottom line

### Top 5 reusable patterns (all as IDEAS, re-implement clean)
1. **DUZP as a required Date on Sales Invoice** (`vat_date`, default Today, near posting date) — the core
   idea maps to our `cz_duzp`; keep the `cz_` prefix and add the purchase side.
2. **IČO via a `Data` custom field with `fetch_from party.<ico>` to the invoice, read_only** — clean
   fetch-and-freeze pattern (their `company_registration_id`); reuse the mechanism, drop the `company2_`
   naming hack.
3. **DIČ off the ERPNext-native `tax_id`** for the party (not a new field) — confirms our plan.
4. **Czech print-format skeleton** (heading with "daňový doklad" suffix, IČ/DIČ block, DUZP + due date,
   item table with a rate column, cs translations like "Datum zd. plnění", "Variabilní symbol") — a useful
   layout checklist to copy structurally, not the file.
5. **Treating variabilní symbol as a derived/payment ref, not a statutory invoice field** — directionally
   supports our VS/KS/SS-as-payment-attribute decision (they derive it; we attach it to the payment, which
   is cleaner and avoids their dot-in-VS bug).

### Top 3 things to avoid
1. **The reverse-charge "implementation"** — it is just relabeling the native `project` field; no §92
   accounting, no 343 rows. Our net-zero Add+Deduct-on-343 template is the correct path.
2. **`naming_series = FA-2019.####`** (hardcoded year) and the blanket rewrite of unrelated doctypes' series
   — use dynamic `FA-.YYYY.####` and touch only what we own.
3. **`vat_rate` as free-text Data driven by a client script** and the `company_tax_id` custom field that
   collides with the ERPNext native — model VAT through real tax/item-tax templates and never shadow a
   native fieldname.

### Not present at all (build ourselves)
Purchase-invoice fields, DPHDP3 / KH1 XML, ISDOC, ARES, QR platba, 12% and 0% rates, any tax template.
