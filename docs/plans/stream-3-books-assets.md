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

## Assets
4. **Asset Categories.** automobil → `022`, odpisová skupina 2; pozemek → `031`, **depreciation
   disabled** (land is not depreciated); byty/stavby → `021`. Map each to its accounts.
5. **Self-built byty (build-to-own default).** Model via CWIP account `042` (Asset Category
   CWIP toggle) + `Asset Capitalization` to activate to `021`. Capitalize own construction
   costs (`042`/`624`). [If build-to-sell is chosen instead: inventory `121`/`611` — coordinate
   with the master decision.]
6. **Účetní vs daňové odpisy.** Two `Finance Book`s (native parallel depreciation schedules):
   one accounting (odpisový plán), one tax (odpisové skupiny per zákon o daních z příjmů).
7. **Trial balance + reconciliation checks** feeding the statements.

## Depends on (contract)
The Account Category codes from Stream 1 (the seam), account numbers, and the fixtures
skeleton. If a category is missing for a needed row, request it from Stream 1 — do not add
accounts or categories here.

## Acceptance
- Rozvaha and VZZ render the statutory layout and reconcile to the trial balance
  (debit = credit; opening + turnover = closing per account).
- Účetní deník lists all entries chronologically with §13 content and drill-down.
- An automobile asset depreciates on both Finance Books; a self-built byt capitalizes via
  `042` → `021`; a pozemek does not depreciate.
- Accountant sign-off on statement layouts before real use.

## Reuse review
Skim `research/reuse-assistant-core.md` only if touching any automation; core statements are
manual. Trust nothing unverified.
