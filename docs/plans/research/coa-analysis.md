# Czech Chart of Accounts — parsing, mapping, and ERPNext ingestion analysis

Scope: `.context/attachments/BGf7L7/coa.xlsx` (Czech commercial "Účtová osnova", Decree
500/2002), the `yuanweize/ERPNext-Czech-Uctova-Osnova-COA-Converter` repo, and the ERPNext
account model from `czech_accounting/docs/knowledge-base/erpnext/accounting/`.

Output data file: `coa-normalized.json` (same folder).

---

## 1. What the spreadsheet actually is

One sheet, `Účtová osnova 2`, 306 data rows, 10 columns. It is an **export from a Czech
accounting package** (Money S3 / Pohoda-style), not a raw statutory list. Columns:

| Col | Header | Meaning | Distinct values |
|---|---|---|---|
| A | `Účet` | Account number, 6-digit zero-padded (`010000` = synthetic `010`; `221001` = analytical) | 306 unique |
| B | `Název` | Czech name | — |
| C | `Alternativní název 1` | English name (authoritative, already in the file) | — |
| D | `Druh` | Statement kind | Rozvahový 206, Výsledovkový 96, Závěrkový 4 |
| E | `Typ` | Balance side / nature | Aktivní 129, Pasivní 77, Nákladový 71, Výnosový 25, (blank) 4 |
| F | `Podtyp` | Sub-behaviour | Nesledovat saldo 202, Ovlivňující daň 72, Neovlivňující daň 24, Sledovat saldo 4, Sledovat zůstatek na MD 4 |
| G | `Oprávkový` | Is an accumulated-depreciation / impairment contra account | Ano 34, Ne 272 |
| H | `Vnitropodnikový` | Internal management account | all Ne |
| I | `Technický` | Technical account | all Ne |
| J | `Účet převodu` | Transfer account (mirrors A) | — |

**Key consequence:** the file carries authoritative mapping columns. Root type does **not**
have to be guessed from the class digit — `Typ` gives it directly (Aktivní→Asset,
Pasivní→Liability/Equity, Nákladový→Expense, Výnosový→Income). The task's class→root_type
table is used only as the fallback/skeleton; per-account `Typ` overrides it.

### Parsing note (risk)
`openpyxl` and `pandas` (default engine) **both fail** on this file — its `xl/styles.xml`
has a named cell style with a `null` name, which trips `openpyxl`'s strict stylesheet
parser (`TypeError: ... .name should be str but value is NoneType`). `calamine` was not
installed. The working path was **raw XML** (`sharedStrings.xml` + `worksheets/sheet1.xml`
via `xml.etree`). Any downstream pipeline that relies on openpyxl/pandas on this exact file
must re-save it or use a raw/`calamine` reader.

### Account-number structure
All 306 rows are 6-digit. 305 are synthetic-level (suffix `000`, i.e. real 3-digit
synthetics `010`…`710`). Exactly **one analytical** exists: `221001` "Bankovní účet CZK"
under synthetic `221`. There are no explicit class (1-digit) or group (2-digit) header rows
in the file; those levels are implied and were synthesized during normalization.

The `X00` / `XX0` accounts (e.g. `010`, `020`, `210`, `220`, `310`, `320`) act as **group
summaries** but are stored as ordinary 3-digit synthetics. They duplicate the synthesized
2-digit group node semantically — see §5 for how to handle them.

---

## 2. Counts

Source: **306 accounts** (305 synthetic + 1 analytical), classes 0–7 all present.

Normalized tree (`coa-normalized.json`): **368 nodes**
- 8 class nodes (synthesized, `is_group=true`)
- 54 group nodes (synthesized 2-digit, `is_group=true`)
- 305 synthetic nodes (from source; `221` promoted to `is_group=true` because it has an analytical child)
- 1 analytical node (`221001`)

Accounts per class (synthetic level): 0→53, 1→27, 2→25, 3→60, 4→40, 5→71, 6→25, 7→4.

root_type distribution (all 368 nodes): Asset 157, Expense 82, Liability 65, Equity 34, Income 30.

account_type assigned (leaves + relevant groups): Fixed Asset 7, Accumulated Depreciation
13, Stock 6, Tax 4, Cash 2, Bank 2, Receivable 1, Payable 1, Depreciation 1, Cost of Goods
Sold 1, Stock Adjustment 1, Expenses Included In Valuation 1. Everything else left blank
(ERPNext `account_type` is optional and only drives special behaviour).

Notable subsets from the source columns:
- **34 contra accounts** (`Oprávkový=Ano`): oprávky `07x`/`08x`/`098` (true accumulated
  depreciation) plus opravné položky `09x`/`19x`/`29x`/`39x` (impairment allowances). Only
  the `07x`/`08x`/`098` set got `account_type = Accumulated Depreciation`; the impairment
  allowances stay contra-asset with blank type (ERPNext has no exact type for them).
- **Balance-tracked (`Sledovat saldo`)**: `310`, `311`, `320`, `321` — the trade
  receivable/payable control accounts → ERPNext `Receivable`/`Payable`.
- **Closing (`Závěrkový`, class 7)**: `700`, `701` (počáteční rozvažný), `702` (konečný
  rozvažný), `710` (zisků a ztrát).
- **Tax-relevance (`Podtyp`)**: 72 "Ovlivňující daň z příjmů" / 24 "Neovlivňující" — this
  is the daňový/nedaňový (tax-deductible) flag on class 5/6, worth preserving as a custom
  field later.

---

## 3. Class → root_type table used

`Typ` (col E) is the primary driver; the class digit is the skeleton. Where a class is
mixed, resolution is per-account by `Typ` (classes 2, 3) or per-group by law (class 4).

| Class | Meaning | Nominal root_type | Per-account / per-group override |
|---|---|---|---|
| 0 | Dlouhodobý majetek (fixed assets) | Asset | none — all Aktivní |
| 1 | Zásoby (inventory) | Asset | none — all Aktivní |
| 2 | Krátkodobý fin. majetek + peníze | Asset | groups **23, 24** (short-term loans/borrowings) → **Liability** (Typ=Pasivní) |
| 3 | Zúčtovací vztahy (receiv./payables/clearing) | Asset (nominal) | **per-account by Typ**: Aktivní→Asset, Pasivní→Liability. Groups split ~50/50 (see §4) |
| 4 | Kapitálové účty + dlouhodobé závazky | Equity | groups **41,42,43,49**→Equity; **45,46,47,48**→Liability |
| 5 | Náklady (expenses) | Expense | none |
| 6 | Výnosy (revenue) | Income | none |
| 7 | Závěrkové účty (closing) | Equity | see note below |

**Class 7 note:** ERPNext has only 5 root types; closing accounts do not fit cleanly.
They are mapped to **Equity** (the converter does the same). In practice ERPNext closes the
year with a **Period Closing Voucher** into one retained-earnings account, so `701/702/710`
as posting accounts are optional — recommend keeping them as non-posting/reference or
dropping them from the operational chart.

`account_type` assignments (where unambiguous): `211,213`→Cash · `221,221001`→Bank ·
`311`→Receivable · `321`→Payable · `341,342,343,345`→Tax · `112,121,122,123,124,132`→Stock ·
`021,022,025,026,029,031,032`→Fixed Asset · `07x,08x,098`→Accumulated Depreciation ·
`551`→Depreciation · `504`→Cost of Goods Sold · `549`→Stock Adjustment · `518`→Expenses
Included In Valuation. Deliberately **not** forcing `Receivable`/`Payable` onto non-trade
sub-accounts (`313,314,335,351…`, `322,324,325…`) because that type makes ERPNext demand a
Party on every posting.

---

## 4. Mixed nodes — the ERPNext tree problem

ERPNext requires every node in a subtree to share the parent's `root_type` (KB:
`company-chart-and-periods.md` — "Asset/Liability/Equity map to Balance Sheet…"; parent
must be a group of the same Company). The Czech class/group hierarchy violates this in
**17 nodes**, all captured in the JSON (parent/child root_type differs):

- **Class 2** node is Asset but groups `23`, `24` are Liability.
- **Class 3** node is genuinely split — leaves are exactly **30 Asset / 30 Liability**.
  Groups `32,33,34,36` are Liability; `31,35,37,38,39` lean Asset.
- **Class 4** node is Equity but groups `45,46,47,48` are Liability.
- **Genuinely mixed groups** (children span two root types):
  - `33` — Liability majority, minority **`335`** (Pohledávky za zaměstnanci, Asset).
  - `37` — Asset majority, minority **`372, 377, 379`** (Liability).
  - `38` — Asset majority, minority **`383, 384, 389`** (Liability).

The JSON keeps the **Czech-faithful hierarchy** (parent = class→group→synthetic) and puts
the authoritative per-leaf `root_type` on every leaf. The 17 mismatches are intentional and
are the exact list the app must fix before feeding ERPNext (see §5).

---

## 5. Converter verdict (`yuanweize/ERPNext-Czech-Uctova-Osnova-COA-Converter`)

Personal repo, MIT, Python. It converts a **different** source (a curated Stormware/Pohoda
CSV `data/commercial/uctova_osnova_2024.csv`, 3-digit synthetics starting at `011`) into an
ERPNext **CSV** with the 8-column header:
`Account Name, Parent Account, Account Number, Parent Account Number, Is Group, Account
Type, Root Type, Account Currency`. Live app on Render confirms the same output.

**Reuse (good ideas):**
- The **8-column ERPNext CSV schema** is exactly what ERPNext's own Chart of Accounts
  Importer consumes — correct and reusable.
- The **mixed-class split algorithm** in `parsers/commercial_parser.py`: it does *not* emit
  class-level nodes for classes 2/3/4, routes each group directly under the correct ERPNext
  root, and **re-parents minority leaves** (root_type ≠ group majority) straight under the
  ERPNext root. This is the right shape and matches our 17-mismatch finding. The class-4
  law mapping (`41,42,43,49`→Equity; `45,46,47,48`→Liability) matches our data exactly.
- Per-account `balance_side` (A/P) as the root_type driver — same principle as our `Typ`.
- Bilingual account names (name collision handling for "Standard with Numbers" mode).

**Avoid (bugs / oversimplifications):**
- **Its bundled data is not ours.** It ships `011 Zřizovací výdaje` (abolished in 2016,
  correctly absent from our file) and lacks the `0X0/XX0` summary accounts our export uses.
  Do not import its CSV; use our normalized data.
- **Aggressive `account_type` map that forces Party ledgers:** `313,314`→Receivable and
  `322,324,325`→Payable turn advance/other accounts into party accounts.
- **Outright wrong mapping:** `389` (Dohadné účty pasivní — estimated/accrued *liabilities*)
  → `Stock Received But Not Billed`, and `518`→`Expenses Included In Valuation`, `549`→`Stock
  Adjustment` are perpetual-inventory hacks bolted onto a general chart. `389` is a liability,
  not a stock-clearing account.
- **Arbitrary tie-break** "class-3 group tie → Liability (conservative)". With our data the
  split is exact 30/30 at class level, so a class-level tie-break is meaningless; resolve
  per-account, never per-class.
- **Redundant hardcoded group→root_type tables** duplicate what `balance_side`/`Typ`
  already say; the tables can drift from the data.
- The bundled `importer.py` is just a **truncated copy of ERPNext's own
  `chart_of_accounts_importer.py`** (it even stops before `build_forest`) — no novel value;
  read ERPNext core instead.
- **LLM translation pipeline** (SiliconFlow/OpenRouter/OpenAI/Gemini) for account names is
  irrelevant and risky for a statutory chart — our source already ships authoritative EN
  names in column C. Skip it.

Its CSV structure (row per account, parent by name + parent number) is the schema; its data
and its account_type opinions are not to be trusted.

---

## 6. ERPNext account model + how to ingest (from the KB)

From `company-chart-and-periods.md` and `ledger-architecture.md` (source-verified against
ERPNext v16.28.0):

- `Account` is a **NestedSet**: account_number (unique per Company), root_type, report_type
  (Asset/Liability/Equity→Balance Sheet, Income/Expense→P&L), account_type, parent (same
  Company, must be a group), is_group, currency (defaults to Company currency).
- **Root accounts must be groups; you post only to leaves.** All **five** root types
  (Asset, Liability, Equity, Income, Expense) are required by the importer.
- **No first-class hook to inject a custom CoA.** Two supported delivery mechanisms:
  1. **Chart template as a tree JSON** consumed by `create_charts` /
     `build_tree_from_json` (the format ERPNext's own verified charts ship, invoked from
     `Company.on_update` for a new company with no accounts).
  2. **Chart of Accounts Importer** (`import_coa`) on a **zero-transaction** company — it is
     **destructive** (`unset_existing_data` deletes company Accounts, Party Accounts, Modes
     of Payment, tax templates before rebuilding). Never rerun on a company with GL Entries.
- **Never insert `GL Entry` directly.** The chart is masters only; posting always goes
  through a voucher → `make_gl_entries`.

### Recommended shape for our app

Ship a **tree JSON** (native ERPNext chart template) and create Account records
programmatically at company setup, or import the equivalent CSV once on a fresh company.
The tree JSON is a nested dict keyed by account **name**, with reserved keys per node:

```json
{
  "Aktiva": {
    "root_type": "Asset", "is_group": 1, "account_number": "0",
    "Dlouhodobý nehmotný majetek": {
      "is_group": 1, "account_number": "01",
      "Software": { "account_number": "013", "account_type": "" },
      "Goodwill":  { "account_number": "015", "account_type": "" }
    }
  },
  "Náklady":  { "root_type": "Expense", "is_group": 1, "account_number": "5", "...": {} },
  "Výnosy":   { "root_type": "Income",  "is_group": 1, "account_number": "6", "...": {} }
}
```

Rules for building it from `coa-normalized.json`:

1. **Top of tree = the 5 ERPNext roots**, not the Czech class digits. Czech classes 0/1/5/6
   map 1:1 to Asset/Asset/Expense/Income; class 7 → Equity. **Do not** create a single Czech
   node for the mixed classes 2/3/4 — split them.
2. **Re-parent the 17 mixed nodes** (§4) under the root matching their own `root_type`:
   groups `23,24`→Liability; `32,33,34,36`→Liability, `31,35,37,38,39`→Asset; groups
   `45,46,47,48`→Liability, `41,42,43,49`→Equity; and the minority leaves `335` (→Asset),
   `372,377,379` (→Liability), `383,384,389` (→Liability) directly under the right root.
   Equivalently: **build bottom-up, grouping every leaf by its own authoritative `root_type`**
   — that produces a valid tree with zero manual exceptions.
3. **is_group / posting leaves:** class and group nodes are groups; synthetics are posting
   leaves *unless* they carry analyticals (`221` becomes a group, `221001` is the leaf).
4. **Currency** defaults to CZK (Company currency); set explicit currency only on
   foreign-currency bank/analytical accounts.
5. Include a Czech **classification / tax-deductible** custom field later (from `Druh` and
   `Podtyp`) rather than encoding meaning only in names (KB failure mode: "encode statutory
   classes only in labels").

### Analyticals — keep vs skip

The user said analyticals can be skipped when unsuitable. Our source has essentially none
except `221001` (a per-currency bank leaf) — **keep it** (it is the postable bank account;
`221` correctly becomes a group). Recommended policy for the real app:

- **Keep** analyticals that are genuine postable sub-ledgers: bank accounts per
  currency/institution under `221`, VAT-rate splits under `343`, receivable/payable party
  breakdowns under `311/321`, cost/expense splits the accountant actually needs.
- **Skip / do not post to** the `0X0` and `XX0` summary synthetics (`010, 020, 210, 220,
  310, 320, 340, 380, 700, …`). They duplicate the synthesized 2-digit group node. Either
  drop them, or mark them `is_group=true` (non-posting). In `coa-normalized.json` they are
  currently kept as `synthetic` leaves for fidelity — flag/collapse them at tree-build time.
- The 34 contra accounts (`Oprávkový=Ano`) are kept; they are normal ledger accounts (with
  a credit-normal balance on the asset side), not to be skipped.

---

## 7. Risks

1. **openpyxl/pandas can't open this exact xlsx** (null-named cell style). Use raw XML or
   `calamine`, or re-save the file, in any ingestion tooling.
2. **Mixed classes 2/3/4 + groups 33/37/38** are the only real modelling hazard — a naive
   "class digit = one root_type" import produces an ERPNext tree that fails validation. The
   17 offending nodes are enumerated (§4) and flagged in the JSON.
3. **Class 7 closing accounts** have no clean ERPNext root; mapping to Equity is a
   convention, not a statutory fact — needs accountant sign-off, and ERPNext's Period
   Closing Voucher may make them redundant.
4. **Contra / impairment accounts** (`09x,19x,29x,39x`) have no exact ERPNext `account_type`;
   left blank. Confirm reporting treatment with the accountant.
5. **CoA Importer is destructive** — only ever run once on a fresh, backed-up,
   zero-transaction company (KB hard rule). Prefer shipping the tree JSON.
6. **Accountant sign-off** gates the chart before real use (repo invariant); this analysis
   encodes a defensible mapping, not a legal ruling on which regime applies.
