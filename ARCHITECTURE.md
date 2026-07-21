# Architecture

## Model

ERPNext is the accounting engine: double-entry posting, general ledger, invoices,
payments, and financial statements. `czech_accounting` is a thin Frappe extension app,
installed on the same site, that adds Czech statutory behavior on top. Frappe and ERPNext
are never modified.

```
frappe  ->  erpnext  ->  czech_accounting   (installed apps on one site)
```

## Principles

- **Extension, not fork.** Extend through supported points only: hooks, Custom DocTypes,
  Custom Fields, fixtures, patches, and reports. Fork only if a confirmed requirement
  cannot be met through an extension point, and record the reason.
- **Effective-dated rules.** Statutory behavior (VAT rates, statement layouts, required
  fields) carries an effective date. Rules are versioned, never hardcoded as timeless.
- **Traceability.** Every reported figure must trace back to its source voucher and
  attachment.
- **Assisted entry is draft-only.** Automated or agent-created documents are created as
  drafts; submission stays a human action. See [AGENTS.md](AGENTS.md).

## How schema is authored

With developer mode enabled on a development bench:

- DocTypes owned by the **Czech Accounting** module serialize to source automatically.
- Custom Fields and Property Setters on ERPNext/Frappe doctypes are exported to fixtures
  with `bench export-fixtures --app czech_accounting`, re-imported on `bench migrate`.

## Scope roadmap

Chart of accounts template, Czech balance sheet and profit-and-loss layouts, accounting
books, VAT/DPH classification and XML exports (DPHDP3, DPHKH1, DPHSHV), ISDOC import and
export, ARES lookup, and scoped API access for assisted data entry.
