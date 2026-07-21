---
title: DocType Reference Index
kind: index
status: accepted
evidence_grade: structural
scope: Frappe v16.27.1
last_verified: 2026-07-21
---

# DocType Reference Index

This is the benchmark module for the evidence-first KB. Current official documentation was cross-checked against Frappe v16.27.1 source and upstream tests. The module is source-verified, not test-verified, because the project Bench has not yet been installed and exercised locally.

## Task routing

| Question | Start here |
|---|---|
| What is a DocType and where is each kind stored? | [Mental Model and Storage Variants](mental-model-and-storage.md) |
| Why were files generated, or why were they not? | [Ownership and Generated Artifacts](ownership-and-generated-artifacts.md) |
| Which controller hook should contain this rule? | [Document Lifecycle and Controller Hooks](document-lifecycle.md) |
| New DocType, child table, Custom Field, or hook? | [Extension Decision Guide](extension-decision-guide.md) |
| What exactly does `bench migrate` do to schema? | [Schema Sync and Migrations](schema-sync-and-migrations.md) |
| Do current docs match the pinned release? | [Evidence and Documentation Drift Map](evidence-and-drift-map.md) |

## Questions answered by this module

1. What exactly is a DocType in Frappe's metadata, document, database, and Desk layers?
2. What files and tables are generated for standard, custom, child, single, and virtual DocTypes?
3. What does developer mode change?
4. What is the complete save, insert, submit, cancel, update-after-submit, and delete lifecycle?
5. Which extension mechanism belongs in a custom app?
6. When should the project use a new DocType, Custom Field, child table, or configuration record?
7. Which migrations and tests are required before changing the persistent site?

## Acceptance boundary

An implementation agent may use these notes for Frappe v16.27.1 design and source navigation. Before changing the persistent site, it must still:

1. take and verify a restorable backup;
2. run the relevant workflow on the installed site;
3. write project tests for accounting-sensitive behavior;
4. record Czech-domain evidence separately;
5. avoid promoting any note to `test-verified` until commands and results are recorded.
