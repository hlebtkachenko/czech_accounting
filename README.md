# czech_accounting

A Frappe app that extends **ERPNext** with Czech accounting behavior: statutory chart of
accounts, financial statements, VAT/DPH exports, ISDOC, ARES lookup, and assisted data
entry.

It is an **extension, not a fork**. Official `frappe` and `erpnext` are used unmodified;
all Czech-specific behavior lives in this app.

Status: initial scaffold. No accounting content yet.

## Dependency

Installs only on a site that already has ERPNext:

```
frappe
  └── erpnext
        └── czech_accounting
```

This is enforced by `required_apps = ["erpnext"]`.

## Install

On a Frappe bench that already has ERPNext:

```bash
bench get-app https://github.com/hlebtkachenko/czech_accounting
bench --site <your-site> install-app czech_accounting
```

## Develop

Run a Frappe development bench with developer mode on:

```bash
bench --site <your-site> set-config developer_mode 1
```

- DocTypes created for the **Czech Accounting** module (with *Custom* unchecked)
  serialize automatically to `czech_accounting/czech_accounting/doctype/...`.
- Custom Fields or Property Setters on ERPNext/Frappe doctypes are database records;
  snapshot them to source with:
  ```bash
  bench --site <your-site> export-fixtures --app czech_accounting
  ```
- Apply schema changes with `bench --site <your-site> migrate`.

Then commit and push.

## Documentation

Everything is mapped in [docs/README.md](docs/README.md): the phased build plan
([docs/ROADMAP.md](docs/ROADMAP.md)) and the researched Frappe / ERPNext / Czech-accounting
knowledge base ([docs/knowledge-base/](docs/knowledge-base/)).

## Safety

This repository is public and contains source only. Never commit credentials, `.env`
files, keys, backups, or any accounting or customer data.

## License

MIT. See [license.txt](license.txt).
