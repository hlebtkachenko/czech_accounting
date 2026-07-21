# Using the statutory books, developer WIP, and assets (Stream 3)

Practical guide to the reports and fixtures Stream 3 adds: the three statutory books
(Rozvaha, VZZ druhové, Účetní deník), the developer WIP (účet 121) workflow, and the fixed
asset / dual-odpisy setup. For the design rationale see
[ADR 0001](../adr/0001-statutory-statements-as-script-reports.md) and the change log in
[docs/streams/stream-3-changes.md](../streams/stream-3-changes.md).

All statutory outputs are **draft-for-accountant-signoff** — verify the layout against the
Decree 500/2002 Sb. forms before any real filing use.

---

## 1. Prerequisites (once per site / per company)

1. **Apply the code** (this app is authored as files; the server only runs it):
   ```
   git pull
   bench --site <site> migrate
   bench --site <site> clear-cache
   ```
   `migrate` syncs the four reports (they are standard reports, no fixture entry needed) and,
   once Stream 1 declares them in `hooks.py`, imports the Finance Book + Asset Category fixtures.
2. **Account Categories assigned (Stream 1).** Every posting account must carry an
   `account_category` from the `CZ-rozvaha-*` / `CZ-vzz-*` taxonomy, and its **account number**
   must be set (07x/08x/09x… drive the Brutto/Korekce split). Stream 3 consumes these
   read-only; it never assigns them.
3. **Per-company Finance Book default.** On the Company, set **Default Finance Book =
   `Účetní odpisy`**. The statutory statements fall back to this when no book is chosen, so the
   účetní and daňové depreciation books are not summed together.
4. **Per-company Asset Category accounts.** Open each shipped Asset Category (Automobil, Stavby,
   Pozemky) and, in the **Accounts** table, add a row for the company with its
   fixed-asset / accumulated-depreciation / depreciation-expense accounts (022/082/551 etc.).
   The fixtures ship the categories and the two finance-book schedules but not these
   company-specific account links.

---

## 2. The three books

Open each from **Accounting > reports** (search the report name). Common filters: **Company**
(required), **To Date** (required), **Finance Book** (optional; defaults to the company book).

### Rozvaha (balance sheet, 4 columns)
- Columns: **Brutto / Korekce / Netto (běžné) / Netto (minulé)**. Brutto/Korekce are shown on
  the Aktiva side only; Netto = Brutto + Korekce. Korekce holds oprávky (07x/08x) and opravné
  položky (091–096, 098, 19x, 291, 391).
- **Minulé období** defaults to one year before To Date; override with **Previous Period End**.
- **Show Zero Rows** reveals the full statutory skeleton (all mandated lines, including empty
  ones); off by default for readability.
- The period result (zisk/ztráta) is computed from the fiscal-year movement of class 5/6 and
  shown on row **A.V**; it always equals the VZZ bottom line.
- **Reconciliation:** AKTIVA CELKEM Netto must equal PASIVA CELKEM Netto. If they differ a red
  **KONTROLA** row appears with the difference — investigate before trusting the statement.

### VZZ druhové (profit & loss, by nature)
- Columns: **Běžné období / Minulé období**. Rows follow Příloha 2. Costs are shown positive,
  revenues positive; the intermediate `*` (provozní) and `**` (finanční) results and the `***`
  bottom line are computed so that `***` equals Rozvaha A.V.
- **From Date** defaults to the start of the fiscal year of To Date.

### Účetní deník (chronological journal, § 13)
- Lists every GL entry in time order with evidenční (pořadové) číslo, datum, účet MD/Dal,
  částka, popis. **Číslo dokladu** is a drill-down link — click it to open the source voucher,
  where its attachment lives.
- Filters: From/To Date, Finance Book, Voucher No, Cost Center, Project. The footer shows the
  control total (Má dáti = Dal).

### Row "Nezařazené účty" / "Nezařazené náklady a výnosy"
If a report shows one of these rows, an account with a balance has **no** (or an unlaid-out)
Account Category. The statement still reconciles, but ask Stream 1 to categorize that account.

---

## 3. Developer WIP — the build-to-sell flats (účet 121)

The flats are **inventory, not fixed assets** (LOCKED decision). Do **not** use the ERPNext
Asset doctype for them. Model construction with **Journal Entries** (the interní-doklad series)
carrying a **Project** (and optionally Cost Center) so 121 is analysed by project / block / unit.

Method A (způsob A) — costs hit class 5 as incurred, then a period-end change-in-state:

| Step | MD | D | Note |
|---|---|---|---|
| Material, subcontractors, design, own wages, own-equipment depreciation | 501 / 518 / 521 / 524 / 525 / 551 | 321 / 331 / 221 … | class-5 costs, each JE tagged with the Project |
| **Period-end change-in-state** (monthly recommended) | **121** | **611** | value = own production cost (materiál + přímé mzdy + výrobní režie; NOT admin/selling). P&L effect of construction in the period is zero |
| Year-end NRV impairment (if cost > realizable value) | 559 | 192 | 192 is a correction → shows in Rozvaha C.I.2 **Korekce**; not tax-deductible |
| On unit sale / completion | 611 | 121 | derecognize the sold unit's cost (change-in-state reversal); recognize revenue separately 311 / 604 |

Read the result in:
- **Nedokončená výroba** report — 121 balance by Project / Cost Center / account.
- **Rozvaha** row **C.I.2 Nedokončená výroba a polotovary** — the same 121 balance.

Land bought for the development is project inventory, not `031`. Whether land sits in 031 or is
folded into 121, and whether completion reserves are deductible, are accountant policy calls.

---

## 4. Genuine fixed assets (automobil, own-use property) — dual odpisy

Only real DHM uses the ERPNext **Asset** flow. Two **Finance Books** give the parallel
schedules: `Účetní odpisy` (accounting, monthly straight-line over useful life) and
`Daňové odpisy` (tax, annual). Categories: **Automobil** (022, odp. skupina 2), **Stavby**
(021), **Pozemky** (031, non-depreciable).

1. Ensure the Asset Category has the company's accounts (see Prerequisites §4).
2. Create a fixed-asset **Item** (Is Fixed Asset ✓, Asset Category = Automobil).
3. Create the **Asset**: set Asset Category, gross/net purchase amount, Available For Use Date,
   **Calculate Depreciation ✓**. The two finance-book rows copy from the category. Submit.
4. ERPNext generates one **Asset Depreciation Schedule** per finance book. The účetní book posts
   depreciation to the GL (551 / 082); the daňové book is the parallel tax schedule for the
   deferred-tax difference (481).

Run the statutory statements with **Finance Book = Účetní odpisy** (or leave blank if the
company default is set) so only účetní odpisy hit the books.

> Note: the daňové book currently uses ERPNext straight-line as an approximation. Czech § 31
> rovnoměrné (year-1 ≠ year-2+) and § 32 zrychlené coefficients are a Custom API follow-up.

---

## 5. Verifying before sign-off

- Rozvaha: AKTIVA CELKEM Netto == PASIVA CELKEM Netto (no KONTROLA row).
- VZZ `***` == Rozvaha A.V for the same period.
- Účetní deník footer: Má dáti == Dal.
- No unexpected "Nezařazené" rows.
- Run the app tests on a dev site:
  ```
  bench --site <site> run-tests --module czech_accounting.czech_accounting.report.rozvaha.test_rozvaha
  bench --site <site> run-tests --module czech_accounting.czech_accounting.tests.test_asset_depreciation
  ```
- Accountant signs off on the statement layouts before real filing use.
