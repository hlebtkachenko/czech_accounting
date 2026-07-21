# Stream 3 — Books, statements & assets

Branch `stream/3-books-assets`. **Merges third.** Read `00-master.md` first. Consume the
Account Category taxonomy from Stream 1 (read-only here). Owns only Stream 3 files.

## Goal
The three statutory books and the asset/odpisy configuration. Sources:
`research/cz-law-requirements.md` (statement rows, depreciation) and
`research/erpnext-modeling.md` (native mechanisms).

## Books
1. **Rozvaha.** Build a v16 `Financial Report Template` mapping Account Categories → statutory
   rows (Decree 500/2002 Příloha 1). Target the filing layout: **Brutto / Korekce / Netto /
   Minulé období** (4 columns). The native template gives management BS cheaply; the 4-column
   statutory layout likely needs a Custom API / custom report row builder — scope that.
2. **VZZ druhové.** Financial Report Template from categories → Příloha 2 (by-nature) rows.
3. **Účetní deník.** Query/Script Report over General Ledger ordered chronologically, meeting
   §13 (evidenční číslo, datum, MD/Dal účet, částka, popis). Reuse GL data; thin report on top.
   Add drill-down from rows to the source voucher + attachment.

## Assets & developer inventory
LOCKED: the self-built flats are **build-to-SELL → inventory, not DHM**. Keep the two paths
strictly separate.

4. **Developer WIP inventory (the flats — the main case).** Construction costs accumulate in
   `121` Nedokončená výroba, **method A (způsob A)**: costs hit class-5 (`501` material, `518`
   subcontractors/design, `521` own wages, `551` own-equipment depreciation) as incurred, then
   at period-end book the change-in-state **MD `121` / D `611`** (`611` = změna stavu, a Class-6
   výnosový account — the net P&L effect of construction within the period is zero). Value at
   vlastní náklady (direct material + labor + production overhead; NOT admin/selling costs). On
   unit sale → `132` / derecognition. Model via **Journal Entries** (the deník series) with a
   **Project / Cost Center dimension** so `121` carries analytics by project/block/unit. This is
   inventory accounting — do NOT use the ERPNext Asset doctype for the flats. Land acquired for
   the development is project inventory, not `031`.
5. **Genuine fixed assets (secondary).** Only real DHM uses the ERPNext `Asset` + `Asset
   Category` flow: automobil → `022`, odpisová skupina 2; any own-use/long-held property →
   `021`/`031` (land `031` depreciation disabled). Not the developed flats.
6. **Účetní vs daňové odpisy** (for the fixed assets, e.g. auto). Two `Finance Book`s (native
   parallel schedules): accounting odpisový plán + tax odpisové skupiny (zákon o daních z příjmů).
7. **Trial balance + reconciliation checks** feeding the statements.

## Depends on (contract)
The Account Category codes from Stream 1 (the seam), account numbers, and the fixtures
skeleton. If a category is missing for a needed row, request it from Stream 1 — do not add
accounts or categories here.

## Acceptance
- Rozvaha and VZZ render the statutory layout and reconcile to the trial balance
  (debit = credit; opening + turnover = closing per account).
- Účetní deník lists all entries chronologically with §13 content and drill-down.
- Construction costs accumulate in `121` and the period-end change-in-state books `MD 121 /
  D 611`; a unit sale derecognizes from inventory. An automobile (fixed asset) depreciates on
  both Finance Books.
- Accountant sign-off on statement layouts before real use.

## Reuse review
Skim `research/reuse-assistant-core.md` only if touching any automation; core statements are
manual. Trust nothing unverified.
