# Stream 2 — Document agendas & VAT

Branch `stream/2-agendas-vat`. **Merges second** (after Stream 1). Read `00-master.md` first.
Build against the frozen account numbers and field-name registry; you fully verify on the
server only once Stream 1 is merged. Owns only Stream 2 files in the ownership map.

## Goal
The five document agendas working on the Czech chart, with correct předkontace and VAT.
Sources: `research/cz-law-requirements.md` (MD/Dal tables per agenda) and
`research/erpnext-modeling.md` (native doctype per agenda).

## Tasks (one per agenda)
1. **Faktura přijatá → Purchase Invoice.** Custom fields `cz_duzp`, `cz_date_received`,
   `cz_vat_supply_type`, `cz_kh_section`, `cz_is_reverse_charge` (supplier no/date = native
   `bill_no`/`bill_date`; DIČ = `tax_id`; dobropis = `is_return`+`return_against`).
   Předkontace: `5xx`/`042` + `343.100` / `321` (neplátce: gross to cost, no 343). Naming
   `FP-.YYYY.-`.
2. **Faktura vydaná → Sales Invoice.** Same field set. Předkontace `311` / `6xx` + `343.200`;
   zálohy `221`/`324` then `324`/`343.200`. Naming `FV-.YYYY.-`.
3. **Banka → Bank Account + Bank Statement Import → Bank Transaction → Reconciliation.**
   Add `cz_variable_symbol` (+ KS/SS) to Bank Transaction for auto-match. Cash-vs-bank = the
   GL account (`221` vs `211`). Core předkontace `221`/`261`, `221`/`311`, `321`/`221`,
   `568`/`221` (fee), FX `563`/`663`; transit via `261` (zero at month-end). Naming `BV-.YYYY.-`.
4. **Pokladna → Payment Entry + Mode of Payment "Cash" → 211.** Receive = příjmový, pay =
   výdajový; cash↔bank = Internal Transfer via `261`. Předkontace příjmový `211`/`6xx`+343,
   výdajový `5xx`+343/`211`. Naming `PO-.YYYY.-`. (Not Journal Entry.)
5. **Interní doklad → Journal Entry** with `voucher_type` + naming `ID-.YYYY.-`. Covers
   samovyměření (`343.100`/`343.200`), odpisy posting, aktivace (`042`/`62x`), FX, časové
   rozlišení. (Asset depreciation *config* is Stream 3; the JE series is here.)

## VAT (payer)
- Sales/Purchase Taxes and Charges Templates for **21 / 12 / 0** referencing `343.100`/`.200`
  from Stream 1. (Rates are effective-dated: 21 standard, 12 reduced, since 2024-01-01. Never 15.)
- **Reverse charge (přenesená daňová povinnost):** Purchase template with Add+Deduct rows on
  343 that net to zero — the native ERPNext lever. Drive it from `cz_is_reverse_charge`.
- Classification fields (`cz_vat_supply_type`, `cz_kh_section`) populate for later KH1/DPHDP3.
  **Fields only now — no XML.**

## Depends on (contract)
Account numbers (`343.100/.200`, `211`, `221`, `311`, `321`, `261`, `5xx`, `6xx`), the `cz_`
field registry, and the fixtures skeleton in hooks.py — all from Stream 1.

## Acceptance
- On a test company (post Stream-1 merge), draft a FP, FV, pokladní doklad, bank line, and
  interní doklad; each posts the expected předkontace and computes VAT.
- A reverse-charge purchase nets to zero on 343.
- Documents are draft-only until a human submits; naming series apply.

## Reuse review
Skim `research/reuse-czech-invoicing.md` (ojanovsky) — adopt any clean field/print-format
ideas, reject outdated VAT (15%) or native-conflicting doctypes. Trust nothing unverified.
