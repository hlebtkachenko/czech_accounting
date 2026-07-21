---
title: Czech Accounting Applicability, Documents, and Books
kind: reference
status: accepted
evidence_grade: primary-law
scope: Czech private entrepreneurs and legal entities under Act 563/1991, effective 2026-01-01
last_verified: 2026-07-21
---

# Czech Accounting Applicability, Documents, and Books

## Direct answer

Do not configure Czech accounting from ERPNext's `Company` alone. First record and obtain professional confirmation of legal form, start date, accounting-entity basis, size category, audit duty, VAT status, accounting regime, accounting period, and currency.

For in-scope double-entry accounting, Czech law requires provable accounting documents and entries, chronological and systematic books, analytical/off-balance records where applicable, and an entity-owned chart of accounts based on the applicable framework chart.

## Use this when

Use this note before Company creation, chart design, document fields, approval workflow, statutory journal/general-ledger reports, or any Czech compliance claim.

## Official model

The principal source is [Act No. 563/1991 Coll., consolidation effective 2026-01-01](https://e-sbirka.gov.cz/sb/1991/563/2026-01-01). The entrepreneur implementation baseline is [Decree No. 500/2002 Coll., consolidation effective 2024-01-01](https://e-sbirka.gov.cz/sb/2002/500/2024-01-01), subject to its scope and exclusions.

### Applicability

Accounting Act § 1 and § 4 include Czech-seated legal persons and specified natural-person entrepreneurs as accounting entities. In the 2026 consolidation, the turnover trigger in § 1(2)(e) is CZK 25,000,000 for the immediately preceding calendar year, subject to the statute's exact definition and transition rules.

Accounting Act § 9 controls full versus permitted simplified scope and contains entity-type limits. Do not infer simplified eligibility from size alone.

### Period and accrual

Accounting Act § 3 requires transactions to be recognized in the period to which they relate in time and substance, with expenses and income independent of cash movement. The normal accounting period is 12 consecutive months, calendar or fiscal year, with statutory exceptions for transitional/formation/restructuring cases.

### Czech language and system completeness

Accounting Act § 4 treats documents, entries, books, depreciation plans, inventories, chart of accounts, financial statements, and reports as accounting records. Accounts are kept in Czech, while another-language evidence is permitted only if intelligibility is maintained under § 8.

### Accounting document fields

Accounting Act § 11(1) requires:

1. accounting-document identifier;
2. content of the accounting case and its parties;
3. amount, or unit price and quantity;
4. document-preparation time;
5. time of the accounting case when different;
6. signature record for the person responsible for the case and for posting.

Section 11(2) requires preparation without undue delay after facts become known and sufficient determinability of each case.

### Entries and books

Accounting Act § 12 requires continuous entries after document preparation and responsibility evidence when the entry maker differs from the person responsible for posting. Entries cannot be made outside accounting books.

Section 13 identifies:

- journal, chronological completeness;
- general ledger, systematic by accounts;
- analytical-account books;
- off-balance-sheet books.

General-ledger synthetic Accounts contain at least opening balances, monthly aggregate debit and credit turnover, and closing balances at statement date.

Sections 13 and 14 require the entity's own period chart, based on the applicable framework chart, containing the accounts needed for all cases and financial statements. Accounts cannot be created outside the chart and books.

## Pinned implementation

This is a legal requirements note. ERPNext mappings below are hypotheses, not verified compliance:

| Requirement | Candidate ERPNext concept | Known gap |
|---|---|---|
| legal entity | Company | does not encode applicability or professional sign-off |
| identifier | naming series and voucher name | needs approved series/no-reuse/exception policy |
| parties and case | party, item, descriptions, references | must preserve source evidence and structured identity |
| event/preparation times | posting, invoice, due, creation dates | requires distinct occurrence, issue, tax, receipt, posting, import times |
| signature records | workflow, assignments, users, audit logs | ordinary username audit is not proven as statutory signature record |
| journal | GL chronology | requires statutory output, ordering, and completeness reconciliation |
| general ledger | General Ledger by Account | must expose opening, monthly turnovers, closing |
| analytical/off-balance books | dimensions, parties, custom classification | explicit scope and reconciliation required |
| chart | Account tree | Czech framework constraints and versioned statement mapping required |

See [ERPNext Company, Chart of Accounts, and Period Controls](../erpnext/accounting/company-chart-and-periods.md) for exact software behavior.

## Implementation runbook

1. Create a versioned Czech Accounting Profile specification before configuration.
2. Record legal form, registration/incorporation, applicability basis, regime/scope, size, audit, VAT, fiscal year, and accounting currency.
3. Obtain Czech accountant sign-off.
4. Build the chart from Decree 500/2002 and Czech Accounting Standards evidence.
5. Map every statutory document field to ERPNext, custom fields, attached evidence, workflow, or derived output.
6. Specify chronological journal, general ledger, analytical, and off-balance reports.
7. Define responsible-person and posting-approval records.
8. Create fixture tests for document completeness and book reconciliation.
9. Block “Czech compliant” output until the profile and mappings are approved.

## Files and commands

Likely custom-app artifacts:

```text
Czech Accounting Profile DocType
Czech Account Classification fields and effective-dated mappings
responsibility/approval records
statutory journal and ledger reports
golden legal-requirement fixtures
```

Names remain design decisions. Do not create these models before the legal-to-system mapping is reviewed.

## Failure modes

- **Assume every Czech entrepreneur has the same duty:** applicability differs by legal and factual profile.
- **Use only Company country:** does not establish accounting regime.
- **Call an ERPNext invoice a complete § 11 document automatically:** evidence may be external or composite.
- **Treat `owner` as statutory signature record:** origin and responsibility require stronger proof.
- **Use General Ledger UI as the complete statutory books:** outputs and reconciliation need explicit acceptance.
- **Translate labels and call it Czech accounting:** legal data, workflow, books, retention, and filings remain.
- **Claim one global gapless series is directly required by § 11:** the cited provision requires an identifier, not that universal sequence rule.

## Verification

### Checked

- Dated 2026 Accounting Act consolidation and dated entrepreneur Decree page.
- Applicability, period, language, document, entry, book, and chart provisions identified above.
- ERPNext mapping kept explicitly hypothetical.

### Open verification

- User's legal profile and professional sign-off.
- Detailed Decree 500/2002 and Czech Accounting Standards chart/statement mapping.
- 2026 audit/category thresholds and transitions.
- Exact statutory output and signature-control implementation.

## Source map

### Official legislation

- [Accounting Act No. 563/1991 Coll., effective 2026-01-01](https://e-sbirka.gov.cz/sb/1991/563/2026-01-01), especially §§ 1 to 4 and 8 to 14
- [Decree No. 500/2002 Coll., effective 2024-01-01](https://e-sbirka.gov.cz/sb/2002/500/2024-01-01)

### Official standards

- [Czech Accounting Standards 001 to 023 for Decree 500/2002](https://www.mfcr.cz/assets/cs/media/Ucetnictvi_2016_Ceske-ucetni-standardy-pro-500-2002.pdf)

### System mapping

- [ERPNext Accounting Index](../erpnext/accounting/INDEX.md)
