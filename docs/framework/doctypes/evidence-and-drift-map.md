---
title: DocType Evidence and Documentation Drift Map
kind: source-map
status: accepted
evidence_grade: source-verified
scope: Current official docs compared with Frappe v16.27.1
last_verified: 2026-07-21
---

# DocType Evidence and Documentation Drift Map

## Direct answer

Use current `docs.frappe.io` to understand concepts and find APIs. Use immutable v16.27.1 source and official tests to decide exact behavior. When they disagree, preserve the disagreement and test the installed site.

This module found material drift, so copying a tutorial into an implementation plan is unsafe.

## Use this when

Use this note to:

- audit another KB note;
- route an agent to the narrow official page and source symbol;
- understand why a live-doc example was not accepted literally;
- locate upstream tests before writing project tests;
- revalidate this module after a Frappe upgrade.

## Official model

The documentation pages are current but do not encode a Frappe patch version in their URLs. Relative “Last updated” labels were observed on 2026-07-21. They cannot prove that a code example was run against v16.27.1.

The pinned implementation baseline is:

```text
Frappe release: v16.27.1
Commit: f33ac3f00ab818e21b25ddbec93efb653fd9aa1b
```

## Pinned implementation

### Confirmed documentation drift

| Live documentation statement or example | Pinned v16.27.1 finding | Implementation-safe rule |
|---|---|---|
| Creating a DocType creates a database table. | Single skips a dedicated table; Virtual skips schema; child uses its own table. | State storage kind explicitly. |
| Enable developer mode before creating DocTypes. | The gate applies to non-custom standard DocTypes; custom DocTypes pass it; custom Virtual is rejected. | Require developer mode for app-owned Desk authoring, not runtime use. |
| Creating `Person` creates `person.py`. | Export is conditional on standard ownership and the export gate. | Git status and actual files are proof. |
| `on_update` is called when an existing document is updated. | Normal insert also reaches `on_update`. | Make `on_update` insert-safe. |
| Allow on Submit can be enabled through Customize Form. | v16 rejects turning it on for a standard field whose base DocField disallows it. | Use a harmless Custom Field or an owning-app change, never a bypass. |
| Tutorial `tabArticle` SQL transcript illustrates a current regular table. | The historical transcript includes parent columns that v16 creates for child tables. | Inspect v16 schema source or the running database. |
| Post-model-sync patch support is develop-only. | v16 migration runner implements both pre- and post-model phases. | Follow pinned migration runner. |
| Old-style naming is deprecated in v16 and will be removed in v16. | The same page is internally inconsistent. | Do not use it for new work; test legacy behavior before upgrade. |

### Historical tutorial artifacts

The Create a DocType tutorial currently includes MariaDB 10.4.13, Homebrew, 2020 timestamps, and a `master` branch. These are an old demonstration transcript. They are not supported requirements for the Mac installation.

The Controller Methods tutorial suggests enabling Server Scripts if an app controller example fails. No controller-source evidence makes Server Scripts a prerequisite for app controller execution. Do not enable that feature as troubleshooting without a separate security and architecture decision.

### Tests are evidence, not local results

The pinned repository contains upstream integration tests. Their presence shows intended behavior and gives patterns, but this KB remains `source-verified` because those tests were not executed in a configured Bench on this Mac.

| Concern | Pinned upstream test | Direct evidence |
|---|---|---|
| Standard JSON export and field order | [`TestDocType.test_sync_field_order`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/test_doctype.py#L204-L323) | JSON `field_order`, reload, and round trip |
| Boilerplate/export gate | [`TestUtils.test_make_boilerplate`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_modules.py#L200-L220) | Standard conversion under dev mode exports JSON |
| Customization export and sync | [`TestUtils` customization tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_modules.py#L77-L163) | Export path and synchronization |
| Child schema | [`TestChildTable`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_child_table.py#L15-L63) | Parent linkage columns and metadata transitions |
| Single loading and writes | [`test_document.py`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_document.py#L46-L50) and [`db_set` case](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_document.py#L534-L555) | Single document load and field update |
| Virtual no-table behavior | [`test_doctype.py`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/test_doctype.py#L554-L594) | No table and virtual-child constraint |
| Virtual CRUD contract | [`TestVirtualDoctypes`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_virtual_doctype.py#L85-L175) | Insert, update, reload, list, count, delete |
| Update after submit | [`test_update_after_submit`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_document.py#L245-L256) | Disallowed edit fails; allowed metadata passes |
| Class extension order | [`TestBaseDocument`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_base_document.py#L44-L124) | Extension methods and method-resolution order |
| Incompatible schema change | [`test_change_field_type_with_incompatible_values`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/test_doctype.py#L127-L140) | Live values can block type conversion |

## Implementation runbook

When an agent finds an answer in Frappe docs:

1. Record the exact page and heading.
2. Decide whether the claim is conceptual or version-sensitive.
3. For version-sensitive behavior, locate the implementation symbol at the pinned commit.
4. Locate a focused upstream test.
5. If docs and source disagree, write both and choose safe wording.
6. Convert the upstream test into a project test when the behavior matters.
7. Run it on the installed site and record the command and result before promoting the note to `test-verified`.

After a Frappe upgrade:

1. pin the new exact tag and commit;
2. compare referenced source paths and symbols;
3. rerun project tests;
4. update `last_verified`, scope, and changed claims;
5. never change only the version label.

## Files and commands

The research snapshots used for this audit are intentionally outside the deliverable and are not KB runtime dependencies. Future agents should use [Source Registry](../../sources/INDEX.md) for the exact upstream pins.

Validation command:

```bash
python3 _tools/validate_kb.py
```

Run it from the KB root. It checks evidence metadata, immutable source permalinks, internal links, and reachability from the root index. It does not check whether an external page still says the same thing.

## Failure modes

- **Use only docs:** misses version-specific exceptions and stale examples.
- **Use only source:** loses official intent, supported workflow, and navigation.
- **Call an upstream test link “test-verified”:** no test ran locally.
- **Link a moving `version-16` branch:** future line content can change.
- **Copy a SQL transcript:** it may encode old schema or environment details.
- **Silently resolve a contradiction:** future agents cannot reassess the decision.
- **Upgrade the source pin without rerunning checks:** evidence links and behavior can become false.

## Verification

### Checked

- 19 official Frappe documentation pages were opened directly on 2026-07-21.
- Frappe v16.27.1 source was pinned to the exact 40-character commit.
- Creation, storage, lifecycle, metadata composition, customization, and migration call paths were traced.
- Relevant upstream tests were located with exact immutable links.
- A separate adversarial pass challenged common claims and identified the drift table above.

### Open verification

- No Frappe integration tests have run locally because the project Bench is not installed yet.
- External documentation URLs are mutable and need re-retrieval during upgrades.
- Request-level commits, background-worker retries, and third-party app hook order require runtime tests.
- Czech legal-domain claims are outside this Framework module.

## Source map

### Official documentation

- [Understanding DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes)
- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [Controllers](https://docs.frappe.io/framework/user/en/basics/doctypes/controllers)
- [Customizing DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes/customize)
- [Allow on Submit](https://docs.frappe.io/framework/doctypes/allow-on-submit)
- [Database Migrations](https://docs.frappe.io/framework/user/en/database-migrations)

### Pinned source

- [Frappe v16.27.1 tree](https://github.com/frappe/frappe/tree/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b)
- [DocType controller](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py)
- [Document lifecycle](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py)
- [Metadata composition](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/meta.py)
- [MariaDB schema](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/mariadb/schema.py)
- [Migration runner](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/migrate.py)

### Pinned tests

- [DocType test suite](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/test_doctype.py)
- [Document test suite](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_document.py)
- [Module export and sync tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_modules.py)
