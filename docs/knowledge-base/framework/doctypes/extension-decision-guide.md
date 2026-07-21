---
title: Extension Decision Guide for DocTypes and Fields
kind: reference
status: accepted
evidence_grade: source-verified
scope: Frappe v16.27.1 and extending ERPNext without upstream edits
last_verified: 2026-07-21
---

# Extension Decision Guide for DocTypes and Fields

## Direct answer

Use the smallest source-controlled extension that matches ownership:

| Need | Mechanism | Source-controlled form |
|---|---|---|
| New reusable business entity owned by this project | Standard DocType in the custom app | DocType JSON, controller, JS, tests |
| New ordered rows owned exclusively by one parent | Standard child DocType plus a Table field | Child DocType JSON and parent metadata/customization |
| Add a field to an ERPNext-owned DocType | Custom Field | Exported customization, fixture, or install code with tests |
| Change a property of an ERPNext field or DocType | Property Setter, only after conflict review | Exported customization or fixture |
| Add behavior without replacing ERPNext controller | `extend_doctype_class` or `doc_events` | Custom app `hooks.py` and Python code |
| Fully replace controller behavior | `override_doctype_class`, rarely | Custom app `hooks.py` and subclass |
| One site-wide project setting | Standard Single DocType in the custom app | DocType JSON and controller |
| External data shown as Frappe records | Standard Virtual DocType | DocType JSON and full controller contract |
| One-off site experiment | Custom DocType or Customize Form | Database-owned until deliberately promoted |

Do not edit Frappe or ERPNext upstream JSON for Czech requirements. Keep upstream apps clean and put owned schema, fields, hooks, patches, and tests in the custom app.

## Use this when

Use this note when an agent asks:

- “Should I add a DocType or a Custom Field?”
- “Can I edit Sales Invoice JSON?”
- “Should this be a child table?”
- “Where should Czech-specific behavior live?”
- “How do we make a Desk customization reproducible?”
- “Should I override or extend an ERPNext controller?”

This is an engineering decision guide. Czech legal requirements must be mapped separately before choosing the final data model.

## Official model

The official [Customizing DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes/customize) page distinguishes Custom Field, Property Setter, Customize Form, Client Script, Server Script, and custom permissions. Customize Form creates override records rather than modifying the underlying standard DocType.

The official [Exporting Customizations to your App](https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations) guide exports Custom Fields, Property Setters, and custom permissions into an app module. It warns that synchronization replaces the site's Property Setters and custom permissions with the exported code-defined set.

The official [Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks) reference documents fixtures and controller extension mechanisms. Current docs are navigation; exact v16 behavior is pinned below.

## Pinned implementation

### Effective metadata is composed

[`Meta.process`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/meta.py#L166-L182) loads the base DocType and then composes runtime metadata. [`Meta.add_custom_fields`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/meta.py#L404-L420) appends Custom Fields, while [`Meta.apply_property_setters`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/meta.py#L422-L462) overlays properties.

This means a Custom Field is neither a direct edit to ERPNext JSON nor a separate DocType. It is a customization record merged into the target DocType's effective metadata.

### Stored Custom Fields alter the target table

[`CustomField.on_update`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/custom/doctype/custom_field/custom_field.py#L208-L218) asks the database to update the target DocType schema for a non-Single target. A stored field becomes a column of that target table. A virtual or layout-only field does not.

For every Czech field added to an ERPNext DocType, record:

- target DocType and unique fieldname;
- field owner and business meaning;
- stored, virtual, or layout-only status;
- insertion point;
- export mechanism;
- upstream collision check;
- migration and uninstall consequences.

### Custom DocType is different

A custom DocType has `custom = 1`, uses generic controller resolution, and remains database-owned by default. [`import_controller`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L97-L108) resolves a custom DocType to generic `Document` or `NestedSet`, not a per-DocType app controller.

For durable Czech accounting functionality, a custom site DocType is usually a prototype, not the final delivery format.

### Extend before override

[`import_controller`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L109-L140) applies `override_doctype_class` and requires the override to subclass the original controller. [`_get_extended_class`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L179-L208) composes `extend_doctype_class` mixins.

Project rule:

1. Use `doc_events` for event-specific behavior that does not need new document methods.
2. Use `extend_doctype_class` when the document needs reusable methods or properties while preserving upstream controller behavior.
3. Use `override_doctype_class` only when extension cannot express the requirement and an upgrade review explicitly accepts full-controller coupling.

This ordering is a project decision based on upgrade risk, not a claim that Frappe mandates it.

### Exported customizations can replace site state

[`export_customizations`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/modules/utils.py#L57-L122) writes scoped customization data. [`sync_customizations`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/modules/utils.py#L125-L239) imports selected customization files during migration according to their settings.

Do not export a broad, unknown set from a personally customized site and assume it is a clean app definition. Diff existing Custom Fields, Property Setters, permissions, links, and actions first.

## Implementation runbook

### Decision sequence

1. Identify the owner of the base model.
   - This custom app: standard DocType or standard field.
   - ERPNext/Frappe: extension record or hook, never direct upstream edit.
2. Decide whether the data is an independent record or an owned row.
   - Independent identity, links, permissions, retention, numbering, or history: regular DocType.
   - Meaningless outside one parent: child DocType.
3. Decide whether persistence is required.
   - Derived display only: virtual field or view/report logic.
   - Durable business value: stored field with migration plan.
4. Decide whether behavior is event-specific or class-wide.
   - Event-specific: `doc_events`.
   - New reusable class capability: `extend_doctype_class`.
   - Full replacement: exceptional `override_doctype_class` decision.
5. Choose a reproducible export route and test it on a clean site.

### Extending an ERPNext DocType safely

For a Czech field on `Sales Invoice`:

1. Search the pinned ERPNext source for the proposed fieldname and label.
2. Choose a namespaced fieldname that is unlikely to collide.
3. Create the Custom Field through supported app code or Customize Form.
4. Export only the intended customization records.
5. Review the generated file, especially Property Setters and permissions.
6. Run `bench migrate` on a disposable or restored site.
7. Assert the effective metadata, SQL column if stored, permissions, forms, API serialization, imports, reports, and print behavior.
8. Run migration a second time and prove it is idempotent.

### Promotion rule

When a Custom DocType prototype becomes durable functionality:

- design the standard app-owned DocType explicitly;
- migrate data with a forward patch;
- do not flip ownership flags casually on the only site;
- validate files and data on a restored copy first.

The exact promotion method remains open until it is tested for this project's version and data.

## Files and commands

Likely custom-app locations:

```text
<app>/<app>/hooks.py
<app>/<app>/<module>/doctype/<doctype>/
<app>/<app>/<module>/custom/<target_doctype>.json
<app>/<app>/fixtures/
<app>/<app>/patches.txt
```

Review commands:

```bash
git status --short
git diff -- <app>/
bench --site <site> migrate
bench --site <site> run-tests --app <app>
```

Do not run export or migrate on the persistent site until the current site customizations and a restorable backup have been checked.

## Failure modes

- **Edit ERPNext DocType JSON directly:** creates an upstream fork conflict and loses the clean extension boundary.
- **Use a new DocType for one extra field:** unnecessary entity and workflow complexity.
- **Use a Custom Field for a reusable multi-row entity:** hides an independent domain object inside another record.
- **Assume Custom Field and Custom DocType mean the same thing:** they have different metadata, controller, and source behavior.
- **Export every customization from a manually changed site:** can commit unrelated Property Setters and permissions.
- **Use `override_doctype_class` for one event:** increases coupling to upstream controller internals.
- **Use Client Script for server invariants:** API and background paths can bypass it.
- **Add a field with an upstream-generic name:** a future ERPNext release may introduce the same fieldname.
- **Test only the already-customized site:** hidden site state can make a broken app appear correct.

## Verification

### Checked

- Current official customization, export, and hook documentation, retrieved 2026-07-21.
- Exact v16.27.1 metadata composition, Custom Field schema update, custom controller resolution, controller extension/override, and customization export/sync source.
- Official upstream tests for customization export/sync and class extension were identified.

### Open verification

- Final namespacing convention for Czech-specific fields.
- Whether exported customizations or narrowly filtered fixtures will be the project default.
- Clean-site installation because the custom app does not exist yet.
- Exact uninstall and collision behavior for each future customization.
- Domain decision for each Czech record and field.

## Source map

### Official documentation

- [Customizing DocTypes](https://docs.frappe.io/framework/user/en/basics/doctypes/customize)
- [Exporting Customizations to your App](https://docs.frappe.io/framework/user/en/guides/app-development/exporting-customizations)
- [Hooks and fixtures](https://docs.frappe.io/framework/user/en/python-api/hooks)

### Pinned source

- [Effective metadata composition](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/meta.py#L166-L182)
- [Custom Fields and Property Setters](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/meta.py#L404-L462)
- [Stored Custom Field schema update](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/custom/doctype/custom_field/custom_field.py#L208-L218)
- [Controller resolution and override](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L97-L140)
- [Controller extension composition](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L179-L208)
- [Customization export and synchronization](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/modules/utils.py#L57-L239)

### Pinned tests

- [Customization export and sync tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_modules.py#L77-L163)
- [Controller override tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_hooks.py#L23-L35)
- [Controller extension tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_base_document.py#L44-L124)
