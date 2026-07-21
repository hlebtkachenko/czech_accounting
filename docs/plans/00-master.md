# Master plan — Czech accounting agendas (parallel build)

_Reimagined 2026-07-21 from three research passes (see `research/`): the CoA spreadsheet,
the accountingAfframe law vault, and ERPNext v16 modeling. Scope narrowed by Hleb._

## Scope

**In:** the books **Rozvaha**, **Výkaz zisku a ztráty (druhové)**, **Účetní deník**; the
document agendas **faktura přijatá / vydaná, banka, pokladna, interní doklad**; **assets**
(automobil, pozemek, self-built byty) with účetní + daňové odpisy; **VAT payer** support
(classification + templates; DPH XML deferred).

**Out (now):** ARES, ISDOC, CNB FX, MCP/agent bulk import (deferred), full Czech UI
localization, sbírka-listin filing, DPPO. Focus is agendas + statutory fidelity, sourced
from `/Users/hleb/Developer/obsidian-vault/accountingAfframe`.

## What ERPNext v16 gives us (do not rebuild)
Most of this is REUSE+EXTEND, not new code (see `research/erpnext-modeling.md`):
- Agendas map to native doctypes: FP→Purchase Invoice, FV→Sales Invoice, banka→Bank
  Account + Bank Statement Import + Reconciliation, pokladna→Payment Entry + Mode of
  Payment (Cash→211), interní doklad→Journal Entry.
- Statements are **native config**: v16 `Financial Report Template` + `Account Category`
  map accounts to statutory rows. Not a from-scratch report.
- Assets: `Asset` + `Asset Category` + CWIP (self-built) + two `Finance Book`s (účetní vs
  daňové odpisy) are native.
- VAT: Sales/Purchase Taxes templates + reverse charge via Add+Deduct rows on 343.

**The real builds:** the Czech CoA (blocking), the 4-column statutory Rozvaha filing layout,
the §13 Účetní deník report, and the asset/odpisy configuration.

## Milestones
- **M1 — can book:** Czech CoA + fields + agendas → draft double-entry documents.
- **M2 — legally operable:** Rozvaha + full VZZ + Účetní deník reconcile to the TB.
- **M3 — later:** DPH XML, assisted import, integrations.

## The shared contract (fixed FIRST, so streams don't collide)
This is what makes the three streams parallel. All identifiers below are frozen in the
foundation commit; every stream codes against them.

1. **Accounts** — source of truth `research/coa-normalized.json` (368 nodes, 305 synthetic,
   root_type driven by the `Typ` column, 17 mixed nodes re-parented). Account numbers are
   the join key everywhere. Fixed anchors: VAT `343.100` (na vstupu) / `343.200` (na
   výstupu); cash `211`; bank `221` (+ `221001` CZK); receivable `311`; payable `321`;
   clearing `261`; self-built assets via `042`.
2. **Account Category taxonomy** — the codes linking each posting account to a Rozvaha row
   (Decree 500/2002 Příloha 1) and a VZZ-druhové row (Příloha 2). Stream 1 **assigns** a
   category to every posting account; Stream 3 **builds the report templates** from those
   categories. This is the seam between Stream 1 and Stream 3.
3. **Custom field registry** (namespaced `cz_`, frozen names):
   - Party/company: `cz_ico` (Company/Customer/Supplier). DIČ = native `tax_id`.
   - Invoices (Purchase/Sales): `cz_duzp` (DUZP), `cz_date_received`, `cz_vat_supply_type`,
     `cz_kh_section`, `cz_is_reverse_charge`. Supplier no/date = native `bill_no`/`bill_date`.
     Opravný doklad = native `is_return` + `return_against`.
   - Payment side (Payment Entry / Bank Transaction): `cz_variable_symbol`,
     `cz_constant_symbol`, `cz_specific_symbol`. NOTE: VS/KS/SS are **payment-matching refs,
     not statutory invoice fields** (law brief) — they live here, not on the invoice.
4. **Naming series (číselné řady)** — policy, not gapless-by-law: `FP-.YYYY.-`, `FV-.YYYY.-`,
   `PO-.YYYY.-` (pokladna), `BV-.YYYY.-` (banka), `ID-.YYYY.-` (interní). Accountant-approved.
5. **hooks.py fixtures** — Stream 1 (which merges first) pre-declares the full, filtered
   `fixtures` list covering all three streams so each stream drops fixture JSON files WITHOUT
   editing hooks.py (avoids the one guaranteed merge conflict).
6. **File-ownership map** — no two streams touch the same file:
   - Stream 1: `chart_of_accounts/`, account-creation patch, `fixtures/account_category*.json`,
     `fixtures/custom_field_party.json`, VAT account setup, `hooks.py` (fixtures skeleton).
   - Stream 2: `fixtures/custom_field_document.json`, `fixtures/naming_series*`, tax templates,
     Mode of Payment, payment-symbol fields, předkontace defaults.
   - Stream 3: `report/` (Rozvaha, VZZ, Účetní deník), `fixtures/financial_report_template*`,
     `fixtures/account_category` is READ-ONLY here, asset categories + finance books.

## Execution protocol
1. **Foundation commit** (this contract + the 4 plan files + `research/`) lands on `main`
   [done]. Stream 1 then lands the `hooks.py` fixtures skeleton first (it merges first),
   pre-declaring all three streams' fixture entries so Streams 2 and 3 never edit hooks.py.
2. Three Conductor workspaces branch from `main`: `stream/1-foundation-coa`,
   `stream/2-agendas-vat`, `stream/3-books-assets`. Each reads its plan in `docs/plans/`.
3. Parallel dev against the frozen identifiers. Streams 2 and 3 build against known account
   numbers / category codes / field names even before Stream 1's fixtures exist; they fully
   verify on the server only after Stream 1 merges.
4. **Merge order 1 → 2 → 3.** After each merge: on the VPS `git pull` + `bench migrate` +
   `clear-cache`, then verify that stream's acceptance on a throwaway test company.

## Decisions (LOCKED 2026-07-21)
1. **One site**, one Company per client (up to 13). Masters (Customer/Supplier/Item) are
   shared site-wide — accept it; enforce separation via the Company field + permissions.
2. **Self-built byty = build-to-SELL → inventory, not DHM.** Construction WIP accumulates in
   `121` Nedokončená výroba (method A: class-5 costs expensed as incurred, then period-end
   change-in-state **MD 121 / D 611**), valued at vlastní náklady (direct material + labor +
   production overhead; not admin/selling). On sale → `132` / derecognition. Land bought for
   the development is project inventory, **not `031`**. (KB: ČÚS 015 + Decree 500/2002 §10;
   `research/`… real-estate-dev scenario.) Genuine long-term fixed assets — automobil (`022`),
   any own-use/long-held property (`021`/`031`) — still use the ERPNext Asset flow.
3. **enable_immutable_ledger = ON.**
4. **VAT = monthly** filing (plátce).
5. Analytical depth: standard synthetic set + minimal analytics (`343.100/.200`, `221001`,
   plus `121` by project/block/unit).
6. **Accountant sign-off** gates the CoA and the statement layouts before real use.

## Reuse review
Personal, unverified reference implementations analyzed in `research/`: the CoA converter
(`coa-analysis.md` — reuse its CSV schema + class-split algorithm, not its data), plus
`reuse-czech-invoicing.md` and `reuse-assistant-core.md`. Each stream has a "reuse review"
task pointing at the relevant file. Trust nothing from them without verification.
