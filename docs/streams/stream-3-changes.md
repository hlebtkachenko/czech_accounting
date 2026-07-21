# Stream 3 — change log for other agents

Branch `stream/3-books-assets`. Merges third (after Stream 1 + Stream 2). This file is the
cross-stream summary of what Stream 3 added, what it CONSUMES from Stream 1, and the exact
contract asks Stream 1 must satisfy. Author-only files; no core or Stream 1/2 files edited.

## What Stream 3 built

### Books (three statutory books)
- **Rozvaha** — standard **Script Report** `czech_accounting/report/rozvaha/`. Statutory
  4-column layout **Brutto / Korekce / Netto (běžné) / Netto (minulé)** (Decree 500/2002,
  Příloha 1). Row tree is built at runtime from the live `CZ-rozvaha-*` Account Categories,
  so it tracks Stream 1's taxonomy automatically. Reconciles Aktiva = Pasiva by construction.
- **VZZ druhové** — standard Script Report `czech_accounting/report/vzz_druhove/` (report
  name `VZZ druhove`). By-nature P&L (Příloha 2) over the `CZ-vzz-*` categories, 2 columns
  (běžné / minulé). Bottom line `***` is computed straight from the GL, so it always equals
  Rozvaha row A.V.
- **Účetní deník** — standard Script Report `czech_accounting/report/ucetni_denik/` (report
  name `Ucetni denik`). Chronological journal over `GL Entry` meeting Act 563/1991 § 13:
  evidenční (pořadové) číslo, datum, účet MD/Dal, částka, popis, drill-down to the source
  voucher (Dynamic Link on `voucher_type` → `voucher_no`; the attachment lives on the
  voucher). Total MD = total Dal footer.

Rationale for Script Reports over the native `Financial Report Template`: see
[ADR 0001](../adr/0001-statutory-statements-as-script-reports.md). Short version: the native
engine's columns are periods, so it cannot render the Brutto/Korekce split; Script Reports
also guarantee reconciliation and avoid diacritic auto-export module paths. The Account
Category seam is still consumed READ-ONLY either way.

### Assets & developer inventory
- **Nedokončená výroba** — Script Report `czech_accounting/report/nedokoncena_vyroba/`
  (report name `Nedokoncena vyroba`). The build-to-sell flats' WIP: account 121 balance by
  Project + Cost Center (block/unit analytics). LOCKED decision (00-master §2): the flats are
  inventory, not DHM — costs accumulate in 121 (method A) via Journal Entries carrying a
  Project/Cost Center dimension, then the period-end change-in-state books **MD 121 / D 611**.
  On sale → derecognition from 121. The Rozvaha row C.I.2 and this report both read 121 from
  the GL. Impairment (`MD 559 / D 192`) shows as **Korekce** on C.I.2 automatically (192 is a
  09x/19x/29x/39x correction prefix). No ERPNext Asset doctype is used for the flats.
- **Asset Category fixtures** `fixtures/asset_category.json` — `Automobil` (022, odp. skupina
  2), `Stavby` (021), `Pozemky` (031, `non_depreciable_category=1`). Each depreciable
  category ships two `finance_books` rows (see below). The `accounts` child is intentionally
  empty — the fixed_asset / accumulated_depreciation / depreciation_expense accounts are
  per-Company Account links and must be filled per company at setup (they cannot be a static
  site-wide fixture). Genuine fixed assets use the ERPNext `Asset` flow.
- **Finance Book fixtures** `fixtures/finance_book.json` — `Účetní odpisy` (accounting
  odpisový plán, monthly straight-line) and `Daňové odpisy` (tax, annual). Two parallel
  depreciation books per asset (§ 28 ZÚ vs § 26–33 ZDP).

### Tests
- `czech_accounting/report/rozvaha/test_rozvaha.py` (`IntegrationTestCase`): builds a
  self-contained scenario (capital, construction 501/518 → 121/611 change-in-state, unit-sale
  derecognition, car with oprávky, output VAT) and asserts Rozvaha reconciles (Aktiva =
  Pasiva), Brutto/Korekce/Netto on the 022/082 row, the result lands in A.V and equals the
  VZZ `***` total, the construction is P&L-neutral with 121 carrying the remaining WIP by
  project, and the deník lists chronologically with MD = Dal.

## Account Categories CONSUMED (READ-ONLY, owned by Stream 1)

Stream 3 reads `account_category` on each posting Account. It depends on Stream 1's live
`CZ-rozvaha-*` / `CZ-vzz-*` taxonomy (verified present on the dev site: 100 rozvaha + 31
vzz). Specific hard dependencies:

- Rozvaha result row: **`CZ-rozvaha-pasiva-a-v`** (Výsledek hospodaření běžného období).
- Dual-side tax routing: **`CZ-rozvaha-pasiva-c-ii-8-5`** (Stát – daňové závazky) ↔
  **`CZ-rozvaha-aktiva-c-ii-2-4-3`** (Stát – daňové pohledávky). An account assigned the
  pasiva category is shown as a receivable when its period balance is a net debit.
- WIP: **`CZ-rozvaha-aktiva-c-i-2`** (Nedokončená výroba a polotovary) for account 121.
- VZZ change-in-state: **`CZ-vzz-b`** (Změna stavu zásob vlastní činnosti) for account 611.

**No missing categories identified** — Stream 1's taxonomy is complete for the statements.
The Rozvaha is data-driven, so any category Stream 1 adds later is picked up automatically.
Any account left unmapped surfaces in a visible "Nezařazené účty" row (statement still
reconciles), so misassignments are caught, not hidden.

Brutto/Korekce split relies on **account numbers** (07x/08x oprávky, 09x/19x/29x/39x opravné
položky) being set on accounts — Stream 1 sets these as the join key (00-master §1).

## hooks.py fixture entries Stream 1 must declare

The four reports are `is_standard = "Yes"` and load by module sync on `bench migrate` — they
need **no** fixture entry. Only the two fixture files need declaring, in this order (Finance
Book before Asset Category, because the category links the finance book):

```python
fixtures = [
    # ... Stream 1 + Stream 2 entries ...
    {"dt": "Finance Book", "filters": [["name", "in", ["Účetní odpisy", "Daňové odpisy"]]]},
    {"dt": "Asset Category", "filters": [["name", "in", ["Automobil", "Stavby", "Pozemky"]]]},
]
```

No `Financial Report Template` and no `Report` fixture entries are required from Stream 3.

## Per-company setup (documented, not a fixture)

- Asset Category `accounts` rows (fixed asset / accumulated depreciation / depreciation
  expense per Company) must be filled once per Company after its Czech CoA exists.
- The statutory statements should be run with the accounting Finance Book (`Účetní odpisy`)
  selected, so the daňové book's memo depreciation is excluded from the books.

## Known gaps / accountant sign-off

- Statement layouts are **draft-for-accountant-signoff** (repo invariant) — verify against
  the verbatim Příloha 1/2 forms before real filing use.
- Tax depreciation on `Daňové odpisy` uses ERPNext straight-line as an approximation; Czech
  § 31 rovnoměrné (year-1 ≠ year-2+) and § 32 zrychlené coefficients are not yet implemented
  (Custom API follow-up).
- Real-estate-dev open policy questions (accountant to confirm): land at 031 vs folded into
  121 WIP for resale intent; deductibility of completion/snag reserves. These are CoA/policy
  decisions, out of Stream 3 scope.

## Verification status

Reports compile and load; the reconciliation/WIP/deník test passes on the VPS dev bench.
Full acceptance (auto-depreciation on both Finance Books; 121/611 on the real Czech CoA)
is re-verified after rebasing onto merged Stream 1 + Stream 2 per the merge protocol.
