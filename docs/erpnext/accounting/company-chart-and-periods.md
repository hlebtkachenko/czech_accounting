---
title: ERPNext Company, Chart of Accounts, and Period Controls
kind: reference
status: accepted
evidence_grade: source-verified
scope: ERPNext v16.28.0 at de591661b9ba0bd3f62ac25b99b5c85c723515f6
last_verified: 2026-07-21
---

# ERPNext Company, Chart of Accounts, and Period Controls

## Direct answer

Configure CZK and the Czech chart before entering real transactions. Use these controls for different jobs:

| Control | Purpose |
|---|---|
| Company | Legal/accounting boundary, currency, defaults, country, freeze settings |
| Account tree | Company-specific posting and statement structure |
| Fiscal Year | Valid accounting-year/date coverage |
| Accounting Period | Operational lock for selected voucher types and date range |
| Company freeze date | Blocks GL changes through a date, subject to role |
| Period Closing Voucher | Closes Income/Expense into the selected closing account |

Do not confuse Fiscal Year with month closing or Period Closing Voucher with an operational lock.

## Use this when

Use this note for initial Company setup, Czech chart import, account validation, fiscal calendar, monthly locks, year-end close, or destructive chart operations.

## Official model

The official [Chart of Accounts](https://docs.frappe.io/erpnext/chart-of-accounts) page says each Company owns its chart and the chart can be adapted to legal requirements. [Accounting Period](https://docs.frappe.io/erpnext/accounting-period) and [Period Closing Voucher](https://docs.frappe.io/erpnext/period-closing-voucher) describe different closing controls.

## Pinned implementation

### Company creation is active setup

[`Company`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/setup/doctype/company/company.py#L34-L138) contains default/reporting currency, default accounts, freeze controls, stock settings, country, and chart source.

For a new Company without Accounts, [`Company.on_update`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/setup/doctype/company/company.py#L337-L379) creates the chart, warehouses, default cost center, country fixtures/tax template under its flags, and resolves default accounts.

[`validate_currency`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/setup/doctype/company/company.py#L321-L335) prevents changing Company currency after relevant submitted transactions exist.

Project rule: set CZK before transactional data. Country fixtures are bootstrap data, not Czech compliance.

### Account invariants

[`Account`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/account/account.py#L25-L87) is a NestedSet with account number, currency, type, root type, report type, parent, group flag, and Company.

Pinned rules include:

- parent belongs to the same Company and is a group;
- root Accounts are groups;
- Asset/Liability/Equity map to Balance Sheet, Income/Expense to P&L;
- Account number is unique within Company;
- Account currency defaults to Company currency;
- currency cannot change after foreign-currency ledger use.

See [`Account` tree validation](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/account/account.py#L107-L218) and [`currency/number validation`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/account/account.py#L333-L361).

### Chart importer destructive scope

The Chart of Accounts Importer is not an incremental synchronization tool. [`import_coa`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/chart_of_accounts_importer/chart_of_accounts_importer.py#L76-L98) calls `unset_existing_data` before rebuilding.

[`unset_existing_data`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/chart_of_accounts_importer/chart_of_accounts_importer.py#L451-L492) clears Company Account links and deletes company-specific Account, Party Account, Mode of Payment Account, Tax Withholding Account, Sales Tax Template, and Purchase Tax Template records.

Use it once on a new, backed-up Company. Do not rerun it on live accounting data as an update mechanism.

The importer requires all five root types: Asset, Liability, Expense, Income, and Equity.

### Fiscal Year

[`AccountsController.validate_date_with_fiscal_year`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/controllers/accounts_controller.py#L770-L793) validates accounting document dates against an explicit or resolved Fiscal Year.

[`FiscalYear`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/fiscal_year/fiscal_year.py#L32-L95) prevents overlapping ranges in the same scope. Normal years are one year less one day; `is_short_year` permits shorter periods.

### Accounting Period and other locks

ERPNext connects Accounting Period validation to configured closable DocTypes through hooks and rechecks it in the common GL service. See [`period_closing_doctypes`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/hooks.py#L326-L356), [`AccountingPeriod`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/accounting_period/accounting_period.py#L39-L106), and [GL period validation](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L155-L187).

Company freeze-date validation is in [`general_ledger.py`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L802-L823). Administrator does not automatically bypass it when the required role is absent.

Period Closing Voucher validation is separate in [`general_ledger.py`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L826-L852).

## Implementation runbook

1. Obtain an accountant-approved Czech chart and statutory classification map.
2. Create a new test Company with Czech Republic and CZK.
3. Import the chart before any real transactions.
4. Verify every Company default points to the correct Company, currency, account type, and ledger leaf.
5. Add explicit Czech report classification fields rather than encoding all meaning only in account names.
6. Test Fiscal Year, short-year, and Company scope.
7. Define month lock workflow using Accounting Period.
8. Define the limited role that can work through freeze dates, if any.
9. Define year-end closing through Period Closing Voucher and reconciliation.
10. Repeat on disposable data before the persistent site.

Do not rerun the COA importer after live transactions. Future account changes need controlled documents, fixtures, or migrations.

## Files and commands

Expected custom-app assets may include:

```text
fixtures or setup code for Czech Account classification
effective-dated chart template data
migration patches for controlled Account changes
tests for Company defaults, Account tree, and period locks
```

The exact chart delivery mechanism remains a project decision after clean-site tests.

## Failure modes

- **Set Company currency after posting begins:** pinned validation prevents it for submitted activity.
- **Treat Czech country fixture as compliance:** fixture data is incomplete evidence.
- **Rerun COA Importer on a live Company:** it deletes a defined group of accounting records before rebuilding.
- **Post to group Account:** ERPNext expects ledger leaves.
- **Use Fiscal Year as a close lock:** it validates date coverage, not all closing governance.
- **Use only freeze date:** Accounting Period and PCV solve different problems.
- **Encode statutory classes only in labels:** names can change and do not provide stable report mapping.

## Verification

### Checked

- Current Chart of Accounts, Accounting Period, and PCV docs.
- Company setup, Account invariants, COA importer deletion scope, fiscal-year validation, and closing controls at v16.28.0.
- Relevant upstream Company, Account, Fiscal Year, and Accounting Period tests.

### Open verification

- Exact Czech country fixtures installed on the local site.
- Accountant-approved chart and classifications.
- Local importer dry run, default-account resolution, period locks, and year-end close.

## Source map

### Official documentation

- [Chart of Accounts](https://docs.frappe.io/erpnext/chart-of-accounts)
- [Accounting Period](https://docs.frappe.io/erpnext/accounting-period)
- [Period Closing Voucher](https://docs.frappe.io/erpnext/period-closing-voucher)

### Pinned source

- [Company setup](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/setup/doctype/company/company.py#L321-L432)
- [Account validation](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/account/account.py#L107-L218)
- [COA importer destructive reset](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/chart_of_accounts_importer/chart_of_accounts_importer.py#L451-L492)
- [Fiscal Year validation](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/fiscal_year/fiscal_year.py#L32-L95)
- [Accounting Period validation](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/accounting_period/accounting_period.py#L39-L106)

### Pinned tests

- [Company chart tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/setup/doctype/company/test_company.py#L17-L127)
- [Account tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/account/test_account.py#L18-L333)
- [Accounting Period tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/accounting_period/test_accounting_period.py#L16-L101)
