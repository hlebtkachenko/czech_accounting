---
title: DocType Schema Sync and Migrations
kind: reference
status: accepted
evidence_grade: source-verified
scope: Frappe v16.27.1 with MariaDB
last_verified: 2026-07-21
---

# DocType Schema Sync and Migrations

## Direct answer

`bench migrate` moves a site forward toward the currently installed app code. It imports standard DocType JSON, synchronizes physical schema, runs forward patches, then synchronizes fixtures and exported customizations in later migration work.

It is not a reversible migration system:

- removing a field from metadata does not normally drop the old database column;
- reverse schema migrations are not supported;
- switching Git back to old code is not a database rollback;
- MariaDB DDL rollback is not established by Frappe's Python transaction wrapper;
- restore from a verified backup is the dependable rollback boundary for the one persistent site.

## Use this when

Use this note before:

- changing a field type, name, uniqueness, index, or requirement;
- adding or removing a DocType or field;
- migrating prototype Czech data into a final model;
- exporting Custom Fields or Property Setters;
- running `bench migrate`;
- planning backup and recovery;
- reviewing an agent's schema-changing pull request.

## Official model

The official [Database Migrations](https://docs.frappe.io/framework/user/en/database-migrations) reference says DocType JSON drives schema synchronization, removed or renamed fields leave their old columns, reverse schema migrations are unsupported, and data transformations use patches.

The older [Migrations guide](https://docs.frappe.io/framework/user/en/guides/deployment/migrations) explains the same forward-patch model but includes historical directory examples. Use it for concepts, not literal paths.

[How To Migrate DocType Changes To Production](https://docs.frappe.io/framework/user/en/guides/deployment/how-to-migrate-doctype-changes-to-production) notes that permissions are not automatically reset simply because app JSON changed. An explicit patch is needed when code-owned permissions must replace site customization.

## Pinned implementation

### Migration phase order

[`SiteMigration.run_schema_updates`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/migrate.py#L136-L145) runs:

1. pre-model-sync patches;
2. standard model synchronization for installed apps;
3. post-model-sync patches.

[`SiteMigration.post_schema_updates`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/migrate.py#L147-L203) later synchronizes jobs, fixtures, dashboards, exported customizations, languages, and other site state before after-migrate completion.

Choose patch phase by dependency:

- pre-model-sync: code must read or transform the old schema before JSON synchronization;
- post-model-sync: code depends on the new metadata or columns.

Do not rely on an old documentation label suggesting post-model-sync is develop-only. The pinned v16 runner implements both phases.

### Standard DocType JSON import

[`sync_all` and `sync_for`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/sync.py#L47-L162) iterate installed apps, discover importable JSON definitions, and import them. [`import_file_by_path`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/modules/import_file.py#L74-L169) uses content hashes to avoid unchanged imports unless forced.

Reloading a DocType replaces its metadata record and child metadata, then `DocType.on_update` synchronizes the retained physical business table. It does not recreate business rows from JSON.

### Create and alter behavior

[`DocType.on_update`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L530-L558) calls `frappe.db.updatedb`. [`MariaDBDatabase.updatedb`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/mariadb/database.py#L461-L477) creates or alters non-Single, non-Virtual tables and commits after synchronization.

Schema alteration is not a down-migration engine. [`trim_tables`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/meta.py#L954-L1000) exists as a separate maintenance operation to find and optionally drop columns absent from metadata. It is destructive and not part of ordinary field removal.

Do not run table trimming on accounting data as cleanup. Retained columns may be necessary for a data migration, forensics, or restore validation.

### Type changes can fail against live data

The upstream DocType test changes a text field containing non-numeric data to `Int` and expects validation failure. A metadata edit that looks harmless in an empty system can fail or corrupt meaning when real rows exist.

For every type, length, nullability, unique, or index change:

1. profile current values;
2. specify conversion and invalid-row handling;
3. run on a restored copy;
4. validate counts and totals;
5. only then apply to the persistent site.

### Exported customization sync is later and can replace overrides

[`sync_customizations`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/modules/utils.py#L125-L239) processes code-defined customizations after normal model sync. A stored Custom Field can trigger a target-table schema update.

Because exported sets can replace site Property Setters and custom permissions, migration review must distinguish:

- base DocType JSON changes;
- Custom Fields;
- Property Setters;
- Custom DocPerm;
- fixtures;
- data patches.

## Implementation runbook

### Before every schema change

1. Record the pinned Frappe and ERPNext versions.
2. Identify owning app and exact source file or customization record.
3. Classify the change as additive, transform, constraint-tightening, rename, removal, or ownership change.
4. Inspect real row counts, nulls, distinct values, and accounting totals.
5. Decide whether a patch needs old or new schema.
6. Create a restorable site backup and verify restore on another site or disposable environment.
7. Test migration against restored realistic data.
8. Run migration twice and confirm the second run makes no domain changes.
9. Run focused application tests and data reconciliation.
10. Only then migrate the persistent site.

### Patch design

A patch should:

- have a unique entry in `patches.txt`;
- be safe to inspect after interruption;
- be idempotent or explicitly guarded;
- avoid hidden dependence on Administrator-only permissions;
- log counts, not sensitive record contents;
- assert or report accounting invariants;
- avoid dropping old data until a separately approved retention decision.

### Accounting reconciliation

For a migration touching invoices, journals, taxes, or accounts, compare at minimum:

- record counts by company, fiscal period, currency, and status;
- debit and credit totals;
- taxable base and tax totals by tax category;
- document totals versus ledger totals;
- missing links and duplicate external identifiers;
- submitted and cancelled status counts;
- old-to-new identifier mapping completeness.

The exact reconciliation set must follow the final Czech accounting model.

## Files and commands

Typical paths:

```text
<app>/<app>/patches.txt
<app>/<app>/patches/<version>/<patch_name>.py
<app>/<app>/<module>/doctype/<doctype>/<doctype>.json
<app>/<app>/<module>/custom/<target_doctype>.json
```

Operational command pattern:

```bash
bench --site <site> backup --with-files
bench --site <site> migrate
bench --site <site> run-tests --app <app>
```

These commands become test-verified only after the project's site name, backup location, restore procedure, and results are recorded. Do not publish or log backup encryption keys.

## Failure modes

- **Treat Git revert as database rollback:** code and schema/data state can diverge.
- **Assume removing JSON deletes a column:** ordinary sync retains old columns.
- **Run `trim-tables` as routine cleanup:** it can permanently drop retained data.
- **Place a patch in the wrong phase:** old columns may already be changed, or new columns may not exist yet.
- **Write a non-idempotent patch:** retry after partial failure can duplicate or corrupt data.
- **Test only an empty site:** real value distributions determine whether constraints and conversions succeed.
- **Assume migration transaction wrappers make MariaDB DDL reversible:** not proven and unsafe as recovery policy.
- **Reset permissions implicitly:** site-customized permissions are not guaranteed to follow base JSON updates.
- **Migrate the only site without a tested restore:** the project then has no dependable rollback.

## Verification

### Checked

- Current official database migration material, retrieved 2026-07-21.
- Exact v16.27.1 migration phases, JSON discovery/import, schema update path, customization sync, and separate column-trim operation.
- Upstream tests for reload, schema constraints, incompatible field changes, and customization synchronization were identified.

### Open verification

- Actual Bench backup and restore on the project's Mac.
- MariaDB version and configuration for the future installation.
- Runtime migration on a clean and restored site.
- Project conventions for patch version folders and reconciliation reports.
- Recovery behavior for a deliberately failed migration.

## Source map

### Official documentation

- [Database Migrations](https://docs.frappe.io/framework/user/en/database-migrations)
- [Migrations guide](https://docs.frappe.io/framework/user/en/guides/deployment/migrations)
- [How To Migrate DocType Changes To Production](https://docs.frappe.io/framework/user/en/guides/deployment/how-to-migrate-doctype-changes-to-production)
- [Exporting Customizations to your App](https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations)

### Pinned source

- [Migration schema phase](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/migrate.py#L136-L145)
- [Post-schema synchronization](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/migrate.py#L147-L203)
- [Standard model discovery and sync](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/sync.py#L47-L162)
- [Content-hash import gate](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/modules/import_file.py#L74-L169)
- [DocType schema update and export](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L530-L558)
- [MariaDB `updatedb`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/mariadb/database.py#L461-L477)
- [Separate destructive column trimming](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/meta.py#L954-L1000)
- [Customization synchronization](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/modules/utils.py#L125-L239)

### Pinned tests

- [DocType field-order and reload test](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/test_doctype.py#L204-L323)
- [Constraint and incompatible type-change tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/test_doctype.py#L102-L140)
- [Reload and migration-hash tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_modules.py#L165-L184)
- [Customization export and sync tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_modules.py#L77-L163)
