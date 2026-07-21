---
title: Czech Accounting-Law Requirements Brief — Narrowed ERPNext Bookkeeping Scope
kind: requirements-brief
status: draft-for-accountant-signoff
scope: >
  Statutory requirements for three books (Rozvaha, VZZ druhové, Účetní deník),
  five document agendas (faktura přijatá/vydaná, banka, pokladna, interní doklad),
  assets (DHM/DNM incl. auto/pozemek/stavby + self-built byty + odpisy), and VAT (plátce).
primary_source: >
  Obsidian vault accountingAfframe (/Users/hleb/Developer/obsidian-vault/accountingAfframe),
  cross-checked against czech_accounting/docs/knowledge-base/czech-accounting/.
prepared: 2026-07-21
disclaimer: >
  Requirements inventory, not legal/tax advice. Every statutory output (CoA, statements,
  VAT XML) needs Czech accountant sign-off before real use (per repo CLAUDE.md invariant).
  Vault confidence is mostly "medium" (single primary source, no second cross-check);
  effective-dated rules must be re-verified against e-Sbírka consolidations at build time.
---

# Czech Accounting-Law Requirements Brief

Legend: **MD** = má dáti (debit), **D** = dal (credit). Citations point to the vault note
path unless prefixed `repo:` (then `czech_accounting/docs/knowledge-base/czech-accounting/`).
Where vault and repo differ, the vault is preferred and the divergence is noted.

## 0. Legal frame (foundation for everything below)

- **Účetní jednotky / double-entry**: Act 563/1991 Sb. (*zákon o účetnictví*, ZÚ). 2026
  consolidation effective 2026-01-01. Books defined in § 13; document content § 11;
  inventarizace § 29–30; retention § 31–35. Source: `10-foundations/statutory-books.md`,
  `repo:applicability-documents-and-books.md`.
- **Statement layout / chart framework**: Decree (vyhláška) 500/2002 Sb. (podnikatelé),
  consolidation effective 2024-01-01 — Příloha 1 = rozvaha, Příloha 2 = VZZ druhové,
  Příloha 3 = VZZ účelové, směrná účtová osnova. Source: `20-coa/README.md`,
  `90-meta/INDEX-by-rozvaha-row.md`, `90-meta/INDEX-by-vzz-row.md`.
- **Účetní standardy**: ČÚS 001–023 (MF ČR). Relevant here: ČÚS 001 (accounts/books),
  013 (DHM/DNM), 015 (zásoby), 016 (peněžní prostředky), 017 (zúčtovací vztahy),
  019 (náklady a výnosy), 003 (odložená daň), 006 (kurzové rozdíly).
- **VAT**: Act 235/2004 Sb. (*zákon o DPH*, ZDPH), consolidation effective 2026-01-01.
- **Income tax / depreciation**: Act 586/1992 Sb. (*zákon o daních z příjmů*, ZDP).
- **Effective-dated caveat**: all rules below carry a date; the repo's own domain invariant
  is "never hardcode a rule as timeless" (`repo:CLAUDE.md`). Vault "law as in force
  2026-05-23"; repo KB pinned to 2026-01-01 consolidations.

---

# PART A — BOOKS (three only)

Class 5xx (náklady) and 6xx (výnosy) never appear in the Rozvaha; they flow through the VZZ
→ účet 710 → 431 → 428/429 at close. Class 7xx (závěrkové účty) appear in neither statement.
Source: `90-meta/INDEX-by-rozvaha-row.md`.

## A1. Rozvaha (balance sheet)

- **Statutory layout basis**: Decree 500/2002 Sb., **Příloha č. 1** (plný / zkrácený rozsah
  by size category). Aktiva = Pasiva. Source: `90-meta/INDEX-by-rozvaha-row.md` (built from
  Příloha č. 1; 70 statutory rows mapped to 236 accounts).
- **Aktiva structure** (row-code → contributing accounts):
  | Section | Row group | Key accounts |
  |---|---|---|
  | A. Pohledávky za upsaný ZK | A | 353 |
  | B.I DNM | B.I.1–5 | 01x (011–019), 04x pořízení (041); oprávky 07x; OP 09x |
  | B.II DHM | B.II.1 Pozemky a stavby | **021** (stavby), **031** (pozemky) |
  | B.II DHM | B.II.2 Hmotné movité věci | **022** |
  | B.II DHM | B.II.7 Zálohy / DHM v pořízení | **042**, 052 |
  | B.III DFM | B.III.1–5 | 06x |
  | C.I Zásoby | C.I.1–6 | 111/112, **121**/122, 123, 131/132, 15x |
  | C.II Pohledávky | C.II.x | **311**, 314, 341–345, 351/352, 355, 378, **388** dohadné aktivní |
  | C.IV Peněžní prostředky | C.IV.1 pokladna | **211**, 213 |
  | C.IV Peněžní prostředky | C.IV.2 účty | **221**, 261 |
  | D. Časové rozlišení aktiv | D.1–3 | 381, 382, 385 |
- **Pasiva structure**:
  | Section | Row group | Key accounts |
  |---|---|---|
  | A. Vlastní kapitál | A.I–A.V | 411/419 ZK, 412–418 fondy, 421–427 fondy ze zisku, 428 nerozdělený zisk, 429 neuhr. ztráta, **431** VH běžného období, 491 (FO) |
  | B.I Rezervy | B.I.1/3 | 451, 453, 459 |
  | B.II Závazky | B.II.x | **321**/324, 331/333, **336**, 341–345, 361–368, 471–479, **389** dohadné pasivní |
  | C. Časové rozlišení pasiv | C.1/2 | 383, 384 |
- **Side-resolution rule** (account class → statement side): 01x–09x → Aktiva B; 11x–15x →
  Aktiva C.I; 21x/22x → Aktiva C.IV; 31x–35x → Aktiva C.II; 41x–43x → Pasiva A; 45x–47x →
  Pasiva B; 48x odložená daň → C.II.1.4 (debit) OR B.II.8 (credit); 38x → D (aktiva, 3-digit
  381/382/385) OR C (pasiva, 383/384). Source: `90-meta/INDEX-by-rozvaha-row.md`.
- **Effective-dated**: size category (mikro/malá/střední/velká) sets plný vs zkrácený rozsah;
  category change only after crossing thresholds at balance-sheet date in **two consecutive**
  periods (§ 1b odst. 5 ZÚ; unchanged by Act 316/2025). Source:
  `60-deadlines-penalties/2026-rates-and-limits.md`,
  `70-ai-platform/primary-source-evidence/F2A.3-law-316-2025.md`.
- **GAP**: the vault provides the account→row *mapping* but does **not** quote the literal
  Příloha č. 1 form layout verbatim (only the derived index). Verifier flags W7-V1/V2/V3 note
  aktiva/pasiva code collisions and short-vs-long-term reclassification not mechanically
  resolved. For non-profits (504/2002), FAQ-NP-005 explicitly leaves the literal statement
  layout as an open gap — relevant only if 504/2002 entities come into scope.

## A2. Výkaz zisku a ztráty — druhové členění (by nature)

- **Statutory layout basis**: Decree 500/2002 Sb., **Příloha č. 2** (druhové členění).
  Účelové členění (Příloha č. 3) is out of scope here. Source: `90-meta/INDEX-by-vzz-row.md`
  (built from Příloha č. 2; 19 statutory rows).
- **Structure** (row → accounts), druhové:
  | Row | Name | Účty |
  |---|---|---|
  | I | Tržby z prodeje výrobků a služeb | 601, 602 |
  | II | Tržby za prodej zboží | 604 |
  | A.1 | Výkonová spotřeba — materiál + energie | 501, 502, 503 |
  | A.2 | Výkonová spotřeba — služby | 504, 511, 512, 518 |
  | B | Změna stavu zásob vlastní výroby | 611–614 |
  | C | Aktivace | 621–624 |
  | D.1–D.4 | Osobní náklady (mzdy / odměny orgánů / zákonné pojištění / ostatní) | 521; 522/523; 524/525/526; 527/528 |
  | E.1 | Úpravy hodnot DNM/DHM — odpisy | **551**, 557 |
  | E.2/E.3 | Úpravy hodnot zásob / pohledávek (OP) | 552; 547, 558, 559 |
  | F | Ostatní provozní (agregát) | 531/532/538 (daně), 541 (ZC prod. DHM), 542, 543, 544–546, 548, 549, 513; výnosy 641/642/644/646/648/649 |
  | G / H | Ostatní finanční výnosy / náklady | 661–668 / 561, 563, 564, 566, 567, 568, 569 |
  | Q | Daň z příjmů (splatná + odložená) | 591, 592, 595 |
- **Effective-dated / notes**: 513 reprezentace and 543 dary are booked here but are daňově
  neuznatelné (§ 25/1/t, § 25/1/o ZDP). Kurzové rozdíly → 563/663 (ČÚS 006).
  Source: `90-meta/INDEX-by-vzz-row.md`.
- **GAP**: verifier flags W7-V4 (F sub-lines F.1/F.2/F.3 aggregated, need detail for real
  statutory VZZ generation) and W7-V5 (562 úroky placené mapping suspect). No verbatim
  Příloha č. 2 form layout in the vault.

## A3. Účetní deník (chronological journal)

- **Legal basis**: Act 563/1991 Sb. **§ 13** (mandatory book) + § 12. Source:
  `10-foundations/statutory-books.md`, `repo:applicability-documents-and-books.md`.
- **Function / required content**: chronological record of **all** accounting entries in time
  order. Each entry must include: **date (okamžik uskutečnění účetního případu)**, **description
  of the case**, **amount**, and a **reference to the source účetní doklad**. Entries must be
  continuous, made after document preparation, and cannot be recorded outside the účetní knihy
  (§ 12). Source: `10-foundations/statutory-books.md` §2, `repo:...` §§ 12–13.
- **Companion mandatory books** (context — not in scope but interlocked): *hlavní kniha*
  (general ledger, systematic by account; synthetic accounts hold ≥ opening balance, monthly
  aggregate MD/D turnover, closing balance at statement date), *knihy analytické evidence*,
  *knihy podrozvahové*. Simplified scope (malé/mikro, non-audited): deník + hlavní kniha stay
  mandatory; analytická/podrozvahová only to the extent the entity specifies.
- **Effective-dated**: none specific; § 13/§ 12 stable in 2026 consolidation.
- **ERPNext mapping caution** (`repo:applicability-documents-and-books.md`): the GL chronology
  is a *candidate*, not proven statutory output — needs explicit ordering, completeness
  reconciliation, and source-document linkage before "Czech journal" can be claimed.

---

# PART B — DOCUMENT AGENDAS ("agendy") — the focus

## Cross-cutting: required fields, dates, numbering, symbols

**Two distinct field regimes apply to every document:**

1. **Účetní doklad content — Act 563/1991 § 11(1)** (applies to ALL five agendas):
   označení dokladu; obsah účetního případu + jeho účastníci; peněžní částka (or unit price +
   quantity); **okamžik vyhotovení dokladu** (preparation date); **okamžik uskutečnění
   účetního případu** when different; podpisový záznam osoby odpovědné za případ + za
   zaúčtování. Source: `10-foundations/statutory-books.md` §5, `repo:applicability-documents-and-books.md`.

2. **Daňový doklad content — Act 235/2004 § 29** (applies when a *plátce* issues/receives a VAT
   invoice — agendas B1/B2, and cash receipts that are zjednodušený DD):
   supplier name/sídlo/**DIČ**; buyer name/address + **DIČ** (if plátce); **evidenční číslo
   daňového dokladu** (unique sequential number); **DUZP**; **datum vystavení** (if ≠ DUZP);
   description of supply; **základ daně** per rate; **sazba daně** (21/12); **výše daně** in
   **CZK** (mandatory even for foreign-currency invoices — § 29(1)(l)); total incl. daň.
   PDP → text *"Daň odvede zákazník"* instead of rate/amount (§ 29(2)). Source:
   `40-workflows/DPH/doklady.md`, `repo:vat-currency-and-corrections.md`.

**Dates to distinguish (do not collapse into "posting date"):**
`datum vystavení` (issue), `DUZP` (datum uskutečnění zdanitelného plnění — tax point),
`datum přijetí` (receipt, drives deduction timing), `datum splatnosti` (due), `posting date`.
The GFŘ position (Apr 2026) is that input-VAT deduction follows the **invoice receipt date, not
DUZP** (§ 73), with a **2-year absolute cutoff** from 1.1.2025 (Act 461/2024). Source:
`40-workflows/DPH/duzp.md` (external cross-refs), `40-workflows/DPH/doklady.md`.

**Numbering / číselné řady:** § 11 ZÚ and § 29 ZDPH require an *identifier / evidenční číslo* —
they do **NOT** mandate one globally gapless sequence. The system still needs controlled unique
series, no reuse, cancellation/correction traceability, and an exception register, all
accountant-approved. Source: `repo:vat-currency-and-corrections.md` ("Numbering conclusion"),
`repo:applicability-documents-and-books.md` (failure mode: "one global gapless series").

**VS / KS / SS symboly — IMPORTANT FINDING:** *variabilní symbol* (VS), *konstantní symbol*
(KS), *specifický symbol* (SS) are **payment-matching references (bank domain), not statutory
§ 29 invoice-content fields.** The vault treats VS only as a payment reference (e.g., DPH
payment VS = DIČ without "CZK" prefix; SP/ZP payments use the institution's VS). Source:
`40-workflows/month-end/06-DPH-monthly-filing.md`, `40-workflows/month-end/02-day-by-day-checklist.md`,
`40-workflows/month-end/03-bank-reconciliation-detail.md`. **GAP**: neither vault nor repo KB
documents VS/KS/SS as *invoice* fields, because legally they are not — model them as
payment/bank attributes used for auto-matching (Step 2 bank reconciliation), not as required
invoice content.

---

## B1. Faktura přijatá (received invoice)

- **Required fields**: § 11 ZÚ (účetní doklad) + § 29 ZDPH (if the buyer is a plátce claiming
  deduction — must hold a valid *daňový doklad* per § 73(1)). Deduction requires the tax
  document; deduction timing follows receipt date (see cross-cutting).
- **Numbering**: internal evidenční řada for došlé faktury (supplier's number stored separately
  as reference). No statutory gapless rule.
- **Standard předkontace** (domestic, plátce buyer + plátce seller):
  | Case | MD | D | Note | Source |
  |---|---|---|---|---|
  | Goods for resale | 504 *Prodané zboží* + 343 (VAT) | 321 *Dodavatelé* (gross) | 501 if internal consumption | `30-predkontace/purchase/goods.md` |
  | Material to stock, method A | 111 + 343 → then 112 / 111 → 501 / 112 on issue | 321 | 111 must be zero at rozvahový den | `.../goods.md` §3 |
  | Material, method B | 501 + 343 | 321 | year-end stock reversal 112↔501 | `.../goods.md` §4 |
  | Services | 518 *Ostatní služby* + 343 | 321 | 511 opravy, 512 cestovné, 513 reprezentace (no VAT deduction), 548/568 pojištění | `30-predkontace/purchase/services.md` |
  | DHM/DNM purchase | 042 (DHM) / 041 (DNM) + 343 | 321 | then activate to 02x/01x | `30-predkontace/purchase/assets.md` |
  | Neplátce buyer | 504/501 gross (net+VAT) | 321 | **no 343** — VAT is part of cost (§ 25/1/a ZDPH) | `.../goods.md` §2 |
  | Payment | 321 | 221 (or 211) | | `.../goods.md` |
- **Advances paid (zálohy poskytnuté)**: 314 *Poskytnuté zálohy* / 221 on payment; on receipt of
  *daňový doklad k záloze* 343 / 314; final invoice nets 314 and posts remaining to 321.
  Long-term advance → 475. Source: `30-predkontace/purchase/advances.md`.
- **Dobropis received (ODD, § 45)**: 321 / 5xx (same account as original) + 343.100 reversal;
  year-crossing → 321 / 648 + 343.100. Source: `.../advances.md` §4.
- **DUZP drivers**: goods = handover/transport start (§ 21); services = completion or last day of
  billing period (§ 21/4); intra-EU acq. = earlier of 15th of following month or supplier invoice
  (§ 25); import = customs acceptance (§ 23). Source: `40-workflows/DPH/duzp.md`.
- **KH/DAP classification** (buyer): B2 (per-invoice, individual ≥ 10,000 CZK gross from CZ
  plátce) / B3 (aggregate ≤ 10,000); PDP purchases → B1. DAP ř. 40 (21%) / ř. 41 (12%); PDP
  input ř. 43. Source: `40-workflows/DPH/kh-sh.md`, `.../goods.md`.

## B2. Faktura vydaná (issued invoice)

- **Required fields**: only a *plátce* may issue a *daňový doklad* — full § 29 ZDPH set. Issue
  deadline 15 days from DUZP (§ 28). Source: `40-workflows/DPH/doklady.md`.
- **Numbering**: own evidenční řada, sequential; KH matching depends on preserving the exact
  evidenční číslo and buyer DIČ formatting (`repo:vat-currency-and-corrections.md`).
- **Standard předkontace** (domestic, seller = plátce):
  | Case | MD | D | Amount | Source |
  |---|---|---|---|---|
  | Sale of zboží 21% | 311 *Odběratelé* | 604 *Tržby za zboží* | net | `30-predkontace/sales/01-sales-goods.md` |
  | + output VAT | 311 | 343 | VAT | same |
  | Sale of služby | 311 | 602 *Tržby z prodeje služeb* + 343 | net + VAT | `30-predkontace/sales/02-sales-services.md` |
  | Sale of materiál | 311 | 642 + 343; cost 542 / 112 | | `.../01-sales-goods.md` §3 |
  | Sale of DHM/DNM | 311 | 641 + 343; vyřazení 08x/07x → 02x/01x, ZC → 541 | | `30-predkontace/sales/03-sales-assets.md` |
  | Exempt service (§ 51) | 311 | 602 | net, **no 343**, no DAP/KH row | `.../02-sales-services.md` §5 |
- **Advances received (zálohy přijaté)**: 221 / 324 *Přijaté zálohy* (gross); VAT extracted
  324 / 343 (VAT arises on receipt, § 20a — even from a neplátce buyer). Final invoice: 311 / 604
  (full net) + 311 / 343 (incremental VAT only) + 324 / 311 (offset advance). Return: 324 / 221 +
  343 / 324 (needs opravný DD). Source: `30-predkontace/sales/05-sales-advances.md`.
- **DUZP**: goods = handover; services = completion / dílčí plnění per contract (§ 21/4); VAT
  liability arises at DUZP, **not invoice date** (common error). Source: `.../01-sales-goods.md`,
  `40-workflows/DPH/duzp.md`.
- **KH/DAP classification** (seller): A4 (per-invoice to identified buyer > 10,000 CZK incl. VAT,
  with buyer DIČ) / A5 (≤ 10,000 or to neplátci/citizens, aggregate); PDP supplies → A1; EU
  supplies → SH (souhrnné hlášení). DAP ř. 1 (21%) / ř. 2 (12%). Source: `40-workflows/DPH/kh-sh.md`,
  `.../01-sales-goods.md`.

## B3. Banka (bankovní výpis)

- **Required content / process**: match every line of the *bankovní výpis* to a GL entry in
  **221** (*Bankovní účty*) / **261** (*Peníze na cestě*). Import ABO (CZK) / MT940 (FX) / XML/CSV;
  auto-match on amount + date ±2 days + **variabilní symbol / reference**. Source:
  `40-workflows/month-end/03-bank-reconciliation-detail.md`.
- **Account structure**: 221 with analytics per account & currency (221.100 CZK, 221.200 EUR…);
  261 transit (**must be zero at each month-end**; items > 5 business days → investigate);
  211 pokladna reconciled separately; 243 termínované vklady. Source: `20-coa/class-2.md`,
  `.../03-bank-reconciliation-detail.md`.
- **Standard předkontace** (typical statement lines):
  | Bank line | MD | D | Source |
  |---|---|---|---|
  | Incoming customer payment | 221 | 311 (or 324 for advance) | `.../03-bank-reconciliation-detail.md` |
  | Outgoing supplier payment | 321 | 221 | same |
  | Bank fee | 568 | 221 | fees usually VAT-exempt — do not book 21% | same |
  | Interest income | 221 | 662 | same |
  | Tax payment (DPH/DPPO) | 343 / 341 / 342 | 221 | same |
  | SP/ZP remittance | 336 | 221 | same |
  | Wage payment | 331 | 221 | same |
  | Transfer between own accounts | 261 → then 221 | 221 → 261 | transit via 261 | `20-coa/class-2.md` |
  | FX revaluation at period-end | 563 (loss) / 221 | 221 / 663 (gain) | CNB denní kurz, last working day (§ 24/7 ZÚ, ČÚS 006) | `.../03-bank-reconciliation-detail.md` |
- **Numbering**: internal bank-document/statement series per account.
- **Effective-dated**: FX monetary items revalued to CNB rate at rozvahový/měsíční den; only
  monetary items (non-monetary prepaids carry historical rate).
- **GAP**: no dedicated "bank document" agenda note; coverage is derived from class-2 + month-end
  reconciliation. Payment symbols VS/KS/SS live here (matching keys), not on invoices.

## B4. Pokladna (pokladní doklad příjmový / výdajový)

- **Account**: **211** *Pokladna* (analytics per currency and per physical register). Daily
  reconciliation of physical count vs book required; overage/shortage → 668 / 569 or 331
  (employee liability). Foreign cash valued at CNB rate on transaction date; year-end
  revaluation → 563/663. **213** *Ceniny* (stamps, meal vouchers, prepaid credit). Source:
  `20-coa/class-2.md` (group 21).
- **Required fields**: § 11 ZÚ účetní doklad set; if it doubles as a VAT receipt ≤ 10,000 CZK it
  is a *zjednodušený daňový doklad* (§ 30 ZDPH) — may omit buyer name/DIČ and separate základ/VAT,
  but a plátce can still deduct if the base is derivable (not for purchases > 10,000). Source:
  `40-workflows/DPH/doklady.md` §3.
- **Standard předkontace**:
  | Doc | MD | D | Source |
  |---|---|---|---|
  | Příjmový (cash sale, plátce) | 211 | 604 + 343 | `30-predkontace/sales/01-sales-goods.md` §5 |
  | Výdajový (cash purchase) | 5xx/504 + 343 | 211 | `30-predkontace/purchase/services.md`, `.../edge-cases.md` |
  | Cash to/from bank | 261 → 211/221 | 221/211 → 261 | via transit 261 | `20-coa/class-2.md` |
  | Advance to employee | 335 | 211 (or 221) | travel; vyúčtování 512 / 335, settle 333 | `30-predkontace/purchase/advances.md` §5 |
- **Numbering**: separate číselné řady for pokladní doklad příjmový vs výdajový per register.
- **GAP**: no dedicated pokladna agenda note; POS/cash treatment appears only inside sales-goods
  §5 and class-2. PHM/fuel cash receipts, per §30, do not appear in KH (aggregate B3 only).

## B5. Interní doklad (internal document)

- **Definition / use**: vnitřní účetní doklad for entries with no external invoice —
  samovyměření (PDP / IO), corrections, accruals, depreciation, WIP change-of-state,
  reclassifications, FX revaluation, year-end postings. Still a full § 11 ZÚ účetní doklad.
  Source: `40-workflows/playbooks/nonprofit-identifikovana-osoba.md` ("vlastní interní doklad
  'Samovyměření DPH'"), `40-workflows/month-end/04-invoice-entry-and-pdz.md` (corrections via
  interní doklad), `90-meta/GLOSSARY.md` (asset card as interní dokument).
- **Standard předkontace** (representative internal entries):
  | Purpose | MD | D | Source |
  |---|---|---|---|
  | PDP / IO samovyměření | 343.100 (input) | 343.200 (output) | wash for full-deduction plátce | `30-predkontace/purchase/PDP.md` |
  | Monthly depreciation | 551 | 08x / 07x | | `30-predkontace/purchase/assets.md` |
  | WIP change of state | 121 | 611 | build-to-sell | `50-scenarios/real-estate-dev/03-WIP-and-construction.md` |
  | Aktivace vlastních nákladů | 042 / 041 | 62x (621–624) | self-built assets | `30-predkontace/purchase/assets.md` §4 |
  | Deferred tax | 592 | 481 | audited entities | `50-scenarios/DHM-lifecycle/depreciation-methods.md` §7 |
  | FX period-end revaluation | 563 | 221/311/321 (or reverse for gain 663) | monetary items | `40-workflows/month-end/03-bank-reconciliation-detail.md` |
  | Časové rozlišení | 381/518 or 384/6xx | 381/518 or 384/6xx | prepaid/deferred | FAQ-CR-001/002 |
- **Numbering**: own interní-doklad series.
- **GAP**: no single interní-doklad agenda note; usage is scattered across playbooks, month-end,
  and predkontace. Clearing account **395** *Vnitřní zúčtování* is used by some accountants for
  PDP self-assessment instead of direct 343 sub-accounts (`.../03-WIP-and-construction.md`).

---

# PART C — ASSETS (majetek)

## C1. DHM / DNM incl. automobil, pozemek, byty/stavby

- **Account map** (activation targets from 042/041):
  | Asset | Account | Depreciated? | Source |
  |---|---|---|---|
  | Pozemky (land) | **031** | **No** — never (§ 27/2/a ZDP; Decree 500/2002 § 7/3 "Pozemky se neodpisují") | `50-scenarios/DHM-lifecycle/asset-categories.md`, `50-scenarios/real-estate-dev/01-land-acquisition.md` |
  | Stavby / budovy (buildings, byty) | **021** | Yes — group 5 (30y) most; group 6 (50y) admin/hotel | `.../asset-categories.md` §2 |
  | Samostatné hmotné movité věci incl. automobil | **022** | Yes — cars group 2 (5y) | `.../asset-categories.md` §3, `.../depreciation-groups.md` |
  | Software | **013** (DNM) | Yes — per accounting plan | `.../asset-categories.md` §5 |
  | Goodwill | **015** | 60 months straight-line (§ 32a/2 ZDP) | `.../asset-categories.md` §6 |
- **Standard předkontace (acquisition lifecycle)**:
  | Step | MD | D | Source |
  |---|---|---|---|
  | Invoice receipt (DHM) | 042 + 343 | 321 | `30-predkontace/purchase/assets.md` |
  | Additional acquisition costs | 042 (+343) | 321/221 | same |
  | Activation (zařazení) | 021 / 022 / 031 / 013 | 042 (or 041 for DNM) | same |
  | Monthly depreciation | 551 | 082 (to 022) / 07x (DNM) | same |
- **Capitalization thresholds** (effective-dated):
  - DHM movable: tax threshold **80,000 CZK** vstupní cena + doba použitelnosti > 1 rok
    (§ 26/2 ZDP), stable since **2021-01-01** (Act 609/2020). Pre-2021 acquisitions
    grandfathered at **40,000 CZK**. Source: `50-scenarios/DHM-lifecycle/definition-thresholds.md`.
  - DNM: **no fixed tax threshold** — § 32a ZDP **repealed 2021-01-01** (Act 609/2020); tax
    amortization follows the entity's own accounting plan/useful life. Software ≤ 60,000 CZK
    commonly expensed to 518. Source: `.../definition-thresholds.md`, `.../asset-categories.md` §5.
  - Accounting threshold: entity sets its own (Decree 500/2002 § 7); many align to 80,000.
- **Automobil specifics** (`50-scenarios/DHM-lifecycle/asset-categories.md` §3):
  - Osobní automobil (M1): input **VAT on acquisition NOT deductible** (§ 75/2 ZDPH) — VAT
    becomes part of pořizovací cena; exception if bought for resale/rental. Depreciation group 2.
  - PHM: deductible pro-rata to business use (kniha jízd) OR paušál 5,000 CZK/měsíc (4,000 if
    mixed use), max 3 cars (§ 24/2/zt ZDP) — flagged for advisor re 2026 confirmation.
  - N1/N2 freight vehicles: full VAT deduction, no § 75 restriction.
- **Pozemek DPH**: bare land generally exempt (§ 56/1); *stavební pozemek* (zoning/permit/utility)
  is taxable 21% (§ 56/2). Building sold within 5 years of first use = taxable; § 78 input-VAT
  korekce over 10y for real estate. Source: `.../asset-categories.md` §1–2, `.../03-sales-assets.md`.

## C2. Self-constructed assets ("byty vybudované námi")

- **Rule / valuation**: in-house construction valued at **vlastní náklady** (own cost) per
  Decree 500/2002 § 48 / Act 563/1991 § 25/1/b. Direct material + direct labor + production
  overhead; **excludes** administrative overhead and selling costs. Source:
  `30-predkontace/purchase/assets.md` §4, `50-scenarios/real-estate-dev/03-WIP-and-construction.md`.
- **The build-to-own vs build-to-sell fork (critical)**:
  | Intent | During build | Final | Source |
  |---|---|---|---|
  | Build to own/rent | **042** Pořízení DHM | activate → **021** at kolaudace | `.../03-WIP-and-construction.md` §3 |
  | Build to sell (developer byty) | **121** Nedokončená výroba (inventory) | 132 zboží / derecognition on sale | `.../03-WIP-and-construction.md` §2 |
- **Předkontace**:
  | Path | MD | D | Source |
  |---|---|---|---|
  | Build-to-own, accumulate own costs | 042 | **624** *Aktivace DHM* (P&L-neutral) | `30-predkontace/purchase/assets.md` §4 |
  | Build-to-own, subcontractor/material | 042 | 321 / 111 | `.../03-WIP-and-construction.md` §3 |
  | Build-to-own, activation | 021 (byty/stavby) | 042 | same |
  | Build-to-sell, WIP change of state | 121 | **611** *Změna stavu NV* | `.../03-WIP-and-construction.md` §2 |
- **PDP on construction (§ 92e)**: subcontractor works CZ-CPA 41–43 between two plátci →
  reverse charge; developer self-assesses 343-out/343-in (or via 395 clearing); capitalize net to
  042 or 121. Source: `30-predkontace/purchase/PDP.md`, `.../03-WIP-and-construction.md` §4.
- **Real-world worked example** (advances + WIP catch-up for a residential developer, incl. the
  30M advances / 20M cost case): `99-client-work/2025-year-end-close-manual-realitni-developer.md`
  — shows reversal 602/604→324, WIP catch-up 121/611, land kept at 031, § 20a VAT on advances,
  and the § 56 23-month first-sale taxability window (effective 1.7.2025, GFŘ + Act 126/2025).
- **Effective-dated**: § 56/1 first-sale-taxable window = **23 months** after building deemed
  complete, effective **1.7.2025**; slipping past flips sale to exempt with input-VAT clawback
  risk. Source: same client-work note, Part 5.

## C3. Odpisy (depreciation) — účetní vs daňové

- **Two parallel mandatory tracks** (Act 563/1991 § 28 + Act 586/1992 § 26–33):
  | Track | Governed by | Basis | Source |
  |---|---|---|---|
  | Účetní odpisy | ZÚ + Decree 500/2002 § 56 + ČÚS 013 | actual useful life (odpisový plán); monthly from month of zařazení | `50-scenarios/DHM-lifecycle/depreciation-methods.md` §2 |
  | Daňové odpisy | ZDP § 26–33 | statutory group + rate/coefficient | `.../depreciation-methods.md` §3–4 |
- **Odpisový plán** required per asset: ID, pořizovací cena, expected useful life, method,
  annual/monthly amount, residual value policy (Decree 500/2002 § 56/3). Source: `.../depreciation-methods.md` §2.2.
- **Tax depreciation groups** (Act 586/1992 Příloha č. 1, § 30):
  | Group | Min period | Typical |
  |---|---|---|
  | 1 | 3y | PCs, servers, tools |
  | 2 | 5y | **osobní automobily**, machinery, trucks |
  | 3 | 10y | large boilers, cranes, AC systems |
  | 4 | 20y | fences, water/rail structures |
  | 5 | 30y | buildings (bytové/průmyslové), family houses |
  | 6 | 50y | administrative buildings, hotels, banks |
  Source: `50-scenarios/DHM-lifecycle/depreciation-groups.md`.
- **Methods**: rovnoměrné (§ 31, fixed year-1 vs year-2+ %) OR zrychlené (§ 32, coefficients);
  choice **irrevocable per asset** (§ 26/8). Depreciation may be **suspended** (přerušení, § 26/8).
  Linear year-1 rates: g1 20%, g2 11%, g3 5.5%, g4 2.15%, g5 1.4%, g6 1.02%. Accelerated k1:
  g1 3, g2 5, g3 10, g4 20, g5 30, g6 50. Source: `.../depreciation-groups.md` §2–3.
- **Land NOT depreciated** — neither účetně nor daňově (§ 27/2/a ZDP; Decree 500/2002 § 7/3);
  031 has no paired 081 oprávky account. Also non-depreciable: umělecká díla, nedokončený majetek,
  gifted goodwill. Source: `.../asset-categories.md` §1, `.../depreciation-groups.md` §4.
- **Odložená daň** from track difference: 592 / 481 (liability when daňová ZC < účetní ZC);
  mandatory for audited (large/medium) entities, optional for small/micro (ČÚS 003). DPPO rate 21%
  (2026). Source: `.../depreciation-methods.md` §7.
- **Mimořádné odpisy (§ 30a)** — effective-dated: 2026 scope is **only bezemisní vozidla**
  acquired **2024-01-01–2028-12-31** (60%/40% over 24 months, first owner). The COVID-era group
  1/2 version (Act 609/2020, 2020–2021 acquisitions) **expired** — not available for ordinary 2026
  equipment. Source: `.../depreciation-methods.md` §5 (confidence high, primary-source verified).

---

# PART D — VAT (plátce)

- **Rates** (effective 2024-01-01, Act 349/2023 merged old 15%+10% into single 12%; no 2026
  change): **21%** základní (§ 47/1/a), **12%** snížená (§ 47/1/b). **No 0%/nulová sazba exists.**
  Books/e-books/audiobooks = **osvobozeno s nárokem na odpočet** (§ 71i), DAP ř. 26 — NOT a rate.
  Newspapers (CN 4902) = 12% (Příloha č. 3). Source: `40-workflows/DPH/rates-and-exemptions.md`
  (confidence high, primary-source verified). Annex map: Příloha 2 = reduced-rate services,
  Příloha 3 = reduced-rate goods, Příloha 5/6 = PDP lists.
- **Reverse charge / přenesená daňová povinnost (PDP)**:
  - Domestic § 92a–92e: stavební/montážní práce (§ 92e, CZ-CPA 41–43), zlato (§ 92b), emisní
    povolenky (§ 92c), Příloha 5 goods > 100,000 CZK. Both parties must be plátci; neplátce/IO
    excluded. Supplier invoices **without VAT** + text *"Daň odvede zákazník"* (§ 29/2/c).
  - Buyer samovyměří: MD 343.100 input / D 343.200 output (wash for full-deduction plátce). Pays
    only net to supplier. DAP ř. 10 (output) + ř. 43 (input); KH **B1** (buyer) / **A1** (seller).
  Source: `30-predkontace/purchase/PDP.md`, `40-workflows/DPH/kh-sh.md`.
- **VAT accounts (343)**: single synthetic 343 *Daň z přidané hodnoty* with analytics —
  343.100 vstup (input), 343.200 výstup (output). Period-end balance = payable (credit) or
  nadměrný odpočet / refund (debit). Reported on Rozvaha C.II.2.4 (debit) or Pasiva daňové
  závazky (credit). Source: `40-workflows/DPH/cycles.md` §3, `90-meta/INDEX-by-rozvaha-row.md`.
- **Document fields that drive KH / přiznání classification** (capture these — no XML now):
  | Field | Drives |
  |---|---|
  | Buyer/supplier **DIČ** + plátce status | A4 vs A5 / B2 vs B3; PDP eligibility |
  | Invoice **gross amount vs 10,000 CZK** threshold | A4/B2 (per-invoice) vs A5/B3 (aggregate) |
  | **DUZP** | tax period assignment (month/quarter) |
  | **Sazba daně** (21/12/exempt/PDP) | DAP ř. 1/2/10/26; základ split per rate |
  | **Regime** (domestic / EU ICD/ICP / export/import / PDP) | A1/A2/A3/B1; SH; DAP output/input blocks |
  | **datum přijetí** (FP) | deduction period (§ 73, receipt-date rule) |
  Source: `40-workflows/DPH/kh-sh.md`, `30-predkontace/sales/01-sales-goods.md`,
  `repo:vat-currency-and-corrections.md`.
- **Filing cycles** (§ 99): monthly if turnover ≥ **10,000,000 CZK** prior year (mandatory);
  quarterly if below (needs ≥ 12 months as plátce; new plátci monthly first 12 months, § 99b).
  DAP + KH + SH all due **25th of following month/quarter**; KH electronic-only. Legal person
  files KH monthly even on a quarterly VAT period. Source: `40-workflows/DPH/cycles.md`,
  `40-workflows/DPH/kh-sh.md`, `repo:vat-currency-and-corrections.md`.
- **VAT currency rule**: the VAT amount must be stated in **CZK** on the tax document even when
  other amounts are foreign currency (§ 29/1/l). Source: `repo:vat-currency-and-corrections.md`.
- **Retention**: daňové doklady **10 years** (§ 35a ZDPH); assets under úprava odpočtu keep records
  for the full adjustment period (5y movables / 10y real estate). Note ZÚ baseline differs:
  § 31(2) gives 10y for statements, **5y** for documents/books/inventories — the longer VAT period
  governs for tax documents. Source: `40-workflows/DPH/doklady.md`, `40-workflows/DPH/cycles.md`,
  `repo:retention-evidence-and-gates.md`.

---

# Conflicts & effective-dated watchlist

- **Retention**: vault `statutory-books.md` (5y inventarizační soupisy, § 31 ZÚ) vs `doklady.md`
  (10y daňové doklady, § 35a ZDPH) vs `repo:retention-evidence-and-gates.md` (§ 31(2): 10y
  statements / 5y documents). All consistent once you separate the ZÚ baseline from the ZDPH
  tax-document rule; § 32 legal holds can extend both. Use 10y as practical minimum.
- **KH penalty ceiling**: § 101h max 50,000 CZK (late/výzva) vs § 101i up to 500,000 CZK (non-
  filing/incorrect data). Vault claims-manifest row 4 (500,000) and Pohoda cross-ref (50,000)
  reconciled: two different provisions. Advisor to confirm post-2025 penalty ladder (Act 461/2024).
  Source: `40-workflows/DPH/kh-sh.md`.
- **Turnover thresholds are two different rules**: 10M CZK = monthly VAT period (§ 99 ZDPH);
  25M CZK = mandatory accounting-entity trigger for FO (§ 1(2)(e) ZÚ, 2026 consolidation,
  `repo:applicability-documents-and-books.md`). Do not conflate.
- **Effective-dated rules to version**: VAT 21/12 since 2024-01-01; DHM 80,000 since 2021-01-01
  (pre-2021 40,000); DNM § 32a repealed 2021-01-01; § 30a mimořádné = bezemisní vozidla 2024–2028;
  daň z nabytí abolished 2020-12-26; § 56 real-estate 23-month window since 1.7.2025;
  § 73 receipt-date deduction + 2-year cutoff since 1.1.2025.

# Coverage gaps (where the vault is silent or thin)

1. **VS / KS / SS symboly** — not documented as invoice fields (legally they are bank
   payment-matching references, not § 29 content). Model as payment attributes.
2. **Číselné řady** — no dedicated note; § 11/§ 29 require an identifier, not a gapless sequence.
   Numbering policy is an accountant-approved design decision (`repo:vat-currency-and-corrections.md`).
3. **Banka / Pokladna / Interní doklad** — no dedicated per-agenda notes; content is reconstructed
   from `20-coa/class-2.md`, `40-workflows/month-end/03-bank-reconciliation-detail.md`, sales-goods
   §5, and scattered playbooks.
4. **Verbatim statutory statement layouts** — vault gives account→row *mappings*
   (`90-meta/INDEX-by-rozvaha-row.md`, `INDEX-by-vzz-row.md`) but not the literal Příloha 1/2 forms;
   verifier flags W7-V1..V5 note collisions/aggregations needing cleanup for real statement
   generation. VZZ účelové (Příloha 3) not mapped at all.
5. **Confidence** — most předkontace notes are "medium" (single primary source, no second
   cross-check); rates, § 30a mimořádné odpisy, and threshold repeals are the "high"-confidence
   islands.
