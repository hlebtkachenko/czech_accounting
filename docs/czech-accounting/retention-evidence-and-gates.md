---
title: Czech Retention, Electronic Evidence, and Acceptance Gates
kind: reference
status: accepted
evidence_grade: primary-law
scope: Accounting Act 563/1991, effective 2026-01-01, and VAT evidence framework
last_verified: 2026-07-21
---

# Czech Retention, Electronic Evidence, and Acceptance Gates

## Direct answer

The live ERPNext database is not, by itself, the retention and evidence system.

Accounting Act § 31 gives baseline 10-year retention for financial statements and annual reports and 5-year retention for accounting documents, books, depreciation plans, inventories, charts, and other proving records. These are not automatic deletion dates: § 32 can extend preservation for litigation, tax, AML, insurance, archival, unpaid obligations, warranty, and other purposes.

Electronic records are permitted, but the entity must preserve human readability, identical content across conversions, origin/provability, integrity, security, and the means to render the records throughout retention.

## Use this when

Use this note for backups, attachments, OCR, audit logs, delete/cancel policy, signature records, legal holds, archive exports, or acceptance criteria.

## Official model

The principal source is [Accounting Act No. 563/1991 Coll., consolidation effective 2026-01-01](https://e-sbirka.gov.cz/sb/1991/563/2026-01-01), especially §§ 31 to 35.

### Baseline retention

Accounting Act § 31(2):

| Record category | Baseline period |
|---|---:|
| Financial statements and annual reports | 10 years |
| Accounting documents, books, depreciation plans, inventories, charts and overviews | 5 years |
| Other records proving accounting | 5 years |

The period starts at the end of the accounting period to which the record relates.

### Extensions and legal hold

Section 32 requires continued preservation after the baseline where a record serves criminal, AML, administrative, civil, tax, archival, social-security, health-insurance, copyright, warranty/complaint, unpaid receivable, or unperformed obligation purposes under its conditions.

Therefore, category plus period end is not enough to calculate destruction. The system needs legal-hold state and a reviewed final disposal decision.

### Record form and conversion

Section 33 recognizes paper, technical, and mixed records. A technical record must be convertible to human-readable form. Conversion creates a new record and must preserve identical content. The entity must retain rendering means and protect records, media, software, and content against misuse, damage, destruction, unauthorized alteration, loss, or theft.

### Provability and signature records

Section 33a defines provable records and signature records. A technical signature record is not merely `owner`, `modified_by`, a username, or an application log. The implementation must prove unambiguous origin and the attachment/relationship required by the statute.

### Correction trail

Section 35 requires correction without undue delay and preservation of responsible person, time, and before/after content. Destructive overwrite or deletion is incompatible with this requirement unless another preserved record establishes the required proof.

EU VAT Directive Articles 233 and 244 to 249 additionally frame invoice authenticity, integrity, legibility, storage, and access.

## Pinned implementation

ERPNext/Frappe mappings are hypotheses and must be proven:

- database plus regular backups for recoverable application state;
- immutable source-file/evidence storage with content hashes;
- preserved original bytes, with OCR/extraction explicitly marked derived;
- linked responsibility and approval records stronger than username metadata;
- cancellation/amendment and Version logs tested against before/after and responsibility needs;
- legal-hold record overriding normal expiry;
- archive export readable without depending on one live ERPNext instance;
- restore tests covering database, private/public files, attachments, hashes, and indexes.

See [DocType Schema Sync and Migrations](../framework/doctypes/schema-sync-and-migrations.md) for database risk and [ERPNext Vouchers, Tax, Currency, and Cancellation](../erpnext/accounting/vouchers-tax-currency-and-cancellation.md) for reversal behavior.

## Implementation runbook

### Evidence intake

1. Store original file bytes before transformation.
2. Calculate and store a cryptographic content hash.
3. Record source, receipt time, importing identity, and external reference.
4. Store OCR/extracted data as a separate derived artifact with parser version.
5. Link evidence to the accounting document, approvals, ledger postings, corrections, and filings.

### Retention model

1. Classify each record under an accountant/lawyer-approved category.
2. Calculate baseline from the end of the relevant accounting period.
3. Evaluate § 32 extensions and project legal holds.
4. Block automated deletion until final disposal review.
5. Record disposal authority, decision, time, actor, and destroyed object set.

### Restore and readability

1. Back up database and all site files/attachments.
2. Encrypt backups and protect keys separately.
3. Restore to a disposable site on a schedule.
4. Verify documents, attachments, hashes, approval history, ledgers, and reports.
5. Produce a human-readable independent export for retained records.
6. Prove that rendering works without relying on an unpinned cloud service.

### Acceptance gates before Czech suitability claim

- accountant-approved applicability and chart;
- complete § 11 document fixture coverage;
- chronological/systematic book golden reports;
- VAT invoice/event/filing reconciliation;
- correction fixtures preserving before/after/responsibility;
- dedicated agent-user permission matrix;
- backup and full attachment restore;
- hash validation and legal hold;
- clean install and upgrade migrations;
- documented professional sign-off and remaining exceptions.

## Files and commands

The backup commands depend on the final deployment, encryption, and storage design. Do not copy a generic `bench backup` command into a retention policy without proving that files, private files, encryption, off-machine copies, and restore are included.

Likely custom app records:

```text
Evidence Record
Evidence Derivation
Responsibility or Approval Record
Correction Event
Retention Classification
Legal Hold
Archive Export Manifest
Restore Verification Report
```

Names are provisional design hypotheses.

## Failure modes

- **Delete at exactly 5 or 10 years:** § 32 can require longer preservation.
- **Keep only the MariaDB database:** attachments, source evidence, rendering, and keys can be lost.
- **Keep only OCR text:** derived extraction does not replace original evidence.
- **Treat `modified_by` as signature record:** statutory provability is stronger.
- **Store backups but never restore:** existence does not prove recoverability.
- **Keep encryption key only on the same Mac:** one failure destroys both data and recovery.
- **Allow ordinary deletion of submitted records:** undermines correction and audit proof.
- **Claim cloud/object immutability without testing:** retention controls need operational evidence.

## Verification

### Checked

- Dated 2026 Accounting Act §§ 31 to 35.
- Official EU VAT invoice integrity/storage framework.
- Retention extensions explicitly separated from baseline periods.
- Software mappings labelled hypotheses.

### Open verification

- Accountant/lawyer-approved category and legal-hold mapping.
- Exact backup/archive architecture and off-machine destination.
- Technical signature-record design.
- Full local restore and independent-readability test.
- Destruction policy and approval.

## Source map

### Official legislation

- [Accounting Act No. 563/1991 Coll., effective 2026-01-01](https://e-sbirka.gov.cz/sb/1991/563/2026-01-01), especially §§ 31 to 35

### EU source

- [VAT Directive 2006/112/EC, consolidated 2025-04-14](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02006L0112-20250414), especially Articles 233 and 244 to 249

### Related system notes

- [Schema Sync and Migrations](../framework/doctypes/schema-sync-and-migrations.md)
- [Vouchers, Tax, Currency, and Cancellation](../erpnext/accounting/vouchers-tax-currency-and-cancellation.md)
