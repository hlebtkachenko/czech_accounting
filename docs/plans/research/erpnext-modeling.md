# Modeling Czech Bookkeeping in ERPNext v16 with Minimal Custom Code

Scope: Frappe 16.27.1 + ERPNext 16.28.0. App `czech_accounting` (extension, not fork).
VAT payer, double-entry, solo accountant, up to 13 client companies (one Company per client).
Verdict legend: **REUSE** = built-in, config only. **EXTEND** = Custom Field, hook, fixture, or
configured template. **BUILD** = new DocType or report.
Source basis: repo KB `docs/knowledge-base/` (source-verified at ERPNext commit
`de591661...`, v16.28.0) plus ERPNext v16 official docs (Financial Report Template, Account
Category, Asset Capitalization, Finance Book) confirmed via context7 / docs.frappe.io on 2026-07-21.
This is an engineering model, not a Czech compliance claim. Statutory outputs stay effective-dated
and gated on accountant sign-off (per `AGENTS.md`).

---

## What ERPNext already gives us for free (do NOT rebuild)

- **Double-entry engine and the single write path.** Every voucher builds a GL map and posts
  through `erpnext.accounts.general_ledger.make_gl_entries`, which does period/freeze/dimension/
  balance validation and Payment Ledger creation. Never insert `GL Entry` directly; never build a
  parallel Czech ledger. All Czech reports read the same GL rows.
- **All five document agendas exist as first-class vouchers:** Purchase Invoice, Sales Invoice,
  Payment Entry, Journal Entry, plus Bank Account / Bank Transaction / Bank Reconciliation Tool.
- **Per-Company chart of accounts** with account number, `account_type`, `root_type`, group flag,
  NestedSet tree, and "no posting to group account" enforced in core.
- **Financial statements are now template-driven in v16.** `Financial Report Template` (types
  Balance Sheet / Profit & Loss / Cash Flow / Custom) with `Financial Report Row` children maps
  rows to accounts via **`Account Category`** (a v16 classification layer), reference codes,
  formulas, and Custom API rows. This is exactly the "explicit report classification, not account
  names" that the KB demanded, and it ships natively. Rozvaha and VZZ become configuration, not a
  from-scratch report.
- **General Ledger, Trial Balance, AR/AP, ageing** reports out of the box, all ledger-derived and
  reconcilable.
- **Fixed assets:** `Asset`, `Asset Category`, depreciation schedules, **CWIP** (Capital Work in
  Progress) accounting toggle, **Asset Capitalization** (composite / self-constructed assets), and
  **Finance Book** for parallel depreciation books (accounting vs tax).
- **Tax engine:** Sales / Purchase Taxes and Charges Templates, Item Tax Templates, tax rows with
  `charge_type` and an **Add / Deduct** flag (the lever for reverse-charge net-zero), Tax Rules.
- **Cash vs bank** is modeled purely by the GL account behind a `Mode of Payment`
  (Cash 211 vs Bank 221); Payment Entry handles receive/pay/internal-transfer.
- **Fiscal Year, Accounting Period locks, Company freeze date, Period Closing Voucher** for the
  time/close controls.
- **Naming Series** on every voucher for Czech document number series.
- **Data Import + REST + Bank Statement Import** for draft-first ingestion; Version log and
  cancellation/repost lifecycle for audit.

The genuinely new-build surface is narrow: the Czech CoA + Account Category mapping (data), the
statutory-format statements and books as *filing artifacts*, the DPH/KH VAT-event layer + XML, and
the assisted-entry batch API. Everything else is REUSE or EXTEND.

---

## 1. Document agendas

| # | Item | ERPNext mechanism | Verdict | Custom fields / hooks / reports | Notes / risks |
|---|---|---|---|---|---|
| 1 | **Faktura přijatá** | `Purchase Invoice`. Supplier doc number and date already exist as `bill_no` + `bill_date`; supplier DIČ = `tax_id` on Supplier; posting/due dates native. | REUSE + EXTEND | Custom Fields: `cz_duzp` (Date, tax point / DUZP, distinct from `posting_date`), `cz_date_received` (Date, datum doručení), `cz_variable_symbol`, `cz_constant_symbol`, `cz_specific_symbol`. IČO on Supplier: `cz_ico`. Corrective doc (opravný daňový doklad) = native credit note: `is_return=1` + `return_against` -> original PI; add `cz_correction_reason`. VAT-classification fields shared with §12. | `bill_no`/`bill_date` cover supplier evidential number, do not duplicate. Extend via Custom Field + fixture; export with `bench export-fixtures`. Namespace fieldnames (`cz_`) to avoid upstream collision (per extension-decision-guide). Any GL-map effect must be deterministic on repost, not just `on_submit`. |
| 2 | **Faktura vydaná** | `Sales Invoice`. Customer DIČ = `tax_id`; invoice `name`/naming series = evidential number and usual variabilní symbol. | REUSE + EXTEND | Same Custom Field set as row 1 on Sales Invoice: `cz_duzp`, `cz_variable_symbol` (often = invoice no.), `cz_constant_symbol`, `cz_specific_symbol`; `cz_ico` on Customer. Corrective/credit: `is_return` + `return_against` + `cz_correction_reason`. | VS usually equals the invoice number; keep an explicit field so payment matching is not name-parsing. Simplified tax doc (≤ CZK 10,000) is a print/validation concern, not a schema one. |
| 3 | **Banka (bankovní výpis)** | `Bank Account` (points to a Bank-type GL account, e.g. 221) + `Bank Statement Import` -> `Bank Transaction` -> **`Bank Reconciliation Tool`** matches transactions to `Payment Entry` / `Journal Entry`. Cash-vs-bank = which GL account (221 vs 211). | REUSE + EXTEND | Custom Fields on Bank Transaction for VS/KS/SS carried from the statement (`cz_variable_symbol` etc.) to drive auto-match on variabilní symbol. Optional import-format mapping for Czech bank CSV/ABO-GPC. | Bank Transaction is the raw statement line; Payment Entry/JE is the posting. VS-based matching is the main Czech-specific ergonomic gap. GPC/ABO format parsing (if used) is a small BUILD (a Bank Statement Import variant or preprocessor). |
| 4 | **Pokladna (pokladní doklad)** | `Payment Entry` with `Mode of Payment` = Cash, mapped per Company to cash account **211**. Receive = příjmový, Pay = výdajový. Cash deposit to bank = Payment Entry type **Internal Transfer** (211 -> 221). | REUSE + EXTEND | Configure Mode of Payment "Cash" -> account 211 per Company (Mode of Payment `accounts` child table). Custom naming series `cz_cash_receipt`/`cz_cash_payment` (or one PDPnnn series). No new DocType. | Prefer Payment Entry over Journal Entry: it owns party, outstanding, and Payment Ledger semantics. Only use a Journal Entry (voucher_type Cash Entry) for cash movements with no party. Cash vs bank is purely the account behind the Mode of Payment, so nothing structural is needed. |
| 5 | **Interní doklad** | `Journal Entry` (has `voucher_type`: Journal Entry / Bank Entry / Cash Entry / etc.) + `naming_series`. | REUSE + EXTEND | Custom naming series (e.g. `ID-.YYYY.-`) and, if wanted, a `cz_document_kind` select. Balanced multi-account adjustments only. | JE is the right home for accruals, reclasses, opening entries, depreciation postings not auto-made, and reverse-charge self-assessment where a template is not used. Do not push invoices/payments through JE (loses party/tax/outstanding meaning) - explicit KB failure mode. |

---

## 2. Books / reports

| # | Item | ERPNext mechanism | Verdict | Custom fields / hooks / reports | Notes / risks |
|---|---|---|---|---|---|
| 6 | **Rozvaha (balance sheet)** | v16 **`Financial Report Template`** (type Balance Sheet) with `Financial Report Row` children mapping accounts via **`Account Category`**, reference codes, and formulas. Built-in Balance Sheet report also exists (root_type + tree). | EXTEND (config/fixtures), not BUILD | Fixtures: Czech `Account Category` set + a "Rozvaha (Decree 500/2002, Annex 1)" Financial Report Template mapping each category to a statutory line, effective-dated. Map every posting account to a category as part of the Czech CoA (Phase A/B). | Big win: no bespoke report engine needed for the management-level statement. **Risk:** the Czech statutory balance sheet has Brutto / Korekce / Netto (běžné období) + Netto (minulé období) columns; whether Financial Report Template renders that 4-column brutto/korekce shape natively is unconfirmed - a `Custom API` row or a thin custom column layer may be needed for the *filing* format. Treat the legal PDF/XML (Sbírka listin) as a later, separate artifact. |
| 7 | **Výkaz zisku a ztráty (druhové členění)** | Same `Financial Report Template` (type Profit & Loss), rows by Account Category. | EXTEND (config/fixtures) | Fixture: "VZZ druhové (Annex 2)" template mapping revenue/expense categories (účtové třídy 5/6) to statutory lines; effective-dated. | Druhové (by-nature) layout maps cleanly to class-5/class-6 account categories, easier than účelové. Same filing-format caveat as row 6 for the official structured output. |
| 8 | **Účetní deník (chronological journal)** | Built-in **General Ledger** report reads `GL Entry` by Company/date, ordered by posting date; is the chronological source. | REUSE for data, thin BUILD for statutory output | New **Query/Script Report** "Účetní deník" over GL Entry: continuous ordering, per-voucher grouping, and completeness reconciliation (§13). Reuse GL rows, store nothing. Companion **Hlavní kniha** (General Ledger by account) already close to built-in GL/Trial Balance. | KB is explicit: the raw GL UI is not the complete statutory book (§11-§13 need ordering + completeness reconciliation and opening/monthly-turnover/closing per synthetic account). So: reuse the ledger data, add a small report for statutory presentation. No second ledger store. Every report subtotal must reconcile to Trial Balance / GL control totals. |

---

## 3. Assets

| # | Item | ERPNext mechanism | Verdict | Custom fields / hooks / reports | Notes / risks |
|---|---|---|---|---|---|
| 9 | **Fixed assets: automobil (022), pozemek (031, non-depreciating), byty/stavby (021)** | `Asset` + `Asset Category` + depreciation schedule. Non-depreciating land = Asset (or plain account balance) with **"Calculate Depreciation" unchecked** -> no schedule generated. | REUSE (config) | Asset Categories: "Stavby" (021), "Samostatné movité věci / Automobil" (022), "Pozemky" (031, depreciation off). Each category's Accounting Details map Fixed Asset / Accumulated Depreciation / Depreciation Expense accounts to the Czech CoA. | Land (031): simplest is an Asset with depreciation disabled, or just carry it as an account balance if no asset register entry is needed - decide per client. `account_type` "Fixed Asset" / "Accumulated Depreciation" / "Depreciation" already exist in core. |
| 10 | **Self-constructed assets (byty vybudované námi)** | `Asset Category` -> **"Enable Capital Work in Progress Accounting"** posts in-build costs to a **CWIP** account; **`Asset Capitalization`** DocType combines consumed items/assets/services into the target asset, then capitalizes (CWIP credited, Fixed Asset debited). | REUSE (config) | Map the category CWIP account to Czech **042** (Nedokončený dlouhodobý hmotný majetek); on capitalization it moves to 021/022. No custom code. | Confirmed v16: submitting an asset/receipt with CWIP on debits CWIP; capitalization moves CWIP -> Fixed Asset. Watch the scheduler-posted entry when "available for use" is a future date. Validate the exact GL rows on a disposable site before trusting the 042 mapping. |
| 11 | **Účetní vs daňové odpisy (parallel depreciation)** | **`Finance Book`**: an Asset can carry multiple depreciation schedules, one per Finance Book, with independent method/rate/life. One book = accounting (účetní), one = tax (daňové). Reports and postings filter by Finance Book. | REUSE (config) | Two Finance Books ("Účetní", "Daňové"). Accounting book posts to GL; tax book is memo/reporting for the daňová evidence and the deferred-tax difference. Optional report: účetní vs daňové odpis reconciliation + deferred tax base (481). | Core supports parallel books natively (confirmed via docs). **Risk / decision:** which book posts to the ledger vs which is report-only, and how the accounting/tax difference feeds odložená daň (481) - an accounting-policy decision, not a code gap. Czech tax depreciation is group-based (rovnoměrné/zrychlené per §31/§32 ZDP); ERPNext methods may need a Custom API depreciation or a periodic override for the tax book. |

---

## 4. VAT / DPH

| # | Item | ERPNext mechanism | Verdict | Custom fields / hooks / reports | Notes / risks |
|---|---|---|---|---|---|
| 12 | **VAT accounts, rates, templates** | `Sales/Purchase Taxes and Charges Template` per rate/regime; `Item Tax Template` for per-item rate override; VAT booked to **343** (account_type "Tax"). | REUSE (config/fixtures) | Effective-dated Templates: 21 % / 12 % / 0 % / exempt / out-of-scope, both sales and purchase. Item Tax Templates for reduced-rate items. All output/input VAT to 343 sub-accounts. | Tax percentage is calculation only; it is NOT the legal classification (KB failure mode). Keep templates effective-dated. |
| 12a | **Reverse charge / self-assessment (přenesená daňová povinnost, EU acquisitions, import)** | Purchase Taxes and Charges Template with two rows on 343: one **Add** (output VAT) + one **Deduct** (input VAT), net cash effect zero, both VAT events recorded. The row **Add/Deduct** flag is the native lever. | REUSE (config) + EXTEND (classification) | Reverse-charge templates per regime (§92a domestic PDP, EU acquisition, import). Classification fields (below) drive later KH1/DPHDP3 section codes. | No native Czech reverse-charge switch; the Add+Deduct net-zero template is the standard ERPNext pattern and is sufficient for the GL. The *filing* meaning lives in the classification fields, not the template. |
| 12b | **Classification fields for later KH1 / DPHDP3 (fields only, XML is Phase D)** | Custom Fields on Sales/Purchase Invoice feeding a normalized VAT-event layer. | EXTEND | Custom Fields: `cz_vat_supply_type` (Select: domestic / EU / third-country / reverse-charge / exempt / out-of-scope), `cz_kh_section` (Select: A1/A2/A4/A5/B1/B2/B3), `cz_is_reverse_charge` (Check), `cz_duzp` (reused from §1/§2), `cz_vat_return_period` (derived). Counterparty DIČ = `tax_id` (reuse); IČO = `cz_ico`. | KB is explicit: DPHDP3/KH1/VIES must derive from a normalized, reconciled **VAT-event ledger**, not from invoice layout. This task delivers the *fields*; the event layer + XML generator + XSD validation are the separate **Phase D BUILD**. Preserve exact VAT ID formatting and evidential number - KH matching depends on source identity. VAT amount stated in CZK even for FX invoices (VAT Act §29(1)(l)). |

---

## Cross-cutting custom fields (one inventory, reused across agendas)

Author as Custom Fields in the app, export via `bench export-fixtures --app czech_accounting`,
re-imported on `bench migrate`. Namespace `cz_` to avoid future upstream collisions (per
extension-decision-guide). All are stored fields unless noted.

- **Party identity:** `cz_ico` on Company / Customer / Supplier (IČO). DIČ reuses core `tax_id`.
- **Czech payment symbols:** `cz_variable_symbol`, `cz_constant_symbol`, `cz_specific_symbol` on
  Sales Invoice, Purchase Invoice, Payment Entry, Bank Transaction, Journal Entry.
- **Dates:** `cz_duzp` (tax point / DUZP) and `cz_date_received` on Sales/Purchase Invoice.
- **VAT classification:** `cz_vat_supply_type`, `cz_kh_section`, `cz_is_reverse_charge` on
  Sales/Purchase Invoice.
- **Corrections:** reuse core `is_return` + `return_against`; add `cz_correction_reason`.
- **Account classification:** use the native v16 `Account Category` (fixtures), not a custom field,
  to map posting accounts to statement lines.

Hooks: prefer `doc_events` (validate/on_submit) for boundary validation (e.g. reject unmapped
posting account, require `cz_duzp` on VAT invoices), `extend_doctype_class` only if reusable
methods are needed. Avoid `override_doctype_class`. Any GL-affecting logic must behave identically
on submit and on repost.

---

## The 3-4 biggest BUILD efforts (everything else is REUSE/EXTEND)

1. **Czech Chart of Accounts template + Account Category mapping (Phase A).** Data/fixtures, not
   code, but it is the largest and blocking deliverable: full class 0-7 tree from Decree 500/2002
   Annex 4, ERPNext account types, and every leaf mapped to an Account Category so the statements
   work. A Company's CoA is fixed at creation, so this must exist first.
2. **DPH / VAT-event layer + XML (DPHDP3, DPHKH1, DPHSHV) - Phase D.** The one true from-scratch
   engine: a normalized, effective-dated tax-event ledger derived from submitted/corrected vouchers,
   reconciled to GL 343, plus versioned XSD-validated XML generators and filing-snapshot records.
   This task delivers only the classification *fields*; the ledger + XML is the build.
3. **Statutory statements and books as filing artifacts.** Management Rozvaha/VZZ are config on
   Financial Report Template (cheap). The *legal* outputs - Rozvaha with Brutto/Korekce/Netto,
   VZZ structured form, Účetní deník / Hlavní kniha with §13 completeness reconciliation, and the
   Sbírka listin submission format - are custom reports / Custom API rows on top.
4. **Assisted-entry batch API (Phase F).** Whitelisted, idempotent, draft-only staging + import
   methods for the scoped agent user (dedup by content hash, batch id, parser version). Plus the
   ISDOC/ARES integrations (Phase E). Not an accounting-model gap, but real net-new code.

Supporting caveats: bank GPC/ABO import mapping (small), tax-book depreciation method for §31/§32
ZDP (possible Custom API on the Finance Book schedule), and the immutable-ledger setting decision
(`enable_immutable_ledger` defaults to 0 in v16.28.0 - decide deliberately after Czech review, it
changes cancellation/correction behavior).
