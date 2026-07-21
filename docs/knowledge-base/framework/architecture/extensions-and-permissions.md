---
title: Frappe Extensions and Permissions
kind: reference
status: accepted
evidence_grade: source-verified
scope: Frappe v16.27.1 at f33ac3f00ab818e21b25ddbec93efb653fd9aa1b
last_verified: 2026-07-21
---

# Frappe Extensions and Permissions

## Direct answer

Keep Frappe and ERPNext unchanged and route Czech behavior through the custom app. Prefer the narrowest mechanism:

1. standard roles, DocPerm, User Permissions, and sharing for grants;
2. `doc_events` for narrow lifecycle reactions;
3. `extend_doctype_class` for reusable class behavior;
4. `override_doctype_class` only when full replacement is unavoidable;
5. `has_permission` only for additional denial, not as the grant mechanism;
6. `permission_query_conditions` for list filtering, paired with document permission checks.

## Use this when

Use this note when extending ERPNext controllers, registering hooks, limiting agent access, or diagnosing why direct document access and list results differ.

## Official model

The official [Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks) page documents `doc_events`, controller extension and override, method override, permission hooks, list-query conditions, fixtures, scheduler events, and request hooks.

The official [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions) page describes users, roles, DocType permissions, permission levels, owner rules, and User Permissions.

## Pinned implementation

### Hook loading order and cache

[`get_hooks`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/__init__.py#L962-L1014) imports installed-app `hooks.py` values and caches the merged result. [`_dict` merge handling](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/__init__.py#L1017-L1035) collects values in installed-app order.

Consequences:

- order is site-dependent, not alphabetical folklore;
- the last override hook wins where the API is defined that way;
- Python and hook changes can require cache clearing and worker restart;
- scheduler hook changes require migration because database job records are synchronized.

### Controller extension and override

[`import_controller`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L82-L140) loads the standard controller, selects the last `override_doctype_class`, then applies extension composition.

[`_get_extended_class`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L179-L208) reverses extension paths before constructing the dynamic class. Later app extensions therefore appear earlier in method resolution order.

Every mixin method that participates in a chain must call `super()`. Failing to do so can cut off other apps or the original ERPNext controller.

### `doc_events` order

For a named controller event, [`Document.run_method`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1238-L1258) and [`Document.hook`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1605-L1655) run:

1. controller method;
2. exact-DocType handlers;
3. wildcard handlers;
4. notifications;
5. webhooks;
6. Server Scripts.

Handlers run with transaction control disabled around the handler call. Do not commit or roll back inside normal document-event handlers.

### Permission layers

The practical model is:

```text
authenticated identity
-> controller permission hook may deny
-> role and permission-level rules
-> owner constraints
-> User Permission restrictions
-> sharing fallback
-> list query conditions for collections
-> field-level read filtering
```

[`has_permission`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/permissions.py#L79-L224) handles Administrator, child and Single cases, role/document rules, and sharing. [`get_doc_permissions`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/permissions.py#L227-L279) combines controller checks, roles, ownership, and User Permissions.

### Documentation conflict: `has_permission` cannot grant

The current Hooks page can be read as if returning `True` grants access. In pinned v16, [`has_controller_permissions`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/permissions.py#L481-L498) states controller hooks can only deny. A truthy result permits normal evaluation to continue; it does not create missing base permission.

Safe rule: grant through roles, DocPerm or Custom DocPerm, User Permissions, or sharing. Use `has_permission` for extra denial.

### List permission differs from direct document permission

[`permission_query_conditions`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/db_query.py#L1157-L1180) are AND-composed into list queries. They do not by themselves decide a direct `frappe.get_doc` read.

`frappe.get_list` applies list permissions. `frappe.get_all` bypasses ordinary list permission filtering and must not be exposed to untrusted integration callers.

The v1 document endpoint performs direct read permission and field-level filtering in [`frappe.api.v1`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/api/v1.py#L73-L87).

## Implementation runbook

### Extend a standard ERPNext document

1. Read the original controller and focused tests.
2. Identify the exact lifecycle method and whether ordering matters.
3. Use `doc_events` for a narrow event or `extend_doctype_class` for class behavior.
4. Avoid wildcard hooks unless the rule is genuinely global.
5. Call `super()` from mixins.
6. Clear caches, restart relevant processes, and migrate if hooks materialize database records.
7. Test original ERPNext behavior plus the extension.

### Configure a dedicated agent user

1. Create a separate enabled User.
2. Grant only the minimum role and DocType permissions.
3. Add User Permission constraints where company or other link scope requires it.
4. Use normal document APIs so server validation and permission checks execute.
5. Test one allowed operation and one forbidden operation with that exact user.
6. Test both list visibility and direct document access.
7. Never grant Administrator simply to bypass permission design.
8. Rotate the API secret independently of human accounts.

## Files and commands

Expected app files:

```text
<app>/<app>/hooks.py
<app>/<app>/<module>/doctype/
<app>/<app>/fixtures/
```

After hook changes, the required operations depend on hook type. Do not turn “clear cache, migrate, restart everything” into ritual. Record which cache or synchronized database record the hook uses.

## Failure modes

- **Two apps override the same controller:** only the last override is selected.
- **Mixin omits `super()`:** breaks the dynamic class chain.
- **Grant access only through `has_permission`:** pinned source does not allow it to grant missing permission.
- **Use only `permission_query_conditions`:** direct reads can still follow document permission logic.
- **Expose `get_all` to an untrusted caller:** bypasses ordinary list filtering.
- **Give the agent Administrator:** defeats least privilege and hides permission defects.
- **Commit inside `doc_events`:** breaks request transaction control.
- **Use broad wildcard events for accounting:** creates unrelated side effects and upgrade risk.

## Verification

### Checked

- Current official Hooks and permissions documentation.
- Exact hook collection, controller composition, document-event order, permission evaluation, and list filtering source.
- Upstream extension, permission-hook, and permission tests were identified.

### Open verification

- Installed-app order on the future site.
- Exact ERPNext controllers that Czech code will extend.
- Dedicated user roles and company scoping.
- Runtime list/direct/API permission matrix.

## Source map

### Official documentation

- [Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)

### Pinned source

- [Hook loading and cache](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/__init__.py#L962-L1035)
- [Controller loading, override, and extension](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/base_document.py#L82-L208)
- [Document method and event composition](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/model/document.py#L1238-L1258)
- [Permission evaluation](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/permissions.py#L79-L279)
- [Deny-only controller permission hooks](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/permissions.py#L481-L498)

### Pinned tests

- [Controller extension composition](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_base_document.py#L44-L124)
- [Override and permission hooks](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_hooks.py#L11-L77)
- [Permission retrieval behavior](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_permissions.py#L79-L117)
