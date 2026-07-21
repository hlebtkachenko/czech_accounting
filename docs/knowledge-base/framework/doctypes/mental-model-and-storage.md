---
title: DocType Mental Model and Storage Variants
kind: reference
status: accepted
evidence_grade: source-verified
scope: Frappe v16.27.1 at f33ac3f00ab818e21b25ddbec93efb653fd9aa1b
last_verified: 2026-07-21
---

# DocType Mental Model and Storage Variants

## Direct answer

A DocType is metadata that defines a Frappe document model: fields, naming, permissions, form behavior, and controller binding. A document is an instance of that model.

Do not equate every DocType with a dedicated database table. Storage depends on the DocType flags:

| Variant | Metadata signal | Persistent representation | Correct use |
|---|---|---|---|
| Regular | `issingle = 0`, `istable = 0`, `is_virtual = 0` | One `tab<DocType>` table, one row per document | Independently addressable business records |
| Child / Table | `istable = 1` | Its own `tab<Child DocType>` table plus parent relationship columns | Ordered rows owned by a parent document |
| Single | `issingle = 1` | Rows in shared `tabSingles`, keyed by DocType and field | One settings record for the site |
| Virtual | `is_virtual = 1` | No Frappe-managed schema | Data backed by an external or custom store |

`Custom` is an ownership/export distinction, not a fifth storage model. A custom regular DocType can still have a normal table. A standard DocType is owned by app files. A custom DocType is stored as site metadata and is not exported by the normal standard-DocType path.

## Use this when

Use this note before:

- designing a new Czech accounting record;
- choosing between a child row and an independently linked record;
- creating site settings;
- exposing an external data source as Frappe documents;
- writing SQL, reports, imports, or migration code that assumes a table name;
- asking an agent to add fields or records.

This note does not decide whether a proposed record satisfies Czech accounting law. It only explains the Frappe persistence model.

## Official model

The official [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes) page describes a DocType as the application building block that defines model and view behavior, fields, naming, and ORM access. Its introductory statement that creating a DocType creates a JSON object and database table is accurate for the normal app-owned case but incomplete as a universal rule.

The exceptions are documented separately:

- [Child / Table DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype) describes rows attached through a parent Table field and the `parent`, `parenttype`, `parentfield`, and `idx` relationship values.
- [Single DocType](https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype) states that the single logical instance is stored field-by-field in `tabSingles`.
- [Virtual DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype) states that no Frappe table is created and the controller supplies the data-source behavior.

The official docs are current, unversioned pages retrieved on 2026-07-21. The source statements below are the exact v16.27.1 baseline.

## Pinned implementation

### Metadata becomes a model

`frappe.get_meta(doctype)` combines the DocType definition with permitted custom metadata. The `Document` class then uses this metadata for validation, persistence, child handling, permissions, and lifecycle dispatch. The controller class for a normal DocType extends `Document`.

Do not treat DocType JSON as the live database row itself. It is the app-owned source definition that migration imports into the site's metadata tables and uses for schema synchronization.

### Regular and child table names

[`DBTable.__init__`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/schema.py#L22-L42) constructs `table_name` as `tab` plus the DocType name. [`DBTable.get_columns_from_docfields`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/schema.py#L80-L110) derives stored columns from metadata and skips virtual fields.

For a child DocType, [`get_other_fields_meta`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_db_update.py#L258-L289) reflects the standard child linkage columns. The official child documentation names their roles:

- `parent`: the owning document name;
- `parenttype`: the owning document's DocType;
- `parentfield`: the Table field on the parent;
- `idx`: row order.

A child row therefore has its own database row and identity, but its supported application meaning is ownership by a parent. Do not model a reusable entity, ledger entry, tax code, or independently permissioned record as a child merely because it appears as a grid.

### Single storage

[`MariaDBDatabase.updatedb`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/mariadb/database.py#L461-L477) reads `issingle` and only creates or synchronizes a dedicated table when it is false.

[`Document._save`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L552-L605) routes Single documents to `update_single` rather than `db_update`. [`Document.update_single`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L773-L788) replaces the DocType's rows in `tabSingles` with `(doctype, field, value)` records.

Consequences:

- there is no `tab<My Settings>` table to query;
- values are not typed into dedicated business columns in `tabSingles`;
- a Single is site-wide, not automatically per company;
- use a regular DocType with a Company link when each company needs a separate record or history.

### Virtual storage

[`DBTable.sync`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/schema.py#L44-L52) returns without schema work for a Virtual DocType. [`DocType.check_developer_mode`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L326-L342) rejects a custom Virtual DocType, so it must be delivered as a standard app-owned DocType in this revision.

The controller must implement persistence and list behavior appropriate to its backing store. The official JSON-file example is explanatory only. It is not a safe multi-user storage design.

### Virtual DocFields are not stored columns

DocType-level Virtual and field-level virtuality are different. A normal DocType may contain a DocField marked virtual. [`DBTable.get_columns_from_docfields`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/schema.py#L80-L110) skips such a field when building columns. Its value must be computed or supplied by code.

## Implementation runbook

Before creating a DocType, write down these answers:

1. Does each record need its own stable identity, permissions, audit trail, API endpoint, or links from other records?
   - Yes: start with a regular DocType.
2. Is the row meaningless outside one parent and should it be saved and deleted with that parent?
   - Yes: consider a child DocType plus a Table field.
3. Is there exactly one configuration object for the entire site, with no per-company variants or history requirement?
   - Yes: consider a Single.
4. Does another system own persistence, while Frappe should provide forms, permissions, and APIs?
   - Yes: consider a Virtual DocType only after specifying the full controller contract.
5. Is a displayed value derived and not persistent?
   - Yes: consider a virtual DocField, not necessarily a Virtual DocType.

For Czech accounting, default to independently addressable regular DocTypes for legally meaningful documents, posting records, tax evidence, number-series control, and audit events. This is a project design starting point, not a legal conclusion.

## Files and commands

For a standard DocType named `Czech Accounting Setting` in a module whose Python package is `czech_accounting`, expect the metadata path pattern:

```text
<app>/<app>/czech_accounting/doctype/czech_accounting_setting/
```

Do not guess the SQL table for a Single or Virtual DocType. Inspect metadata first:

```bash
bench --site <site> execute frappe.get_meta --args '["Czech Accounting Setting"]'
```

For interactive inspection, prefer Bench Console and the ORM over direct SQL. When SQL is necessary, resolve `issingle`, `istable`, and `is_virtual` first.

## Failure modes

- **Every DocType has a table:** false for Single and Virtual DocTypes.
- **Child rows live inside the parent's SQL row:** false. They use a child table and relationship columns.
- **A child row is a cheap normal record:** unsafe. Its lifecycle and meaning are coupled to the parent.
- **Single means one record per company or user:** false unless application code implements that behavior elsewhere.
- **Virtual means no implementation work:** false. Persistence and query behavior move into the controller.
- **Custom means no database table:** false. `custom` concerns ownership and export, not regular storage.
- **A layout field becomes a column:** false for no-value fields; field type labels are not a complete schema contract.
- **Removing a field removes its data column:** false during ordinary schema sync. See [Schema Sync and Migrations](schema-sync-and-migrations.md).

## Verification

### Checked

- Official model and all three storage exceptions, retrieved 2026-07-21.
- Frappe v16.27.1 schema dispatcher, MariaDB `updatedb`, `Document._save`, `update_single`, and Virtual schema short-circuit.
- Official upstream test source showing child metadata columns and database schema expectations.

### Open verification

- Runtime creation and inspection of one regular, child, Single, and Virtual DocType on the project's installed site.
- PostgreSQL behavior is outside the planned MariaDB deployment and was not operationally tested.
- Direct REST behavior and permission checks for child records need a dedicated API and permissions module.
- The appropriate Czech accounting entity boundaries need legal-domain evidence and a separate architecture decision.

## Source map

### Official documentation

- [Understanding DocTypes, Introduction and Conventions](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Child / Table DocType, relationship properties](https://docs.frappe.io/framework/user/en/basics/doctypes/child-doctype)
- [Single DocType, Schema](https://docs.frappe.io/framework/user/en/basics/doctypes/single-doctype)
- [Virtual DocTypes, purpose and controller example](https://docs.frappe.io/framework/user/en/basics/doctypes/virtual-doctype)
- [Field Types, Table and layout controls](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)

### Pinned source

- [`DBTable` naming, schema dispatch, and field columns](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/schema.py#L22-L110)
- [MariaDB `updatedb` Single branch](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/mariadb/database.py#L461-L477)
- [`Document._save` storage branch](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L552-L605)
- [`Document.update_single`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L773-L788)
- [`DocType.check_developer_mode` Virtual restriction](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L326-L342)

### Pinned tests

- [Database field and child-column expectations](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_db_update.py#L250-L289)
- [Virtual DocType integration tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_virtual_doctype.py)
- [Child-table integration tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_child_table.py)
