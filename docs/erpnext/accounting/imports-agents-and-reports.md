---
title: ERPNext Accounting Imports, Agent Integration, and Reports
kind: reference
status: accepted
evidence_grade: source-verified
scope: ERPNext v16.28.0 and Frappe v16.27.1
last_verified: 2026-07-21
---

# ERPNext Accounting Imports, Agent Integration, and Reports

## Direct answer

For 100 ordinary current supplier invoices, create Purchase Invoice documents as drafts through Data Import or a custom API workflow, validate and reconcile them, then submit deliberately.

Do not use the Opening Invoice Creation Tool for current detailed invoices. It creates synthetic one-line opening invoices for outstanding balances at migration cutover.

Core reports are derived from GL Entry, Account hierarchy, Payment Ledger, and period logic. Czech statutory reports should consume and reconcile to the same ledgers rather than store separate balances.

## Use this when

Use this note to import invoices, design an agent batch, load opening balances, choose Data Import versus API, or build Czech reports.

## Official model

The official [Data Import](https://docs.frappe.io/erpnext/data-import) page supports CSV/XLSX insert/update with validation and optional submit. [Opening Invoice Creation Tool](https://docs.frappe.io/erpnext/opening-invoice-creation-tool) is specifically for migration of outstanding receivables/payables. [Accounting Reports](https://docs.frappe.io/erpnext/accounting-reports) describes the principal ledger-derived reports.

## Pinned implementation

### Data Import uses document lifecycle

Pinned Frappe [`DataImport`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/data_import/data_import.py#L50-L150) checks target `allow_import` and user import permission, then queues work outside developer/test shortcuts.

[`Importer`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/data_import/importer.py#L170-L313) builds a normal Document and calls `insert`; when selected and allowed, it then calls `submit`. Successes commit individually and failures are logged.

Safe first-use policy: import drafts. “Submit After Import” removes a valuable review boundary.

### REST creates through controllers

Frappe v1 and v2 resource creation call normal document insertion. See [`v1.create_doc`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/api/v1.py#L43-L63) and [`v2.create_doc`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/api/v2.py#L171-L207).

For repeated automation, a custom whitelisted batch method is safer than arbitrary calls because it can enforce mappings, idempotency, dry-run/commit states, and durable results.

### Opening Invoice Tool is specialized

[`get_invoice_dict`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/opening_invoice_creation_tool/opening_invoice_creation_tool.py#L191-L278) constructs an opening invoice with one synthetic item against a Temporary Account, `is_opening = Yes`, and no stock update.

[`import_doc`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/opening_invoice_creation_tool/opening_invoice_creation_tool.py#L281-L319) inserts and submits each invoice; 50 or more are queued.

The loop creates a named savepoint but calls general rollback in its exception branch. Do not assume partial-success semantics without a runtime test.

Use this tool only for open AR/AP migration where item/tax detail is intentionally not being reconstructed.

### Reports consume ledgers

| Report | Main source behavior |
|---|---|
| General Ledger | queries GL Entry by Company/date and calculates opening/closing |
| Trial Balance | aggregates Account balances from ledger rows |
| Balance Sheet | groups Asset/Liability/Equity through shared statement functions |
| Profit and Loss | groups Income/Expense through shared statement functions |
| AR/AP | derives outstanding and ageing from ledger/payment concepts |

[`General Ledger.execute`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/report/general_ledger/general_ledger.py#L29-L160) requires Company/date context, reads Account metadata, fetches GL rows, and calculates opening/closing.

[`Balance Sheet.execute`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/report/balance_sheet/balance_sheet.py#L31-L124) calls shared statement data for root types and includes provisional P&L and opening-balance checks.

Czech financial statements, journal, general ledger, analytical books, and tax reports should be derived views with explicit classifications and reconciliation, not an independent store.

## Implementation runbook

### Import 100 current supplier invoices

1. Preserve source invoice bytes and calculate a hash.
2. Parse into a versioned staging schema.
3. Normalize supplier identity, invoice number, dates, currency, lines, tax, totals, and references.
4. Map to ERPNext Supplier, Item/expense Account, tax template/classification, currency, cost center, and Company.
5. Store a unique external/source identifier on Purchase Invoice.
6. Dry-run every row, with no document writes.
7. Reconcile source count, net, VAT, and gross totals.
8. Create drafts through normal Purchase Invoice `insert()`.
9. Review errors and representative rendered documents.
10. Reconcile created drafts back to source.
11. Submit through a separately authorized action.
12. Reconcile submitted vouchers, GL, Payment Ledger, VAT events, and reports.
13. Retry the same batch and prove no duplicates.

### Explicit transaction choice

Decide before implementation:

- atomic batch: one failure rolls everything back, simpler state but poor for large/error-prone input;
- resumable per-row: each invoice has durable state, retries, and reconciliation, but requires stronger idempotency and batch accounting.

For 100 invoices, a staged resumable design is usually operationally safer. This is a project recommendation, not upstream behavior.

### Build Czech reports

1. Define statutory output and legal source.
2. Identify source ledger and classification fields.
3. Write the query/report without storing duplicate balances.
4. Reconcile every report subtotal to General Ledger or Trial Balance control totals.
5. Freeze filing datasets and preserve XML/export hashes when relevant.
6. Add golden fixtures and accountant sign-off.

## Files and commands

Likely custom app artifacts:

```text
batch import parent and row DocTypes
source evidence attachment/hash fields
unique external-id Custom Field on Purchase Invoice
mapping/configuration DocTypes
whitelisted dry-run and commit methods
background job and reconciliation service
Czech reports and test fixtures
```

Do not expose raw database access, direct GL insertion, or `ignore_permissions` to the agent.

## Failure modes

- **Use Opening Invoice Tool for current invoices:** loses normal item/tax evidence detail.
- **Submit during first import:** bypasses review and correction before accounting effects.
- **No stable external ID:** retries create duplicates.
- **Direct GL import:** bypasses Purchase Invoice and payment semantics.
- **Assume Data Import is atomic:** pinned importer commits successful records individually.
- **Assume Opening Invoice savepoint guarantees prior rows survive:** source rollback call needs runtime verification.
- **Store separate Czech balances:** creates reconciliation divergence.
- **Call a generic report statutory:** format, classification, evidence, and filing rules need separate validation.

## Verification

### Checked

- Current official Data Import, Opening Invoice, REST, and Accounting Reports docs.
- Exact Frappe import/document lifecycle and ERPNext Opening Invoice construction/import loop.
- Core report entrypoints and representative upstream tests.

### Open verification

- Local Data Import and API behavior with Purchase Invoice child rows.
- Batch atomic/resumable project decision.
- Opening Invoice partial-failure semantics.
- Accountant-approved Czech report mappings and golden fixtures.

## Source map

### Official documentation

- [Data Import](https://docs.frappe.io/erpnext/data-import)
- [Opening Invoice Creation Tool](https://docs.frappe.io/erpnext/opening-invoice-creation-tool)
- [Accounting Reports](https://docs.frappe.io/erpnext/accounting-reports)
- [Frappe REST API](https://docs.frappe.io/framework/user/en/api/rest)

### Pinned source

- [Frappe Data Import](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/data_import/data_import.py#L50-L150)
- [Importer lifecycle and commit model](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/data_import/importer.py#L170-L313)
- [Opening Invoice construction](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/opening_invoice_creation_tool/opening_invoice_creation_tool.py#L191-L319)
- [General Ledger report](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/report/general_ledger/general_ledger.py#L29-L160)

### Pinned tests

- [Opening Invoice Tool tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/opening_invoice_creation_tool/test_opening_invoice_creation_tool.py#L41-L145)
- [General Ledger report tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/report/general_ledger/test_general_ledger.py#L30-L300)
- [Balance Sheet tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/report/balance_sheet/test_balance_sheet.py#L15-L89)
