---
title: Czech VAT, Currency, and Corrections
kind: reference
status: accepted
evidence_grade: primary-law
scope: Czech VAT Act 235/2004, consolidation effective 2026-01-01
last_verified: 2026-07-21
---

# Czech VAT, Currency, and Corrections

## Direct answer

Czech VAT support requires more than ERPNext tax rates. The system must preserve invoice evidence, tax point and issue dates, supplier/customer identities and VAT IDs, evidential number, base/rate/VAT, supply regime, correction links, filing-period assignment, and reconciled VAT return/control-statement outputs.

The VAT amount on a Czech tax invoice is stated in CZK even when other invoice amounts use another currency.

## Use this when

Use this note for tax fields, invoice templates, foreign currency, VAT event model, control statement, corrective documents, deadlines, or filing exports.

## Official model

The principal source is [VAT Act No. 235/2004 Coll., consolidation effective 2026-01-01](https://e-sbirka.gov.cz/sb/2004/235/2026-01-01). Official operational guidance comes from the Czech Financial Administration.

### Invoice obligation and deadline

VAT Act § 28 defines cases requiring a tax document. The normal issuance deadline is 15 days from the date the obligation to declare tax or the supply arose, with specific cross-border monthly rules in § 28(9).

### Ordinary invoice fields

VAT Act § 29 requires supplier and customer identification/VAT ID where applicable, evidential number, scope and subject of supply, issue date, tax point or advance date when different, unit price excluding VAT, discounts outside that price, taxable base, rate, and VAT in Czech currency. Section 29(2) adds wording for exemption, self-billing, reverse charge, and specified regimes.

VAT Act § 30 generally permits a simplified tax document only up to CZK 10,000 and excludes listed cases.

### Numbering conclusion

Accounting Act § 11 and VAT Act § 29 require identifiers/evidential numbers. These provisions alone do not establish one globally gapless sequence for every accounting and tax document.

The project still needs controlled unique series, no reuse, cancellation/correction traceability, and an exception register. A Czech accountant must approve the policy.

### VAT records and control statement

VAT Act §§ 100 to 100b require sufficiently detailed VAT records for return, recapitulative statement, and control statement. Sections 101c to 101k establish the control-statement regime.

The Financial Administration states:

- a legal person files monthly within 25 days after month end, even with a quarterly VAT period;
- a natural person follows its VAT-return period, monthly or quarterly, within 25 days after period end;
- a subsequent control statement is due within 5 working days after discovering incorrect or incomplete filed information;
- filing is electronic in the published format and structure.

See [when to file](https://financnisprava.gov.cz/cs/dane/dane/dan-z-pridane-hodnoty/kontrolni-hlaseni-dph/kdy) and the [control statement portal](https://financnisprava.gov.cz/cs/dane/dane/dan-z-pridane-hodnoty/kontrolni-hlaseni-dph).

### Currency

Accounting Act § 4(12) requires accounting-currency recording and dual tracking of specified foreign-currency assets/liabilities and related items. Sections 24a to 24d govern accounting currency in the 2026 Act and need a dedicated implementation pass before selecting a non-CZK functional currency.

VAT Act § 29(1)(l) requires VAT amount in Czech currency. EU VAT Directive Article 230 is consistent with this rule.

### Corrections

Accounting Act § 35 requires correcting incomplete, non-provable, incorrect, or unintelligible records without undue delay and preserving responsible person, correction time, and before/after content.

VAT corrections are transaction-specific. Corrective tax documents must link to original treatment and enter the correct VAT evidence and period. A separate professional mapping is required for each correction reason/regime.

## Pinned implementation

ERPNext mappings are design hypotheses:

- use a normalized effective-dated Czech VAT classification layer in the custom app;
- map it to ERPNext tax templates/calculation and invoice GL posting;
- store exact supplier/customer VAT ID and evidential number as exchanged;
- distinguish issue, tax point, occurrence, receipt, posting, and import times;
- derive VAT return, control statement, and recapitulative statement from one normalized tax-event ledger;
- reconcile every tax event to invoice and GL control Accounts;
- freeze each filing dataset and preserve generated XML hash, receipt, amendments, and reconciliation;
- model correction as a linked event with before/after evidence, not destructive overwrite.

See [ERPNext Vouchers, Tax, Currency, and Cancellation](../erpnext/accounting/vouchers-tax-currency-and-cancellation.md) for exact software behavior.

## Implementation runbook

1. Fix the user's VAT status and supported transaction scope.
2. Extract effective-dated VAT rates and regimes from primary authority.
3. Define the normalized Czech VAT event schema.
4. Map each event class to ERPNext tax calculation and GL Accounts.
5. Create fixtures for domestic, exempt, reverse charge, EU, third-country, advance, corrective, and foreign-currency cases that actually apply.
6. Reconcile invoice tax rows to VAT events and GL.
7. Reconcile VAT events independently to VAT return, control statement, and recapitulative statement.
8. Pin and hash Financial Administration XML schemas.
9. Store filing snapshot, submission receipt, and subsequent statement chain.
10. Obtain accountant/tax-adviser approval before submission claims.

## Files and commands

Likely project artifacts:

```text
effective-dated VAT classification DocTypes
invoice Custom Fields for tax evidence
VAT event ledger generated from submitted/corrected vouchers
return/control/recapitulative report mappings
versioned XML generator and schemas
filing snapshot and receipt records
golden transaction fixtures
```

Do not submit to the tax authority from an unreviewed development environment.

## Failure modes

- **Configure only 21% or reduced rates:** rate is not the full legal regime.
- **Use posting date as every date:** issue, tax point, occurrence, receipt, and filing can differ.
- **Render control statement directly from invoice layout:** filing must derive from normalized, reconciled tax events.
- **Lose the original evidential number or VAT ID formatting:** control-statement matching depends on source identity.
- **Use live exchange-rate provider without policy:** authority, date, evidence, and rounding remain undefined.
- **Treat cancel as legal correction automatically:** ERPNext reversal behavior and Czech correction-document rules must be mapped.
- **Claim global gapless numbering from cited sections:** the sources support identification, not that broad statement.

## Verification

### Checked

- Dated 2026 VAT Act and Accounting Act sources.
- Official Financial Administration control-statement timing and interface pages.
- EU invoice currency/integrity framework used only as supporting context.
- ERPNext mappings kept explicitly hypothetical.

### Open verification

- Current VAT rates and every supported regime.
- Exact §§ 100 to 101k field/filing mapping.
- Current XML schemas and sample acceptance.
- Accountant-approved numbering, exchange-rate, rounding, and correction policy.
- End-to-end fixture reconciliation on ERPNext.

## Source map

### Official legislation

- [VAT Act No. 235/2004 Coll., effective 2026-01-01](https://e-sbirka.gov.cz/sb/2004/235/2026-01-01), especially §§ 26 to 35 and 100 to 101k
- [Accounting Act No. 563/1991 Coll., effective 2026-01-01](https://e-sbirka.gov.cz/sb/1991/563/2026-01-01), especially §§ 4, 11, 24a to 24d, and 35

### Official administration guidance

- [Control statement basic information](https://financnisprava.gov.cz/cs/dane/dane/dan-z-pridane-hodnoty/kontrolni-hlaseni-dph/zakladni-informace)
- [Control statement deadlines](https://financnisprava.gov.cz/cs/dane/dane/dan-z-pridane-hodnoty/kontrolni-hlaseni-dph/kdy)
- [Control statement portal and current artifacts](https://financnisprava.gov.cz/cs/dane/dane/dan-z-pridane-hodnoty/kontrolni-hlaseni-dph)

### EU source

- [VAT Directive 2006/112/EC, consolidated 2025-04-14](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02006L0112-20250414)
