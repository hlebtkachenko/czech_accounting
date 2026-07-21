---
title: DocType Ownership and Generated Artifacts
kind: reference
status: accepted
evidence_grade: source-verified
scope: Frappe v16.27.1 at f33ac3f00ab818e21b25ddbec93efb653fd9aa1b
last_verified: 2026-07-21
---

# DocType Ownership and Generated Artifacts

## Direct answer

For changes that belong to this project and must survive rebuilds, create or extend DocTypes through a custom Frappe app and keep the resulting files in Git.

There are two distinct ownership paths:

| Path | `custom` value | Source of truth | Normal purpose |
|---|---:|---|---|
| Standard app-owned DocType | `0` | `<doctype>.json` and controller files in an installed app | New project models and behavior |
| Custom site-owned DocType | `1` | Site database metadata, unless separately exported through supported mechanisms | Rapid site-only configuration |

Developer mode is required to create or change a non-custom standard DocType through Desk in a normal runtime. It is not universally required to create a custom site DocType.

## Use this when

Use this note when an agent must:

- create a source-controlled DocType;
- understand why files were or were not generated;
- decide whether a change belongs in Git or only in site metadata;
- add a controller, form script, or tests;
- move a DocType between modules;
- enable developer mode;
- review generated file changes before commit.

Use [Schema Sync and Migrations](schema-sync-and-migrations.md) for deploying those files and [Extension Decision Guide](extension-decision-guide.md) for modifying ERPNext-owned DocTypes.

## Official model

The official [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype) tutorial says developer mode enables app boilerplate creation and source tracking. Its worked example creates a normal table and, with `Custom?` unchecked, generates JSON, JavaScript, Python controller, and test files.

The tutorial's MariaDB 10.4.13 Homebrew transcript, 2020 timestamps, and `master` branch are historical output, not current installation requirements.

The official [developer mode guide](https://docs.frappe.io/framework/user/en/guides/app-development/how-enable-developer-mode-in-frappe) shows `bench set-config -g developer_mode 1` and also discusses editing a site's `site_config.json`. Because that page does not reconcile global and site scope, inspect effective configuration after setting it.

## Pinned implementation

### The actual developer-mode rule

[`DocType.check_developer_mode`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L326-L342) provides the exact rule:

1. Patch and test contexts bypass the check.
2. Outside those contexts, developer mode must be enabled when `custom` is false.
3. A custom DocType can be created without developer mode.
4. A custom Virtual DocType is prohibited.
5. In developer mode, an ownerless DocType is assigned to Administrator.

Therefore, the tutorial phrase “before we can create DocTypes” is too broad. The precise statement is: developer mode is required for a normal Desk operation that creates a standard app-owned DocType, not for every possible custom DocType creation.

### Save first synchronizes metadata and schema

[`DocType.on_update`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L530-L568) calls `frappe.db.updatedb` before the export branch. It then exports only when all these conditions are true:

- the DocType is not custom;
- the operation is not importing;
- developer mode or the explicit export flag is active.

Do not describe the Desk save as “writing JSON which then creates the table” in strict execution-order terms. In this path, the live DocType update invokes database schema synchronization and then exports the standard definition.

### Files generated in v16.27.1

[`DocType.export_doc`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L885-L890) writes the standard metadata under:

```text
<module>/doctype/<scrubbed_doctype>/<scrubbed_doctype>.json
```

[`DocType.make_controller_template`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L891-L911) creates:

- a Python controller for every standard DocType;
- a Python test and JavaScript controller only when it is not a child table;
- a tree controller for a tree DocType;
- HTML templates when web view is enabled.

Boilerplate creation does not overwrite an existing file. Generated files are a starting point, not proof that business behavior exists.

### Field order and export normalization

[`DocType.before_export`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L796-L865) removes empty values from exported metadata, records form order in `field_order`, and attempts to preserve the existing JSON field-definition order. A reorder may therefore change `field_order` without mechanically reordering every object in `fields`.

This matters during code review: inspect semantic metadata and `field_order`, not only line movement.

### Type annotations are opt-in

[`DocType.export_types_to_controller`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L913-L923) writes generated controller annotations only when the owning app enables the `export_python_type_annotations` hook. The official controller docs say the generated annotation block is regenerated when the DocType changes, so do not hand-edit that block.

### Moving a module does not move old files

[`DocType.warn_on_module_change`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L867-L883) warns that exporting under a new module leaves the previous module directory behind. An agent must inspect both directories, move intentional code carefully, and archive obsolete files rather than assuming Frappe relocated them.

## Implementation runbook

### Create a new app-owned DocType

1. Confirm that the custom app is installed on the site and its module exists.
2. Take a site backup before persistent schema work.
3. Enable developer mode and inspect the effective configuration.
4. In Desk, create the DocType in the custom app's module with `Custom?` unchecked.
5. Save once, then inspect generated files immediately.
6. Review the JSON flags, fields, permissions, naming, and module.
7. Add controller behavior only where server-side invariants require it.
8. Replace placeholder tests with meaningful cases.
9. Run migration and focused tests against the development site.
10. Commit the app files and migration code together.

### Enable and verify developer mode

From the Bench directory:

```bash
bench set-config -g developer_mode true
bench --site <site> show-config
```

Restart development processes or clear cache if the running process has not reloaded configuration. Do not infer scope only from the command's success message.

### Review generated artifacts

For a DocType named `Czech VAT Control Statement`:

```text
<app>/<app>/<module>/doctype/czech_vat_control_statement/
  __init__.py
  czech_vat_control_statement.json
  czech_vat_control_statement.py
  czech_vat_control_statement.js
  test_czech_vat_control_statement.py
```

Exact optional files depend on child, tree, and web-view flags. The path uses scrubbed Python names; the SQL table retains `tab` plus the DocType name.

## Files and commands

Useful read-only checks:

```bash
bench --site <site> list-apps
bench --site <site> show-config
git status --short
git diff -- <app>/<app>/<module>/doctype/
```

Focused test pattern after implementation:

```bash
bench --site <site> run-tests --app <app> --doctype "<DocType>"
```

Treat the command as a planned project check until it has been executed on the actual site and its result recorded.

## Failure modes

- **Create the DocType as Custom and expect standard files:** source export is gated by `not self.custom`.
- **Enable developer mode and assume all changes are Git-backed:** Customize Form and custom records still need deliberate export or fixture handling.
- **Use the tutorial's old MariaDB transcript as a dependency specification:** it is historical example output.
- **Edit a generated type-annotation block:** later DocType saves can regenerate it.
- **Move a DocType to another module and delete the old directory blindly:** the old directory can contain controller code that Frappe did not move.
- **Commit generated boilerplate without real tests:** file existence is not behavior verification.
- **Use developer mode as an authorization boundary:** it controls standard metadata export behavior, not user permissions or code review.
- **Create a Virtual DocType as custom:** v16.27.1 rejects it.

## Verification

### Checked

- Current official creation and developer-mode guides, retrieved 2026-07-21.
- Exact v16.27.1 validation gate, schema-update/export branch, boilerplate generation, type annotation hook, and module-move warning.
- Upstream test source for field order export and reload behavior.

### Open verification

- The project's Bench version and exact global-versus-site configuration precedence.
- Actual generated files on the future custom app, because app and DocType names are not yet chosen.
- The focused test command on a running project site.
- Whether generated Python type annotations should be enabled is a project decision.

## Source map

### Official documentation

- [Create a DocType](https://docs.frappe.io/framework/user/en/tutorial/create-a-doctype)
- [How to Enable Developer Mode in Frappe](https://docs.frappe.io/framework/user/en/guides/app-development/how-enable-developer-mode-in-frappe)
- [Controllers, Type Annotations](https://docs.frappe.io/framework/user/en/basics/doctypes/controllers)

### Pinned source

- [DocType validation and developer-mode check](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L186-L230)
- [Exact developer-mode and custom Virtual rules](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L326-L342)
- [Schema update and export gate](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L530-L568)
- [Export normalization and field order](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L796-L865)
- [Module-move warning and generated artifacts](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/doctype.py#L867-L923)

### Pinned tests

- [Field-order export and reload test](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/test_doctype.py#L204-L323)
- [Module reload tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_modules.py#L165-L180)
