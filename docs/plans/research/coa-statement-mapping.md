# Czech statement-row mapping for cz_coa.json (Rozvaha + VZZ druhové)

- **Generated:** 2026-07-21
- **Chart mapped:** `czech_accounting/czech_accounting/chart_of_accounts/cz_coa.json` (314 posting-account leaves).
- **Companion machine file:** [`coa-statement-mapping.json`](./coa-statement-mapping.json) - one object per posting account (`rozvaha_row`, `vzz_row`, `category_code`, `category_label`).
- **category_code convention:** `rozvaha-<aktiva|pasiva>-<rowslug>`, `vzz-<rowslug>`, or `off-<kind>`. The side
  segment is included on Rozvaha codes (extending the task's `rozvaha-b-ii-2` example) because bare row codes
  collide across sides - e.g. aktiva `D.1.` (Náklady příštích období) vs pasiva `D.1.` (Výdaje příštích období),
  and roman `I.` vs letter `I.` in the VZZ. Codes are therefore globally unique.
- **Statement scheme:** Vyhláška (Decree) **500/2002 Sb.**, as amended (consolidation effective 2024-01-01). **Příloha č. 1** = Rozvaha (plný rozsah). **Příloha č. 2** = Výkaz zisku a ztráty, druhové členění.
- **Status:** draft for accountant sign-off. Statutory outputs must be reviewed before real use (repo domain invariant).

## 1. Sources

- **Account -> row mapping logic (primary):** accountingAfframe vault -
  `90-meta/ACCOUNT-INDEX.csv` (per-account rozvaha_row / vzz_row, the granular source),
  `90-meta/INDEX-by-rozvaha-row.md` (Příloha 1 reverse index, "70 rozvaha rows / 236 accounts"),
  `90-meta/INDEX-by-vzz-row.md` (Příloha 2 reverse index, "19 VZZ rows"),
  cross-checked against `20-coa/class-0.md` .. `class-8-9.md` and
  `czech_accounting/docs/plans/research/cz-law-requirements.md`.
- **Statutory row codes + labels (authoritative for the scheme):** current Decree 500/2002 Příloha 1 and 2.
  Top-level structure verified against cs.wikipedia.org/wiki/Rozvaha, money.cz, and the uctovani.net
  VZZ druhové form (PDF). No Russian-language sources used.

## 2. Row codes: decree wins over KB (important)

The vault indexes were built from an **older / simplified** statement layout. Where they diverge from the
current Decree 500/2002 wording, this mapping follows the **decree** (per task rule). The material divergences:

1. **Pasiva restructure (post-2016 decree).** The KB `INDEX-by-rozvaha-row.md` uses the pre-2016 pasiva tree
   (`A. Vlastní kapitál` / `B. Cizí zdroje` with `B.I Rezervy`, `B.II Závazky`, `C.1/C.2 Časové rozlišení`).
   The current decree is: **A. Vlastní kapitál** (A.I-A.VI) / **B. Rezervy** (B.1-B.4) /
   **C. Závazky** (C.I Dlouhodobé C.I.1-9, C.II Krátkodobé C.II.1-8 with C.II.8.x sub-lines) /
   **D. Časové rozlišení pasiv** (D.1 Výdaje, D.2 Výnosy p.o.). All liability/equity accounts use the new codes.
2. **VZZ druhové (Příloha 2) rebuilt.** The KB `INDEX-by-vzz-row.md` uses non-statutory codes
   (e.g. `G/H` = ostatní finanční výnosy/náklady, `Q` = daň, `R` = převod podílu, `A.1` = materiál+energie).
   Current decree order used here: I, II, **A.1** Náklady na prodané zboží / **A.2** Spotřeba materiálu a energie /
   **A.3** Služby, B, C, **D.1** Mzdové n. / **D.2.1** SZ+ZP / **D.2.2** Ostatní, **E.1.1/E.2/E.3** Úpravy hodnot,
   III.1-III.3, **F.1-F.5**, IV/V/VI, **G/H/I/J/K** (financial), **L.1/L.2** Daň z příjmů, **M** Převod podílu.
3. **Balance-sheet placements corrected vs KB.** `388` Dohadné účty aktivní -> **C.II.2.4.5** (not D.3);
   `389` Dohadné účty pasivní -> **C.II.8.6** (not C.1); `252` Vlastní podíly -> **A.I.2** (contra-equity).
4. **Account-name divergence in this chart.** In cz_coa.json, `547` = "Mimořádné provozní náklady" and
   `649` = "Mimořádné provozní výnosy" (the "mimořádné" section was abolished in 2016). They are mapped to
   **F.5** / **III.3** by their names in this chart - the KB CSV, keyed on different names for 547
   (tvorba zákonných OP), disagrees. `623`/`624` in the file are DNM/DHM (standard order), not the
   task-brief order; both map to **C. Aktivace** regardless.
5. **513 Reprezentace -> A.3 Služby** (účtová skupina 51), not F; its tax non-deductibility is a tax matter,
   not a statement placement. **552/554/555** (rezervy, KNPO) -> **F.4**, not E.

## 3. Coverage

- **Posting accounts in cz_coa.json:** **314** (all leaves with `account_number`, no children).
- **Mapped:** **314 / 314 (100%)**. No posting account left without a category.
- **Stream 1 additions already present in the file (mapped):** 343.100 (DPH na vstupu -> C.II.2.4.3),
  343.200 (DPH na výstupu -> C.II.8.5), 611-614 (Změna stavu -> VZZ B), 621-624 (Aktivace -> VZZ C).
  `343` itself is now a **group** (parent of 343.100/343.200) and is correctly excluded (no posting to groups).
- **Distinct categories:** **133** total = 53 Rozvaha-Aktiva rows +
  47 Rozvaha-Pasiva rows + 31 VZZ rows + 2 off-statement buckets.

### 3a. Accounts deliberately NOT on any statement (11)
These are technical / internal accounts. They map to `rozvaha_row: null, vzz_row: null` and an off-statement
category. This is correct, not a gap - they net to zero or exist only for the year-end close:

- **Závěrkové účty:** 700, 701, 702, 710 (počáteční/konečný účet rozvažný, účet zisků a ztrát).
- **Vnitřní / převodové účty:** 395, 398, 597, 598, 690, 697, 698 (vnitřní zúčtování, spojovací účet, vnitropodnikové převody nákladů/výnosů).

### 3b. Accounts the KB (ACCOUNT-INDEX.csv) does NOT map - resolved here by decree logic (87)
The vault's per-account CSV is silent on these; each was mapped from the decree structure + the group it sits in.
Most are the ERPNext "x0" group-summary placeholder accounts (normally carry no balance); mapped to the
**aggregate section row** of their skupina. Flag for accountant confirmation:

010, 020, 030, 040, 050, 060, 068, 070, 080, 090, 097, 098, 110, 120, 130, 150, 153, 190, 197, 198, 199, 210, 220, 230, 233, 240, 250, 254, 260, 290, 310, 320, 330, 340, 343.100, 343.200, 350, 352, 360, 362, 367, 368, 370, 380, 390, 410, 416, 417, 420, 426, 430, 432, 450, 452, 460, 462, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 565, 570, 580, 581, 582, 583, 584, 585, 586, 587, 588, 590, 599, 600, 640, 643, 660, 669, 690, 700, 221001

### 3c. Balance-nature-dependent accounts (single account, two possible rows)
Mapped to a **default** row with the alternative noted; a report generator must switch on the period-end
balance sign (systemic caveat, not resolvable statically):

- **Daňové účty (debit = pohledávka / credit = závazek):** 341, 342, 343.100/343.200, 345, 346, 347 -
  default as recorded (input VAT -> aktiva C.II.2.4.3; the rest -> pasiva C.II.8.5 unless overpaid -> C.II.2.4.3).
- **Odložená daň:** 480, 481 - default C.I.8 (závazek); asset side -> C.II.1.4 (Odložená daňová pohledávka).
- **Deriváty / pevné termínové operace:** 373 - C.II.2.4.6 (asset) or C.II.8.7 (liability).
- **Krátkodobé vs dlouhodobé reclassification:** 311, 321, 324, 351, 352, 361, 362, 475, 462, ... default to
  **krátkodobé** rows; the same account moves to the dlouhodobé block (C.II.1.x / C.I.x) by residual maturity.
  The KB flags this too (W7-V3) and does not resolve it mechanically.

### 3d. Finanční VZZ split (podíly vs cenné papíry)
- `561` Prodané CP a podíly -> **K** (default); the participation-sale part belongs to **G**.
- `661` Tržby z prodeje CP a podílů -> **VII** (default); the participation part belongs to **IV**.
- `665` Výnosy z DFM -> **IV.2** (dividends from participations); interest-type parts may fall under **V**.

## 4. Distinct Account Category list (for Stream 3 report templates)

Order = statutory order within each statement. `# accounts` = how many posting accounts feed the row in this chart.
Contra accounts (oprávky 07x/08x, opravné položky 09x/19x/29x/39x) share their gross asset's row and are shown
net (brutto / korekce / netto) inside that row.

### 4a. Rozvaha - AKTIVA (Příloha 1)

| category_code | statement | row | statutory label | # accounts | accounts |
|---|---|---|---|---:|---|
| `rozvaha-aktiva-a` | Rozvaha · Aktiva | A. | Pohledávky za upsaný základní kapitál | 1 | 353 |
| `rozvaha-aktiva-b-i` | Rozvaha · Aktiva | B.I. | Dlouhodobý nehmotný majetek (souhrn) | 3 | 010, 070, 091 |
| `rozvaha-aktiva-b-i-1` | Rozvaha · Aktiva | B.I.1. | Nehmotné výsledky vývoje | 2 | 012, 072 |
| `rozvaha-aktiva-b-i-2-1` | Rozvaha · Aktiva | B.I.2.1. | Software | 2 | 013, 073 |
| `rozvaha-aktiva-b-i-2-2` | Rozvaha · Aktiva | B.I.2.2. | Ostatní ocenitelná práva | 2 | 014, 074 |
| `rozvaha-aktiva-b-i-3` | Rozvaha · Aktiva | B.I.3. | Goodwill | 2 | 015, 075 |
| `rozvaha-aktiva-b-i-4` | Rozvaha · Aktiva | B.I.4. | Ostatní dlouhodobý nehmotný majetek | 2 | 019, 079 |
| `rozvaha-aktiva-b-i-5-1` | Rozvaha · Aktiva | B.I.5.1. | Poskytnuté zálohy na dlouhodobý nehmotný majetek | 1 | 051 |
| `rozvaha-aktiva-b-i-5-2` | Rozvaha · Aktiva | B.I.5.2. | Nedokončený dlouhodobý nehmotný majetek | 2 | 041, 093 |
| `rozvaha-aktiva-b-ii` | Rozvaha · Aktiva | B.II. | Dlouhodobý hmotný majetek (souhrn) | 6 | 020, 030, 040, 080, 090, 092 |
| `rozvaha-aktiva-b-ii-1-1` | Rozvaha · Aktiva | B.II.1.1. | Pozemky | 1 | 031 |
| `rozvaha-aktiva-b-ii-1-2` | Rozvaha · Aktiva | B.II.1.2. | Stavby | 2 | 021, 081 |
| `rozvaha-aktiva-b-ii-2` | Rozvaha · Aktiva | B.II.2. | Hmotné movité věci a jejich soubory | 2 | 022, 082 |
| `rozvaha-aktiva-b-ii-3` | Rozvaha · Aktiva | B.II.3. | Oceňovací rozdíl k nabytému majetku | 2 | 097, 098 |
| `rozvaha-aktiva-b-ii-4-1` | Rozvaha · Aktiva | B.II.4.1. | Pěstitelské celky trvalých porostů | 2 | 025, 085 |
| `rozvaha-aktiva-b-ii-4-2` | Rozvaha · Aktiva | B.II.4.2. | Dospělá zvířata a jejich skupiny | 2 | 026, 086 |
| `rozvaha-aktiva-b-ii-4-3` | Rozvaha · Aktiva | B.II.4.3. | Jiný dlouhodobý hmotný majetek | 3 | 029, 032, 089 |
| `rozvaha-aktiva-b-ii-5-1` | Rozvaha · Aktiva | B.II.5.1. | Poskytnuté zálohy na dlouhodobý hmotný majetek | 3 | 050, 052, 095 |
| `rozvaha-aktiva-b-ii-5-2` | Rozvaha · Aktiva | B.II.5.2. | Nedokončený dlouhodobý hmotný majetek | 2 | 042, 094 |
| `rozvaha-aktiva-b-iii` | Rozvaha · Aktiva | B.III. | Dlouhodobý finanční majetek (souhrn) | 2 | 060, 096 |
| `rozvaha-aktiva-b-iii-1` | Rozvaha · Aktiva | B.III.1. | Podíly – ovládaná nebo ovládající osoba | 1 | 061 |
| `rozvaha-aktiva-b-iii-2` | Rozvaha · Aktiva | B.III.2. | Zápůjčky a úvěry – ovládaná nebo ovládající osoba | 1 | 066 |
| `rozvaha-aktiva-b-iii-3` | Rozvaha · Aktiva | B.III.3. | Podíly – podstatný vliv | 1 | 062 |
| `rozvaha-aktiva-b-iii-4` | Rozvaha · Aktiva | B.III.4. | Zápůjčky a úvěry – podstatný vliv | 1 | 067 |
| `rozvaha-aktiva-b-iii-5` | Rozvaha · Aktiva | B.III.5. | Ostatní dlouhodobé cenné papíry a podíly | 2 | 063, 065 |
| `rozvaha-aktiva-b-iii-6` | Rozvaha · Aktiva | B.III.6. | Zápůjčky a úvěry – ostatní | 1 | 068 |
| `rozvaha-aktiva-b-iii-7-1` | Rozvaha · Aktiva | B.III.7.1. | Jiný dlouhodobý finanční majetek | 2 | 043, 069 |
| `rozvaha-aktiva-b-iii-7-2` | Rozvaha · Aktiva | B.III.7.2. | Poskytnuté zálohy na dlouhodobý finanční majetek | 1 | 053 |
| `rozvaha-aktiva-c-i` | Rozvaha · Aktiva | C.I. | Zásoby (souhrn) | 2 | 120, 190 |
| `rozvaha-aktiva-c-i-1` | Rozvaha · Aktiva | C.I.1. | Materiál | 5 | 110, 111, 112, 119, 191 |
| `rozvaha-aktiva-c-i-2` | Rozvaha · Aktiva | C.I.2. | Nedokončená výroba a polotovary | 4 | 121, 122, 192, 193 |
| `rozvaha-aktiva-c-i-3-1` | Rozvaha · Aktiva | C.I.3.1. | Výrobky | 2 | 123, 194 |
| `rozvaha-aktiva-c-i-3-2` | Rozvaha · Aktiva | C.I.3.2. | Zboží | 5 | 130, 131, 132, 139, 196 |
| `rozvaha-aktiva-c-i-4` | Rozvaha · Aktiva | C.I.4. | Mladá a ostatní zvířata a jejich skupiny | 2 | 124, 195 |
| `rozvaha-aktiva-c-i-5` | Rozvaha · Aktiva | C.I.5. | Poskytnuté zálohy na zásoby | 7 | 150, 151, 152, 153, 197, 198, 199 |
| `rozvaha-aktiva-c-ii` | Rozvaha · Aktiva | C.II. | Pohledávky (souhrn) | 3 | 310, 350, 390 |
| `rozvaha-aktiva-c-ii-2-1` | Rozvaha · Aktiva | C.II.2.1. | Pohledávky z obchodních vztahů (krátkodobé) | 3 | 311, 312, 391 |
| `rozvaha-aktiva-c-ii-2-2` | Rozvaha · Aktiva | C.II.2.2. | Pohledávky – ovládaná nebo ovládající osoba (krátkodobé) | 1 | 351 |
| `rozvaha-aktiva-c-ii-2-3` | Rozvaha · Aktiva | C.II.2.3. | Pohledávky – podstatný vliv (krátkodobé) | 1 | 352 |
| `rozvaha-aktiva-c-ii-2-4-1` | Rozvaha · Aktiva | C.II.2.4.1. | Pohledávky za společníky (krátkodobé) | 3 | 354, 355, 358 |
| `rozvaha-aktiva-c-ii-2-4-3` | Rozvaha · Aktiva | C.II.2.4.3. | Stát – daňové pohledávky | 1 | 343.100 |
| `rozvaha-aktiva-c-ii-2-4-4` | Rozvaha · Aktiva | C.II.2.4.4. | Krátkodobé poskytnuté zálohy | 1 | 314 |
| `rozvaha-aktiva-c-ii-2-4-5` | Rozvaha · Aktiva | C.II.2.4.5. | Dohadné účty aktivní | 1 | 388 |
| `rozvaha-aktiva-c-ii-2-4-6` | Rozvaha · Aktiva | C.II.2.4.6. | Jiné pohledávky | 9 | 313, 315, 335, 370, 371, 373, 374, 375, 378 |
| `rozvaha-aktiva-c-iii` | Rozvaha · Aktiva | C.III. | Krátkodobý finanční majetek (souhrn) | 2 | 250, 290 |
| `rozvaha-aktiva-c-iii-1` | Rozvaha · Aktiva | C.III.1. | Podíly – ovládaná nebo ovládající osoba | 1 | 254 |
| `rozvaha-aktiva-c-iii-2` | Rozvaha · Aktiva | C.III.2. | Ostatní krátkodobý finanční majetek | 8 | 251, 253, 255, 256, 257, 259, 291, 376 |
| `rozvaha-aktiva-c-iv-1` | Rozvaha · Aktiva | C.IV.1. | Peněžní prostředky v pokladně | 3 | 210, 211, 213 |
| `rozvaha-aktiva-c-iv-2` | Rozvaha · Aktiva | C.IV.2. | Peněžní prostředky na účtech | 4 | 220, 260, 261, 221001 |
| `rozvaha-aktiva-d` | Rozvaha · Aktiva | D. | Časové rozlišení aktiv (souhrn) | 1 | 380 |
| `rozvaha-aktiva-d-1` | Rozvaha · Aktiva | D.1. | Náklady příštích období | 1 | 381 |
| `rozvaha-aktiva-d-2` | Rozvaha · Aktiva | D.2. | Komplexní náklady příštích období | 1 | 382 |
| `rozvaha-aktiva-d-3` | Rozvaha · Aktiva | D.3. | Příjmy příštích období | 1 | 385 |

### 4b. Rozvaha - PASIVA (Příloha 1)

| category_code | statement | row | statutory label | # accounts | accounts |
|---|---|---|---|---:|---|
| `rozvaha-pasiva-a` | Rozvaha · Pasiva | A. | Vlastní kapitál (souhrn) | 2 | 490, 491 |
| `rozvaha-pasiva-a-i-1` | Rozvaha · Pasiva | A.I.1. | Základní kapitál | 2 | 410, 411 |
| `rozvaha-pasiva-a-i-2` | Rozvaha · Pasiva | A.I.2. | Vlastní podíly (-) | 1 | 252 |
| `rozvaha-pasiva-a-i-3` | Rozvaha · Pasiva | A.I.3. | Změny základního kapitálu | 1 | 419 |
| `rozvaha-pasiva-a-ii-1` | Rozvaha · Pasiva | A.II.1. | Ážio | 1 | 412 |
| `rozvaha-pasiva-a-ii-2-1` | Rozvaha · Pasiva | A.II.2.1. | Ostatní kapitálové fondy | 1 | 413 |
| `rozvaha-pasiva-a-ii-2-2` | Rozvaha · Pasiva | A.II.2.2. | Oceňovací rozdíly z přecenění majetku a závazků (+/-) | 1 | 414 |
| `rozvaha-pasiva-a-ii-2-3` | Rozvaha · Pasiva | A.II.2.3. | Oceňovací rozdíly z přecenění při přeměnách obchodních korporací (+/-) | 1 | 418 |
| `rozvaha-pasiva-a-ii-2-4` | Rozvaha · Pasiva | A.II.2.4. | Rozdíly z přeměn obchodních korporací (+/-) | 1 | 417 |
| `rozvaha-pasiva-a-ii-2-5` | Rozvaha · Pasiva | A.II.2.5. | Rozdíly z ocenění při přeměnách obchodních korporací (+/-) | 1 | 416 |
| `rozvaha-pasiva-a-iii-1` | Rozvaha · Pasiva | A.III.1. | Ostatní rezervní fondy | 3 | 420, 421, 422 |
| `rozvaha-pasiva-a-iii-2` | Rozvaha · Pasiva | A.III.2. | Statutární a ostatní fondy | 2 | 423, 427 |
| `rozvaha-pasiva-a-iv-1` | Rozvaha · Pasiva | A.IV.1. | Nerozdělený zisk nebo neuhrazená ztráta minulých let (+/-) | 2 | 428, 429 |
| `rozvaha-pasiva-a-iv-2` | Rozvaha · Pasiva | A.IV.2. | Jiný výsledek hospodaření minulých let (+/-) | 1 | 426 |
| `rozvaha-pasiva-a-v` | Rozvaha · Pasiva | A.V. | Výsledek hospodaření běžného účetního období (+/-) | 2 | 430, 431 |
| `rozvaha-pasiva-a-vi` | Rozvaha · Pasiva | A.VI. | Rozhodnuto o zálohové výplatě podílu na zisku (-) | 1 | 432 |
| `rozvaha-pasiva-b` | Rozvaha · Pasiva | B. | Rezervy (souhrn) | 1 | 450 |
| `rozvaha-pasiva-b-1` | Rozvaha · Pasiva | B.1. | Rezerva na důchody a podobné závazky | 1 | 452 |
| `rozvaha-pasiva-b-2` | Rozvaha · Pasiva | B.2. | Rezerva na daň z příjmů | 1 | 453 |
| `rozvaha-pasiva-b-3` | Rozvaha · Pasiva | B.3. | Rezervy podle zvláštních právních předpisů | 1 | 451 |
| `rozvaha-pasiva-b-4` | Rozvaha · Pasiva | B.4. | Ostatní rezervy | 1 | 459 |
| `rozvaha-pasiva-c-i` | Rozvaha · Pasiva | C.I. | Dlouhodobé závazky (souhrn) | 1 | 470 |
| `rozvaha-pasiva-c-i-1` | Rozvaha · Pasiva | C.I.1. | Vydané dluhopisy (dlouhodobé) | 1 | 473 |
| `rozvaha-pasiva-c-i-2` | Rozvaha · Pasiva | C.I.2. | Závazky k úvěrovým institucím (dlouhodobé) | 2 | 460, 461 |
| `rozvaha-pasiva-c-i-3` | Rozvaha · Pasiva | C.I.3. | Dlouhodobé přijaté zálohy | 1 | 475 |
| `rozvaha-pasiva-c-i-5` | Rozvaha · Pasiva | C.I.5. | Dlouhodobé směnky k úhradě | 1 | 478 |
| `rozvaha-pasiva-c-i-6` | Rozvaha · Pasiva | C.I.6. | Závazky – ovládaná nebo ovládající osoba (dlouhodobé) | 1 | 471 |
| `rozvaha-pasiva-c-i-7` | Rozvaha · Pasiva | C.I.7. | Závazky – podstatný vliv (dlouhodobé) | 1 | 472 |
| `rozvaha-pasiva-c-i-8` | Rozvaha · Pasiva | C.I.8. | Odložený daňový závazek | 2 | 480, 481 |
| `rozvaha-pasiva-c-i-9-3` | Rozvaha · Pasiva | C.I.9.3. | Jiné závazky (dlouhodobé) | 3 | 462, 474, 479 |
| `rozvaha-pasiva-c-ii` | Rozvaha · Pasiva | C.II. | Krátkodobé závazky (souhrn) | 1 | 320 |
| `rozvaha-pasiva-c-ii-1` | Rozvaha · Pasiva | C.II.1. | Vydané dluhopisy (krátkodobé) | 1 | 241 |
| `rozvaha-pasiva-c-ii-2` | Rozvaha · Pasiva | C.II.2. | Závazky k úvěrovým institucím (krátkodobé) | 3 | 230, 231, 232 |
| `rozvaha-pasiva-c-ii-3` | Rozvaha · Pasiva | C.II.3. | Krátkodobé přijaté zálohy | 1 | 324 |
| `rozvaha-pasiva-c-ii-4` | Rozvaha · Pasiva | C.II.4. | Závazky z obchodních vztahů (krátkodobé) | 1 | 321 |
| `rozvaha-pasiva-c-ii-5` | Rozvaha · Pasiva | C.II.5. | Krátkodobé směnky k úhradě | 1 | 322 |
| `rozvaha-pasiva-c-ii-6` | Rozvaha · Pasiva | C.II.6. | Závazky – ovládaná nebo ovládající osoba (krátkodobé) | 1 | 361 |
| `rozvaha-pasiva-c-ii-7` | Rozvaha · Pasiva | C.II.7. | Závazky – podstatný vliv (krátkodobé) | 1 | 362 |
| `rozvaha-pasiva-c-ii-8-1` | Rozvaha · Pasiva | C.II.8.1. | Závazky ke společníkům | 5 | 360, 364, 365, 366, 368 |
| `rozvaha-pasiva-c-ii-8-2` | Rozvaha · Pasiva | C.II.8.2. | Krátkodobé finanční výpomoci | 3 | 233, 240, 249 |
| `rozvaha-pasiva-c-ii-8-3` | Rozvaha · Pasiva | C.II.8.3. | Závazky k zaměstnancům | 3 | 330, 331, 333 |
| `rozvaha-pasiva-c-ii-8-4` | Rozvaha · Pasiva | C.II.8.4. | Závazky ze sociálního zabezpečení a zdravotního pojištění | 1 | 336 |
| `rozvaha-pasiva-c-ii-8-5` | Rozvaha · Pasiva | C.II.8.5. | Stát – daňové závazky a dotace | 7 | 340, 341, 342, 343.200, 345, 346, 347 |
| `rozvaha-pasiva-c-ii-8-6` | Rozvaha · Pasiva | C.II.8.6. | Dohadné účty pasivní | 1 | 389 |
| `rozvaha-pasiva-c-ii-8-7` | Rozvaha · Pasiva | C.II.8.7. | Jiné závazky | 5 | 325, 367, 372, 377, 379 |
| `rozvaha-pasiva-d-1` | Rozvaha · Pasiva | D.1. | Výdaje příštích období | 1 | 383 |
| `rozvaha-pasiva-d-2` | Rozvaha · Pasiva | D.2. | Výnosy příštích období | 1 | 384 |

### 4c. Výkaz zisku a ztráty - druhové členění (Příloha 2)

Note: row `I.` appears twice in the decree - Roman **I.** (revenue, Tržby z prodeje výrobků a služeb,
`vzz-i`) and letter **I.** (Úpravy hodnot a rezervy ve finanční oblasti, `vzz-i-fin`). The `category_code`
disambiguates; the printed row string is "I." for both.

| category_code | statement | row | statutory label | # accounts | accounts |
|---|---|---|---|---:|---|
| `vzz-i` | VZZ | I. | Tržby z prodeje výrobků a služeb | 3 | 600, 601, 602 |
| `vzz-ii` | VZZ | II. | Tržby za prodej zboží | 1 | 604 |
| `vzz-a` | VZZ | A. | Výkonová spotřeba (souhrn) | 1 | 500 |
| `vzz-a-1` | VZZ | A.1. | Náklady vynaložené na prodané zboží | 1 | 504 |
| `vzz-a-2` | VZZ | A.2. | Spotřeba materiálu a energie | 3 | 501, 502, 503 |
| `vzz-a-3` | VZZ | A.3. | Služby | 5 | 510, 511, 512, 513, 518 |
| `vzz-b` | VZZ | B. | Změna stavu zásob vlastní činnosti (+/-) | 9 | 580, 581, 582, 583, 584, 611, 612, 613, 614 |
| `vzz-c` | VZZ | C. | Aktivace (-) | 8 | 585, 586, 587, 588, 621, 622, 623, 624 |
| `vzz-d` | VZZ | D. | Osobní náklady (souhrn) | 1 | 520 |
| `vzz-d-1` | VZZ | D.1. | Mzdové náklady | 3 | 521, 522, 523 |
| `vzz-d-2-1` | VZZ | D.2.1. | Náklady na sociální zabezpečení a zdravotní pojištění | 3 | 524, 525, 526 |
| `vzz-d-2-2` | VZZ | D.2.2. | Ostatní náklady (osobní) | 2 | 527, 528 |
| `vzz-e-1-1` | VZZ | E.1.1. | Úpravy hodnot dlouhodobého nehmotného a hmotného majetku – trvalé | 3 | 550, 551, 557 |
| `vzz-e-3` | VZZ | E.3. | Úpravy hodnot pohledávek | 2 | 558, 559 |
| `vzz-iii-1` | VZZ | III.1. | Tržby z prodaného dlouhodobého majetku | 1 | 641 |
| `vzz-iii-2` | VZZ | III.2. | Tržby z prodaného materiálu | 1 | 642 |
| `vzz-iii-3` | VZZ | III.3. | Jiné provozní výnosy | 6 | 640, 643, 644, 646, 648, 649 |
| `vzz-f-1` | VZZ | F.1. | Zůstatková cena prodaného dlouhodobého majetku | 1 | 541 |
| `vzz-f-2` | VZZ | F.2. | Prodaný materiál | 1 | 542 |
| `vzz-f-3` | VZZ | F.3. | Daně a poplatky (v provozní oblasti) | 4 | 530, 531, 532, 538 |
| `vzz-f-4` | VZZ | F.4. | Rezervy v provozní oblasti a komplexní náklady příštích období | 3 | 552, 554, 555 |
| `vzz-f-5` | VZZ | F.5. | Jiné provozní náklady | 8 | 540, 543, 544, 545, 546, 547, 548, 549 |
| `vzz-iv-2` | VZZ | IV.2. | Ostatní výnosy z podílů | 1 | 665 |
| `vzz-vi-2` | VZZ | VI.2. | Ostatní výnosové úroky a podobné výnosy | 1 | 662 |
| `vzz-i-fin` | VZZ | I. | Úpravy hodnot a rezervy ve finanční oblasti | 3 | 570, 574, 579 |
| `vzz-j-2` | VZZ | J.2. | Ostatní nákladové úroky a podobné náklady | 1 | 562 |
| `vzz-vii` | VZZ | VII. | Ostatní finanční výnosy | 8 | 660, 661, 663, 664, 666, 667, 668, 669 |
| `vzz-k` | VZZ | K. | Ostatní finanční náklady | 9 | 560, 561, 563, 564, 565, 566, 567, 568, 569 |
| `vzz-l-1` | VZZ | L.1. | Daň z příjmů splatná | 4 | 590, 591, 595, 599 |
| `vzz-l-2` | VZZ | L.2. | Daň z příjmů odložená (+/-) | 1 | 592 |
| `vzz-m` | VZZ | M. | Převod podílu na výsledku hospodaření společníkům (+/-) | 1 | 596 |

### 4d. Off-statement (technical - build no report row)

| category_code | statement | row | statutory label | # accounts | accounts |
|---|---|---|---|---:|---|
| `off-zaverkove` | — | — | Závěrkové účty (počáteční/konečný účet rozvažný, účet Z+Z) – nevykazují se ve výkazech | 4 | 700, 701, 702, 710 |
| `off-interni` | — | — | Vnitřní zúčtování / vnitropodnikové převodové účty – nevykazují se ve výkazech (nettují se na nulu) | 7 | 395, 398, 597, 598, 690, 697, 698 |

## 5. Systemic gaps / caveats for the caller

1. **Short-term vs long-term reclassification** (3c) is the single biggest open item: several pohledávky/závazky
   accounts legitimately land in either the dlouhodobé or krátkodobé block by residual maturity. Static account ->
   row mapping cannot decide this; the statement engine needs a maturity input. Defaults here are krátkodobé.
2. **Mixed debit/credit accounts** (3c) need balance-sign switching at report time.
3. **"x0" group-summary placeholder accounts** (010, 020, 500, 510, ...): mapped to aggregate section rows.
   If ERPNext never posts to them, they contribute nothing; if they are used, confirm the aggregate placement.
4. **KB layout is pre-2016 / simplified**; this mapping supersedes the KB row codes with current Decree 500/2002.
   The vault's verifier flags W7-V1..V5 (aktiva/pasiva code collision, 481 two-sided, F-line aggregation,
   562 úroky) are all addressed above.
5. **Vault confidence is "medium"** (single primary source). Every row code here is subject to accountant
   sign-off; the exact plný-rozsah Příloha 1/2 line list should be reconciled against an e-Sbírka consolidation
   before the statements are declared statutory.
