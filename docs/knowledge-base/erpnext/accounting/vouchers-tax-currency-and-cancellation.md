---
title: ERPNext Vouchers, Tax, Currency, and Cancellation
kind: reference
status: accepted
evidence_grade: source-verified
scope: ERPNext v16.28.0 at de591661b9ba0bd3f62ac25b99b5c85c723515f6
last_verified: 2026-07-21
---

# ERPNext Vouchers, Tax, Currency, and Cancellation

## Direct answer

Choose the voucher by business meaning:

| Voucher | Meaning | Typical posting responsibility |
|---|---|---|
| Sales Invoice | Customer receivable, revenue, output tax, optional stock/POS effects | Customer, income, taxes, payments/rounding |
| Purchase Invoice | Supplier payable, expense/asset, input tax, optional stock effects | Supplier, expense/asset, taxes, withholding/rounding |
| Journal Entry | Explicit balanced multi-account adjustment or specialized entry | One GL row per account row, references as configured |
| Payment Entry | Settlement, allocation, bank/cash movement, outstanding updates | Party, bank, deductions, taxes, references |

Tax templates calculate amounts. They do not supply Czech legal classification or statutory filing mappings. Cancellation creates reversal behavior and depends on the v16 immutable-ledger setting.

## Use this when

Use this note for invoice/payment imports, VAT design, foreign currency, submitted corrections, cancellation, or ledger tests.

## Official model

Official pages for [Sales Invoice](https://docs.frappe.io/erpnext/sales-invoice), [Purchase Invoice](https://docs.frappe.io/erpnext/purchase-invoice), [Journal Entry](https://docs.frappe.io/erpnext/journal-entry), [Payment Entry](https://docs.frappe.io/erpnext/payment-entry), [Setting Up Taxes](https://docs.frappe.io/erpnext/setting-up-taxes), and [Multi Currency Accounting](https://docs.frappe.io/erpnext/multi-currency-accounting) describe the business concepts.

## Pinned implementation

### Sales and Purchase Invoice

[`SalesInvoice.on_submit`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/sales_invoice/sales_invoice.py#L466-L550) handles stock when applicable and posts through `make_gl_entries`. [`get_gl_entries`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/sales_invoice/sales_invoice.py#L1585-L1652) assembles customer, tax, income/item, transfer, discount, POS/payment, write-off, and rounding effects.

[`PurchaseInvoice.on_submit`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/purchase_invoice/purchase_invoice.py#L768-L817) follows the purchase lifecycle. [`PurchaseInvoice.get_gl_entries`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/purchase_invoice/purchase_invoice.py#L835-L917) builds supplier, item/expense/asset, tax, withholding, paid, write-off, and rounding rows.

Do not turn a Purchase Invoice into a Journal Entry just because both produce balanced GL. The invoice also owns supplier, tax, due-date, document, and outstanding semantics.

### Journal and Payment Entry

[`JournalEntry`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/journal_entry/journal_entry.py#L128-L213) validates balanced rows, parties, references, currencies, and lifecycle state. Its GL builder is in [`journal_entry.py`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/journal_entry/journal_entry.py#L1126-L1230).

[`PaymentEntry`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/payment_entry/payment_entry.py#L172-L228) validates settlement difference, withholding, requests/schedules, posting, and outstanding state. Its GL map in [`payment_entry.py`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/payment_entry/payment_entry.py#L1304-L1427) includes party, bank, deductions, taxes, and references.

### Tax calculation and classification gap

[`AccountsController`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/controllers/accounts_controller.py#L276-L296) loads tax templates and invokes calculation during validation.

[`calculate_taxes_and_totals`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/controllers/taxes_and_totals.py#L32-L91) validates currency, item values and templates, initializes taxes, calculates exclusive/net/tax/totals, and adjusts inclusive tax.

[`TaxRule.get_tax_template`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/tax_rule/tax_rule.py#L177-L245) selects active candidates by matched fields and priority.

A Czech app still needs effective-dated classification for tax point, regime, VAT IDs, domestic/EU/third-country treatment, exemptions, reverse charge, corrections, VAT return, control statement, and recapitulative statement.

### Multiple currency contexts

[`GL Entry`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/gl_entry/gl_entry.py#L37-L71) stores amounts and rates across Company, Account, transaction, and reporting currency contexts.

Pinned exchange-rate source is configurable: [`get_exchange_rate`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/setup/utils.py#L61-L153) checks local records and stale-rate rules, pegged rates, then Currency Exchange Settings endpoint/response configuration.

The provider names in current docs are not a stable v16 contract. Czech policy must define the authority, rate date, evidence, and rounding.

### Immutable-ledger documentation trap

Current invoice and journal docs broadly refer to immutable ledger behavior. In v16.28.0, [`enable_immutable_ledger`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/accounts_settings/accounts_settings.json#L461-L466) is an Accounts Settings field whose JSON default is `0`.

[`make_reverse_gl_entries`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L683-L799) branches:

- disabled: original active rows are marked cancelled, then cancelled reversal rows are created;
- enabled: originals stay active and active reversing rows are created with swapped debit/credit and cancellation-date behavior.

This must become an explicit project decision after Czech professional review and disposable-site tests.

### Submitted updates can repost

Purchase Invoice accounting-sensitive updates can create Repost Accounting Ledger through [`on_update_after_submit`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/purchase_invoice/purchase_invoice.py#L818-L830) and [`repost_accounting_entries`](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/controllers/accounts_controller.py#L3020-L3047).

Czech extensions must be deterministic during repost, not only original submit.

## Implementation runbook

Create a fixture matrix before configuring taxes:

1. domestic CZK sales and purchase;
2. each approved VAT rate;
3. exempt and out-of-scope cases;
4. reverse-charge and EU cases as applicable;
5. foreign-currency invoice and settlement;
6. advance/payment allocation;
7. credit/corrective document linked to original;
8. rounding cases;
9. cancel before and after period lock;
10. repost after an allowed submitted edit.

For each case, record:

- source fields and legal classification;
- expected voucher state;
- expected GL debit/credit rows;
- Payment Ledger effect;
- VAT event/filing mapping;
- expected report totals;
- cancellation/correction result.

## Files and commands

Expected custom-app additions may include Custom Fields, tax classification DocTypes, fixtures, controller extensions, report code, and focused integration tests. No direct change to ERPNext invoice JSON is planned.

## Failure modes

- **Import every transaction as Journal Entry:** loses invoice/payment semantics.
- **Treat a tax percentage as Czech VAT classification:** calculation and filing meaning are different layers.
- **Rely on a named online rate provider from docs:** pinned v16 uses configurable settings.
- **Enable immutable ledger without testing:** cancellation date, period lock, and report behavior change.
- **Use `db_set` on submitted accounting fields:** bypasses the intended lifecycle.
- **Implement only `on_submit`:** cancellation and repost can diverge.
- **Assume cancel deletes effects:** it creates reversal behavior.

## Verification

### Checked

- Current official voucher, tax, and currency docs.
- Exact voucher posting routes, tax calculation, rate retrieval, submitted repost, and cancellation branch.
- Representative upstream invoice, journal, payment, tax, currency, and immutable-ledger tests.

### Open verification

- Czech accountant-approved voucher/tax/correction mappings.
- Local setting state and decision for immutable ledger.
- Full fixture matrix on the local site.
- Czech VAT report and correction reconciliation.

## Source map

### Official documentation

- [Sales Invoice](https://docs.frappe.io/erpnext/sales-invoice)
- [Purchase Invoice](https://docs.frappe.io/erpnext/purchase-invoice)
- [Journal Entry](https://docs.frappe.io/erpnext/journal-entry)
- [Payment Entry](https://docs.frappe.io/erpnext/payment-entry)
- [Setting Up Taxes](https://docs.frappe.io/erpnext/setting-up-taxes)
- [Multi Currency Accounting](https://docs.frappe.io/erpnext/multi-currency-accounting)

### Pinned source

- [Sales Invoice lifecycle and GL map](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/sales_invoice/sales_invoice.py#L466-L550)
- [Purchase Invoice lifecycle and GL map](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/purchase_invoice/purchase_invoice.py#L768-L917)
- [Tax calculation](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/controllers/taxes_and_totals.py#L32-L150)
- [Cancellation branches](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/general_ledger.py#L683-L799)
- [Configurable exchange-rate retrieval](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/setup/utils.py#L61-L153)

### Pinned tests

- [Sales Invoice tax tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/sales_invoice/test_sales_invoice.py#L328-L932)
- [Purchase Invoice multi-currency tests](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/purchase_invoice/test_purchase_invoice.py#L768-L831)
- [Immutable-ledger reversal test](https://github.com/frappe/erpnext/blob/de591661b9ba0bd3f62ac25b99b5c85c723515f6/erpnext/accounts/doctype/payment_ledger_entry/test_payment_ledger_entry.py#L471-L525)
