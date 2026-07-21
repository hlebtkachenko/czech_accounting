# Architecture

## Model

ERPNext is the accounting engine (double-entry posting, GL, invoices, payments,
statements). `czech_accounting` is a thin Frappe extension app installed on the same
site that adds Czech statutory behavior. ERPNext and Frappe are never modified.

```
Mac  --ssh -L 8000:127.0.0.1:8000-->  VPS (all project files under ~/frappe/)
                                        Docker project "czech-dev":
                                          mariadb 11.8, redis-cache, redis-queue, frappe
                                        bench: ~/frappe/frappe_docker/development/frappe-bench
                                        site: erpnext.localhost (developer_mode = 1)
                                        apps: frappe, erpnext, czech_accounting
                                        served by `bench start` on 127.0.0.1:8000
```

## Decisions

- **Extension, not fork.** Extend via hooks, Custom DocTypes, Custom Fields, fixtures,
  patches, and reports. Fork only if a confirmed requirement cannot be met through
  supported extension points.
- **One developable bench** during the build phase: it is both the running system and the
  development environment. A locked, baked production image is a later milestone, for when
  real books go live.
- **Localhost-only.** The dev bench binds to `127.0.0.1`; the Mac reaches it via an SSH
  tunnel. No public port, no TLS, no domain yet.
- **Containment.** Everything for this project lives under `~/frappe/` on the VPS and
  `~/Developer/frappe/` on the Mac. Nothing else on either machine is touched.

## Data and secrets

- Site data and backups live under the bench `sites/` directory and `~/frappe/backups/`.
  MariaDB data is bind-mounted to `~/frappe/data/mariadb`.
- Secrets (DB root password, admin password, site `encryption_key`) never enter this
  repo. They live on the VPS (`~/frappe/frappe.env`, site_config.json) and in a password
  manager.

## Deferred milestones

Czech chart of accounts, statements, VAT XML (DPHDP3/DPHKH1/DPHSHV), ISDOC, ARES,
scoped agent API access (dedicated `Accounting Assistant` role, draft-only), Tailscale,
CI, baked production image, full restore rehearsal.
