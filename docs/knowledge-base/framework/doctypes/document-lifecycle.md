---
title: Document Lifecycle and Controller Hooks
kind: reference
status: accepted
evidence_grade: source-verified
scope: Frappe v16.27.1 at f33ac3f00ab818e21b25ddbec93efb653fd9aa1b
last_verified: 2026-07-21
---

# Document Lifecycle and Controller Hooks

## Direct answer

Put business invariants in the DocType's Python controller or a documented app hook, not only in client JavaScript. The exact lifecycle depends on the action.

The central sequences in v16.27.1 are:

```text
Insert
permission/link checks
-> before_insert
-> naming
-> before_validate
-> validate
-> before_save
-> framework validation
-> parent DB insert
-> child DB inserts
-> after_insert
-> on_update
-> cache/search/version/notification work
-> on_change

Save existing draft
permission/concurrency/link checks
-> before_validate
-> validate
-> before_save
-> framework validation
-> parent DB update
-> child synchronization
-> on_update
-> cache/search/version/notification work
-> on_change

Submit
before_validate
-> validate
-> before_submit
-> framework validation and DB update with docstatus 1
-> child synchronization
-> on_update
-> on_submit
-> post-save work
-> on_change

Cancel
before_cancel
-> DB update with docstatus 2
-> child synchronization
-> on_cancel
-> backlink check
-> post-save work
-> on_change

Update after submit
before_update_after_submit
-> allow-on-submit validation
-> DB update
-> child synchronization
-> on_update_after_submit
-> post-save work
-> on_change
```

This is a source-derived operational outline. It omits internal helper calls that an application normally should not override.

## Use this when

Use this note to decide where to:

- calculate or normalize values;
- reject invalid accounting documents;
- post or reverse ledger effects;
- integrate after a committed business transition;
- permit narrow metadata edits after submission;
- write lifecycle tests;
- diagnose duplicate or unexpectedly repeated side effects.

This note does not prove transaction commit boundaries for external integrations. Queue irreversible external work through a separately designed, idempotent integration flow.

## Official model

The official [Controllers](https://docs.frappe.io/framework/user/en/basics/doctypes/controllers) page defines a controller as a Python class extending `frappe.model.Document`. It lists hooks for insert, save, submit, cancel, update-after-submit, rename, and deletion.

Important documented guidance:

- `db_insert` and `db_update` are low-level operations and generally should not be overridden except for Virtual DocTypes.
- `on_change` can also be caused by `db_set`, so it must be idempotent.
- type annotations can be generated into controllers when the app opts in.

The docs provide a hook matrix, not the full call graph or transaction model. The precise ordering below comes from pinned source.

## Pinned implementation

### Insert path

[`Document.insert`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L431-L520) performs, in order:

1. defaults, user/timestamp, and draft status;
2. create permission and freshness checks;
3. link validation;
4. `before_insert`;
5. document and child naming;
6. parent relationship and higher-permission validation;
7. the before-save method dispatcher;
8. framework `_validate`;
9. parent persistence, with a Single-specific branch;
10. direct child inserts unless the DocType is Virtual;
11. `after_insert`;
12. amendment/file work;
13. the post-save dispatcher.

Inside step 7, [`run_before_save_methods`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1383-L1413) calls `before_validate`, then `validate`, then `before_save` for the normal save action.

Inside step 13, [`run_post_save_methods`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1437-L1469) calls `on_update` for save, then cache notification, global search, versioning, and finally `on_change`.

This explains a common surprise: a newly inserted document invokes both `after_insert` and `on_update`.

### Existing save path

[`Document._save`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L552-L611) routes an unsaved object back to `insert`. For an existing object it performs lock, permission, timestamp, freshness, parent/child, link, before-save, and framework validation before updating the parent and synchronizing children.

Application code must not assume child rows have already been synchronized while `validate` or `before_save` runs. Those hooks execute before the parent DB update and `update_children` call.

### Submit and cancel

[`Document.submit` and `cancel`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1338-L1346) delegate to internal actions that set the target docstatus and save.

The before-save dispatcher calls:

- submit: `before_validate`, `validate`, `before_submit`;
- cancel: `before_cancel` only;
- update after submit: `before_update_after_submit`.

The post-save dispatcher calls:

- submit: `on_update`, then `on_submit`;
- cancel: `on_cancel`, then a no-backlinks check;
- update after submit: `on_update_after_submit`.

Do not assume `validate` runs during cancel based only on its name. The pinned dispatcher does not call it for the cancel action.

### Update after submit

[`BaseDocument._validate_update_after_submit`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L1270-L1305) loads stored values and rejects a changed non-virtual field whose metadata does not allow editing after submission. It also checks child rows and table sizes through the document validation flow.

For Czech accounting documents, do not mark amounts, tax bases, rates, dates, parties, accounts, currency, quantities, or posting-driving state as `allow_on_submit`. The official [Allow on Submit](https://docs.frappe.io/framework/doctypes/allow-on-submit) page recommends cancel-and-amend for transaction-changing corrections.

### `on_change` is a broad notification, not a one-time event

`run_post_save_methods` calls `on_change` after normal persistence actions. The official controller docs also note that `db_set` can trigger it. Therefore:

- make repeated execution safe;
- do not create an irreversible external side effect without an idempotency key;
- do not assume it means the document was newly inserted;
- avoid using it as the only accounting posting trigger.

### Controller methods and `doc_events` are composed

For each named event, [`Document.run_method`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1238-L1258) runs the controller method through a composed handler. [`Document.hook`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1605-L1655) gives this order:

1. controller method;
2. exact-DocType `doc_events` handlers;
3. wildcard `*` `doc_events` handlers;
4. notifications;
5. webhooks;
6. matching Server Scripts.

Across apps, handler accumulation follows installed-app ordering, not an assumed alphabetical order. When accounting behavior depends on ordering, inspect the site's installed apps and prove the order with an integration test.

### A pinned v16 restriction missing from the current guide

The current Allow on Submit guide broadly describes enabling the property through Customize Form. In v16.27.1, [`CustomizeForm.validate_allow_on_submit`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/custom/doctype/customize_form/customize_form.py#L321-L350) refuses to turn the property on for a standard field when the owning standard DocField did not already permit it.

Safe rule for this project: use a dedicated harmless Custom Field when post-submit metadata is required. Do not assume Customize Form can unlock an arbitrary ERPNext standard field, and never use `db_set` to evade the check.

### Deletion has a separate path

[`Document.delete`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1372-L1381) delegates to `frappe.delete_doc`; it is not a save action. Use the documented `on_trash` and `after_delete` hooks and inspect delete behavior separately when retention matters.

## Implementation runbook

For each controller rule, classify it before coding:

| Need | Preferred location | Reason |
|---|---|---|
| Fill a missing derived value before validation | `before_validate` | Later validation sees normalized data |
| Enforce a business invariant on draft and submit | `validate` | Runs on save and submit |
| Enforce only the transition to submitted | `before_submit` | Can reject before persistence |
| Apply submitted-state effects | `on_submit` | Transition-specific post-save hook |
| Reverse submitted-state effects | `on_cancel` | Cancellation-specific hook |
| Permit and react to approved metadata edits | `before_update_after_submit` and `on_update_after_submit` | Explicit submitted-update lifecycle |
| Keep a repeated cache or derived projection current | idempotent `on_change` | May run from multiple paths |
| Client interaction only | `<doctype>.js` | Never rely on it for server integrity |

Then write tests for at least:

1. valid draft insert;
2. invalid draft rejection;
3. valid submit and exact durable effects;
4. failed submit without partial business effects;
5. cancel and reversal;
6. disallowed post-submit edit;
7. allowed metadata edit;
8. repeated execution of any integration-facing handler.

For accounting posting code, add explicit idempotency checks and assert ledger balance. Lifecycle placement alone does not guarantee idempotency.

## Files and commands

Typical app-owned files:

```text
<app>/<app>/<module>/doctype/<doctype>/<doctype>.py
<app>/<app>/<module>/doctype/<doctype>/<doctype>.js
<app>/<app>/<module>/doctype/<doctype>/test_<doctype>.py
```

Focused test command pattern:

```bash
bench --site <site> run-tests --app <app> --doctype "<DocType>"
```

During debugging, inspect the action and status explicitly in tests rather than inferring them from which UI button was clicked.

## Failure modes

- **Put validation only in JavaScript:** API, imports, background jobs, and server code can bypass it.
- **Assume `after_insert` is the final insert hook:** `on_update` and `on_change` follow it.
- **Assume `validate` runs for cancel:** the pinned cancel branch calls `before_cancel`, not `validate`.
- **Send external requests directly from a repeatable hook:** retry or repeated `on_change` execution can duplicate effects.
- **Override `db_insert` or `db_update` for a normal DocType:** bypasses framework persistence expectations.
- **Use `allow_on_submit` for ledger-driving fields:** destroys the meaning of submission as a locked transaction state.
- **Assume Customize Form can unlock any standard field:** pinned v16 rejects enabling the property on a previously locked standard DocField.
- **Assume a successful hook means the database transaction has committed:** commit boundaries are not proven by this note.
- **Enable Server Scripts to fix an app controller:** these are different mechanisms; the official tutorial troubleshooting note is not sufficient justification.

## Verification

### Checked

- Current official controller and Allow on Submit references, retrieved 2026-07-21.
- Exact v16.27.1 insert, existing save, before-save, post-save, submit/cancel, delete delegation, and update-after-submit field validation source.
- Relevant upstream test locations were identified.

### Open verification

- Runtime hook-order trace on the project's site.
- Exact interaction order among controller methods, `doc_events`, override hooks, workflows, and Server Scripts.
- Transaction boundaries, rollback of external side effects, and worker retry semantics.
- Delete retention policy for Czech accounting records. Deletion should likely be restricted, but that requires a project decision and legal evidence.

## Source map

### Official documentation

- [Controllers and lifecycle matrix](https://docs.frappe.io/framework/user/en/basics/doctypes/controllers)
- [Controller Methods tutorial](https://docs.frappe.io/framework/user/en/tutorial/controller-methods)
- [Docstatus](https://docs.frappe.io/framework/doctypes/docstatus)
- [Allow on Submit](https://docs.frappe.io/framework/doctypes/allow-on-submit)

### Pinned source

- [`Document.insert`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L431-L520)
- [`Document._save`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L552-L611)
- [Submit, cancel, delete delegation](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1338-L1381)
- [Before-save dispatcher](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1383-L1413)
- [Post-save dispatcher](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1437-L1469)
- [Update-after-submit field enforcement](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L1270-L1305)
- [Named method and `doc_events` composition](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1238-L1258)
- [Handler order, notifications, webhooks, and Server Scripts](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1605-L1655)
- [Customize Form restriction for Allow on Submit](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/custom/doctype/customize_form/customize_form.py#L321-L350)

### Pinned tests

- [Document integration tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_document.py)
- [DocType integration tests](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/doctype/test_doctype.py)
- [Update-after-submit test search entry](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_document.py)
