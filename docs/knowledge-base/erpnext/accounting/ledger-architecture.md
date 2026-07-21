---
title: ERPNext Accounting and Ledger Architecture
kind: reference
status: accepted
evidence_grade: source-verified
scope: ERPNext v16.28.0 at de591661b9ba0bd3f62ac25b99b5c85c723515f6
last_verified: 2026-07-21
---

# ERPNext Accounting and Ledger Architecture

## Direct answer

Frappe supplies the platform. ERPNext supplies Accounting. A Czech app extends both layers without replacing either.

The central write path is:

```text
submitted business voucher
-> voucher controller validates business meaning
-> controller builds a GL map
-> erpnext.accounts.general_ledger.make_gl_entries
-> period, account, budget, dimension, freeze, and balance validation
-> GL Entry documents
-> Payment Ledger entries when relevant
-> reports query ledger rows plus Account tree metadata
```

Never import or insert `GL Entry` directly. Create the correct voucher and let the normal posting pipeline generate ledgers.

## Use this when

Use this note to understand where Czech validations belong, trace posting failures, design reports, or decide which document an import should create.

## Official model

The official [Accounting introduction](https://docs.frappe.io/erpnext/accounting/introduction), [Accounts module](https://docs.frappe.io/erpnext/accounts), and [Accounting Reports](https://docs.frappe.io/erpnext/accounting-reports) describe masters, transactions, ledgers, and derived financial statements.

## Pinned implementation

### Core layers

| Layer | Principal artifact | Role |
|---|---|---|
| Legal entity | Company | Currency, chart, defaults, freeze settings, country |
| Structure | Account | Company-specific NestedSet tree and posting leaves |
| Time | Fiscal Year, Accounting Period | Valid dates and operational locks |
| Vouchers | Sales/Purchase Invoice, Journal Entry, Payment Entry | Business validation and GL-map construction |
| Book of record | GL Entry | Debit/credit rows linked to source vouchers |
| Open items | Payment Ledger Entry | Outstanding, allocation, reconciliation |
| Posting service | `general_ledger.py` | Common validation, normalization, balance, insert, reverse |
| Reports | GL, Trial Balance, statements, AR/AP | Queries and aggregates ledger rows |

### Shared transaction validation

[`AccountsController.validate`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/controllers/accounts_controller.py#L239-L327) performs fiscal-year, party, account-currency, tax-template, totals, schedule, and regional validation shared by accounting transactions.

This shared layer is important but not the complete voucher contract. Each invoice, journal, and payment controller adds its own rules and GL map.

### Common GL service

[`make_gl_entries`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L29-L69) is the main accounting choke point. Its flow includes:

- budget validation;
- accounting-dimension offsets;
- Accounting Period and disabled-account checks;
- cost-center allocation;
- optional merging of similar rows;
- negative debit/credit normalization;
- Payment Ledger creation where applicable;
- work-in-progress, balance, dimension, freeze-date, and closing validation;
- GL Entry insertion and submission.

[`process_gl_map`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L190-L202) and [`save_entries`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L408-L443) implement normalization and persistence.

### GL Entry still validates

[`GLEntry`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/gl_entry/gl_entry.py#L28-L125) resolves fiscal year, validates mandatory data and currencies in normal paths, then checks Account, dimensions, balance direction, frozen accounts, and outstanding references.

Do not bypass the posting service or GL Entry lifecycle with raw SQL, `db_insert`, or ignored permissions.

### Where Czech code belongs

Prefer, in order:

1. configure existing Company, Account, tax, period, and voucher fields;
2. add Czech classification fields through the custom app;
3. validate at the originating voucher before GL-map creation;
4. use supported regional or controller extension points;
5. add reports that consume the same GL rather than creating a second ledger.

Any GL-map extension must behave identically during initial posting and reposting.

## Implementation runbook

When tracing a posting:

1. Identify voucher DocType, state, Company, currency, and posting date.
2. Read its `validate`, `on_submit`, `get_gl_entries`, and `make_gl_entries` paths.
3. Inspect the resulting GL map before the common service.
4. Follow common validations through `general_ledger.py`.
5. Inspect created GL and Payment Ledger rows by voucher type/name.
6. Reconcile total debit and credit in all relevant currency contexts.
7. Verify the report that consumes those rows.

For a new Czech rule, write the required journal effect first, then map it to the correct voucher and lifecycle. Do not start from a proposed UI field.

## Files and commands

Key pinned source entrypoints:

```text
erpnext/controllers/accounts_controller.py
erpnext/accounts/general_ledger.py
erpnext/accounts/doctype/gl_entry/gl_entry.py
erpnext/accounts/doctype/payment_ledger_entry/
erpnext/accounts/report/
```

Use ORM and reports for verification. Direct database inspection is diagnostic only and must not become the posting integration.

## Failure modes

- **Install Accounting without ERPNext:** Accounting is part of the ERPNext app.
- **Insert GL Entry directly:** bypasses voucher semantics and common controls.
- **Treat all voucher types as generic journals:** invoices and payments carry party, tax, outstanding, and workflow meaning.
- **Add a parallel Czech ledger:** creates reconciliation and source-of-truth failure.
- **Extend only initial posting:** repost or cancel can produce different results.
- **Assume generic reports equal statutory Czech output:** economic totals and statutory layouts/classifications are different requirements.

## Verification

### Checked

- Official Accounting and report documentation.
- Shared AccountsController and GL pipeline at ERPNext v16.28.0.
- GL Entry validation and representative upstream voucher/report tests.

### Open verification

- Local voucher fixture and generated ledger snapshots.
- Czech-specific extension points after legal mapping.
- Repost, cancel, and report reconciliation on the local site.

## Source map

### Official documentation

- [Accounting introduction](https://docs.frappe.io/erpnext/accounting/introduction)
- [Accounts module](https://docs.frappe.io/erpnext/accounts)
- [Accounting Reports](https://docs.frappe.io/erpnext/accounting-reports)

### Pinned source

- [Shared AccountsController validation](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/controllers/accounts_controller.py#L239-L327)
- [Common general-ledger entrypoint](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L29-L69)
- [GL-map processing and balance](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L190-L202)
- [GL Entry controller](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/gl_entry/gl_entry.py#L28-L125)

### Pinned tests

- [Sales Invoice GL tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/sales_invoice/test_sales_invoice.py#L1096-L1280)
- [Purchase Invoice GL tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/purchase_invoice/test_purchase_invoice.py#L107-L148)
- [General Ledger report tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/report/general_ledger/test_general_ledger.py#L30-L300)
