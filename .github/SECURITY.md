# Security policy

This app performs bookkeeping and handles financial data for real companies. Treat security
reports seriously.

## Reporting

Report privately to **afframe@hapd.cz**. Do not open a public issue for a vulnerability.
Include: affected area, reproduction, and impact. Expect an acknowledgement within a few days.

## Severity and response intent

| Severity | Examples | Response intent |
|---|---|---|
| Critical | Data exposure, auth bypass, arbitrary code/SQL execution | Fix as top priority |
| High | Privilege escalation, incorrect access control on accounting data | Fix promptly |
| Medium | Injection with limited scope, missing validation at a boundary | Scheduled fix |
| Low | Hardening, defense-in-depth | Backlog |

## Ground rules

- The repository is public and source-only. Never commit credentials, `.env` files, keys,
  backups, or accounting/customer data. Real secrets live only on the server.
- The accounting-assistant role is minimally scoped: no Administrator, shell, SQL, or
  arbitrary Python, and draft-only writes.
- Dependencies are tracked via Dependabot; review advisories before bumping pins.
