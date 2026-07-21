---
title: Agent Instructions for the Evidence KB
kind: policy
status: maintained
evidence_grade: structural
scope: All agents using this knowledge base
last_verified: 2026-07-21
---

# Agent Instructions for the Evidence KB

## Purpose

Use this KB as a routing and evidence layer. It does not replace official documentation, pinned source, runtime tests, or Czech professional review.

## Required workflow

Before implementing a Frappe, ERPNext, or Czech accounting change:

1. Start at [Knowledge Base Index](INDEX.md).
2. Open the narrowest matching module index.
3. Check the note's `scope`, `evidence_grade`, and `last_verified`.
4. Read its Direct answer, Pinned implementation, Failure modes, Verification, and Source map.
5. Open the cited official documentation for supported concepts.
6. Open immutable pinned source for exact version behavior.
7. Read the linked upstream tests, but do not call them locally passing unless they were executed.
8. Complete every relevant Open verification item on the actual site.
9. Keep Frappe and ERPNext upstream apps unchanged. Put owned changes in the custom app.
10. Record project decisions separately from upstream or legal facts.

Do not implement from a note marked `researching`.

## Common routing

| Task | Entry point |
|---|---|
| Add or extend a DocType | [DocType Reference Index](framework/doctypes/INDEX.md) |
| Understand apps, sites, hooks, API, permissions, jobs, tests | [Frappe Developer Architecture](framework/architecture/INDEX.md) |
| Work with accounting vouchers, ledgers, periods, taxes, or reports | [ERPNext Accounting](erpnext/accounting/INDEX.md) |
| Map Czech legal requirements | [Czech Accounting Requirements](czech-accounting/INDEX.md) |
| Check source pins | [Source Registry](sources/INDEX.md) |
| Add or audit a note | [Evidence Standard](governance/EVIDENCE_STANDARD.md) |

## Hard boundaries

- Never claim Czech compliance from ERPNext behavior alone.
- Never write directly to GL Entry for normal business transactions.
- Never use Administrator or ignored permissions as an integration design.
- Never use raw SQL or `db_set` to bypass document validation.
- Never treat an upstream test link as a local test result.
- Never use moving branch links as accepted source evidence.
- Never expose site configuration, API secrets, backup keys, or invoice personal data in logs or notes.
- Never run a destructive schema, chart, retention, or deletion operation without a verified backup and explicit scope.

## Validation

From the KB root:

```bash
python3 _tools/validate_kb.py
```

The validator checks metadata, evidence requirements, immutable source citations, internal links, and index reachability. It does not validate external page content or local runtime behavior.
