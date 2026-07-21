---
title: Research and Audit Log
kind: audit-log
status: maintained
evidence_grade: structural
scope: Entire knowledge base
last_verified: 2026-07-21
---

# Research and Audit Log

## 2026-07-21: reset

The original breadth-first draft was rejected as assumption-heavy and moved under `outputs/_junk/`. It is not accepted evidence and is not linked from this KB.

The replacement started from source resolution rather than topic generation.

## Source baseline resolution

Official repository tags and commits were resolved on 2026-07-21:

| Repository | Selected baseline | Why |
|---|---|---|
| Frappe | `v16.27.1`, `f33ac3f00ab818e21b25ddbec93efb653fd9aa1b` | Newest observed `v16.*` release tag |
| ERPNext | `v16.28.0`, `de591661b9ba0bd3f62ac25b99b5c85c723515f6` | Newest observed `v16.*` release tag |
| frappe_docker | `v3.2.1`, `d4a310089f5d6fc38ed1317b898d75b9c74901db` | Current tagged container baseline |
| Frappe MCP | captured `main`, `11d5076b1bf4483b2ff6751a13e0736f5396b1e6` | No stable release selected; snapshot is explicitly branch-derived |

GitHub's generic “latest release” result was not used blindly for ERPNext because a v15 patch had a later publication time than v16. The research filtered release tags by the selected major line.

See [Source Registry](../sources/INDEX.md) for immutable links.

## DocType benchmark research

Three independent passes were completed before synthesis:

1. Official documentation pass: 19 directly opened `docs.frappe.io` pages, exact headings, observed update indicators, version caveats, 22 mapped claims, and 18 unresolved questions.
2. Pinned source pass: creation, metadata, storage, controllers, permissions, lifecycle, schema sync, migrations, and test anchors traced at the exact Frappe commit.
3. Adversarial pass: common statements were challenged against both evidence sets, producing explicit documentation drift and safe replacement wording.

The accepted notes are linked from [DocType Reference Index](../framework/doctypes/INDEX.md).

## Validation record

On 2026-07-21:

- KB structure validator passed 12 Markdown notes.
- All internal Markdown links resolved.
- Every note was reachable from the root index.
- Source-verified notes contained immutable 40-character Frappe GitHub permalinks.
- 110 pinned Frappe source links were mapped to the local v16.27.1 snapshot.
- All referenced local source paths and line anchors were within the pinned files.
- No note was marked `test-verified`.

## Current evidence limit

The project Bench and MariaDB site are not installed yet. Upstream tests were inspected but not run on this Mac. The DocType module is therefore source-verified only.

## Second research batch

Three parallel dossiers were completed and then synthesized into accepted modules:

- Frappe developer architecture: 574 research lines covering runtime boundaries, request/transaction flow, hooks, permissions, APIs, jobs, scheduler, configuration, migrations, and tests.
- ERPNext Accounting: 532 research lines tracing Company, Account, periods, invoices, journals, payments, GL/Payment Ledger, cancellation, tax, currency, imports, reposting, and reports.
- Czech accounting: 230 research lines based on dated e-Sbírka consolidations, Ministry of Finance, Financial Administration, and EUR-Lex.

The Czech module introduced the `primary-law` evidence grade. It means an official-source legal requirements inventory, not a compliance or legal opinion.

## Expanded validation record

After synthesis on 2026-07-21:

- KB structure validator passed 27 Markdown notes and 3,454 lines.
- 241 pinned repository paths were checked against local source snapshots.
- 228 of those citations included line anchors, all within the pinned files.
- No note is marked `test-verified`.
- Docker/operations and local runtime installation remain unaccepted work.
