---
title: Frappe Runtime Boundaries and Request Lifecycle
kind: reference
status: accepted
evidence_grade: source-verified
scope: Frappe v16.27.1 at f33ac3f00ab818e21b25ddbec93efb653fd9aa1b
last_verified: 2026-07-21
---

# Frappe Runtime Boundaries and Request Lifecycle

## Direct answer

The planned local system is one Bench, one site, and three apps installed on that site:

```text
one Bench workspace
├── frappe     framework
├── erpnext    accounting and other ERP domains
├── custom app Czech behavior and agent integration
└── one site   database, files, config, and installed-app state
```

Frappe and ERPNext are both required. The Czech app extends ERPNext and depends on it. An app being present under Bench does not mean it is installed on the site.

## Use this when

Use this note for installation planning, app creation, module ownership, configuration scope, HTTP transaction behavior, or any command that changes a site.

## Official model

The official [Architecture](https://docs.frappe.io/framework/user/en/basics/architecture), [Directory structure](https://docs.frappe.io/framework/user/en/basics/directory-structure), [Apps](https://docs.frappe.io/framework/user/en/basics/apps), and [Sites](https://docs.frappe.io/framework/user/en/basics/sites) pages establish the conceptual boundaries:

- Bench is the workspace and process boundary.
- An app is a Python package containing metadata, code, assets, hooks, and migrations.
- A site is a tenant with database, files, and configuration.
- A module organizes app-owned DocTypes and other artifacts.

## Pinned implementation

### App present versus app installed

[`get_all_apps`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/__init__.py#L904-L920) reads Bench app availability and forces Frappe first. [`get_installed_apps`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/__init__.py#L923-L942) reads the site's `installed_apps` state from its database.

[`install_app`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/installer.py#L270-L348) validates availability, installs module definitions, synchronizes schema, records the installation, then synchronizes jobs, fixtures, customizations, and dashboards.

Consequences:

- cloning an app into Bench does not activate it for a site;
- installing it is a database-changing operation;
- agent commands should always name the site explicitly;
- application hooks and schema are site-specific through the installed-app set.

### Modules map back to apps

[`get_module_list` and module-map setup](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/__init__.py#L1038-L1081) read `modules.txt` and map modules to owning apps. A standard DocType must be assigned to a module whose owning app is intentional.

### Exact request outline

Pinned Frappe handles a normal request in this broad sequence:

```text
resolve site
-> initialize site and database context
-> parse request data
-> before_request hooks
-> authenticate
-> route legacy command, API v1/v2, or website
-> commit unsafe HTTP methods on success, otherwise roll back
-> roll back on exception
-> after_request hooks
-> after-response callbacks and context destruction
```

[`frappe.app.application`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/app.py#L96-L166) covers initialization, authentication, routing, exception handling, and response creation. [`init_request`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/app.py#L177-L208) selects and initializes the site and request context.

[`sync_database`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/app.py#L421-L435) commits unsafe HTTP methods and rolls back safe requests unless a commit flag was deliberately set. Database commit and rollback callbacks are implemented in [`frappe.database.Database`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/database/database.py#L1176-L1215).

Safe conclusion:

- mutations belong behind POST, PUT, PATCH, or DELETE;
- a mutating GET conflicts with request transaction semantics;
- queue derived work with `enqueue_after_commit=True` when it must not run after rollback;
- document hooks must not hide arbitrary partial commits.

### Configuration precedence

The current [Configuration](https://docs.frappe.io/framework/user/en/basics/site_config) page says site config overrides common config. [`get_site_config`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/config.py#L14-L106) confirms common config is loaded first, site config overlays it, supported environment/database values follow, and explicit extra configuration hooks apply last.

Do not print the complete configuration because it can contain credentials and encryption material. Inspect only named non-secret keys.

## Implementation runbook

1. Create or select one Bench workspace.
2. Install pinned Frappe and ERPNext apps into Bench.
3. Create one explicitly named local site with MariaDB.
4. Install ERPNext into the site.
5. Create the custom app, declare its dependency, and install it into the same site.
6. Record versions and installed apps without secrets.
7. Use one module in the custom app for Czech accounting artifacts initially.
8. Pass `--site <site>` to every agent command that can change data.

Documented command shapes:

```bash
bench new-site <site>
bench --site <site> install-app erpnext
bench new-app <custom_app>
bench --site <site> install-app <custom_app>
bench --site <site> list-apps
bench --site <site> migrate
```

Exact installation commands and dependency versions must be rechecked against the chosen deployment route before execution.

## Files and commands

Expected boundaries:

```text
frappe-bench/
├── apps/
│   ├── frappe/
│   ├── erpnext/
│   └── <custom_app>/
└── sites/
    ├── apps.txt
    ├── common_site_config.json
    └── <site>/
        └── site_config.json
```

Never commit site credentials, private files, database dumps, or API secrets.

## Failure modes

- **Treat ERPNext as a Frappe configuration:** it is a separate app that must be installed.
- **Treat the Czech app as an ERPNext fork:** it should be an installed extension app.
- **Assume an app in `apps/` is active:** installed-app database state controls participation.
- **Run state-changing Bench commands without `--site`:** creates ambiguity for automation.
- **Mutate data through GET:** conflicts with safe-method rollback behavior.
- **Enqueue before the source transaction commits:** a worker may see missing or rolled-back state.
- **Print site configuration for debugging:** exposes secrets.

## Verification

### Checked

- Current official architecture, app, site, and configuration docs.
- Exact app availability/installation, module mapping, request routing, and transaction paths in v16.27.1.
- Upstream request-hook tests were located.

### Open verification

- Actual Bench and site paths on this Mac.
- Installed Bench CLI spelling and version.
- Request commit/rollback test on the future local site.
- Custom app and module names.

## Source map

### Official documentation

- [Architecture](https://docs.frappe.io/framework/user/en/basics/architecture)
- [Apps](https://docs.frappe.io/framework/user/en/basics/apps)
- [Sites](https://docs.frappe.io/framework/user/en/basics/sites)
- [Configuration](https://docs.frappe.io/framework/user/en/basics/site_config)

### Pinned source

- [Bench apps and installed apps](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/__init__.py#L899-L942)
- [App installation](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/installer.py#L270-L348)
- [Request entrypoint](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/app.py#L96-L208)
- [HTTP transaction synchronization](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/app.py#L421-L435)
- [Configuration merge](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/config.py#L14-L106)

### Pinned tests

- [Request hook-order test](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/test_api.py#L407-L421)
- [Migrate command test](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/commands/test_commands.py#L922-L927)
