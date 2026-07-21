# czech_accounting

A Frappe app that extends **ERPNext** with Czech accounting behavior (statutory chart of
accounts, financial statements, VAT/DPH exports, ISDOC, ARES, and agent-assisted data
entry). It is an **extension, not a fork**: official `frappe` and `erpnext` are used
unmodified, and all Czech-specific behavior lives here.

Status: initial scaffold. No accounting content yet.

## Dependency

Installs only on a site that already has ERPNext (`required_apps = ["erpnext"]`).

```
frappe
  └── erpnext
        └── czech_accounting
```

## Where it runs

One personal, single-user Frappe **development bench** in Docker on a private VPS,
reachable only over an SSH tunnel (nothing public). See [ARCHITECTURE.md](ARCHITECTURE.md).

## Development loop

1. Bring up the dev bench (frappe_docker `.devcontainer`), `developer_mode = 1`.
2. Author DocTypes for the `Czech Accounting` module in Desk. With developer mode on,
   they serialize straight into this repo under
   `czech_accounting/czech_accounting/doctype/...`.
3. Custom Fields / Property Setters on ERPNext doctypes are snapshotted with:
   ```bash
   bench --site <site> export-fixtures --app czech_accounting
   ```
4. Commit and push from this repo.

## Safety

This repository is **public**. It contains code and configuration only. Never commit
secrets, `.env` files, keys, backups, or any accounting/customer data. Real credentials
live on the VPS (`~/frappe/frappe.env`, chmod 600) and in a password manager.
