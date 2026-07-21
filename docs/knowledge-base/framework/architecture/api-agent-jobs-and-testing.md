---
title: Frappe API, Agent Integration, Jobs, and Testing
kind: reference
status: accepted
evidence_grade: source-verified
scope: Frappe v16.27.1 at f33ac3f00ab818e21b25ddbec93efb653fd9aa1b
last_verified: 2026-07-21
---

# Frappe API, Agent Integration, Jobs, and Testing

## Direct answer

Codex or Claude Code should not “log in and click around” as the primary integration. Give a dedicated least-privilege Frappe user an API credential and expose deterministic operations through normal document APIs or narrowly scoped whitelisted methods in the custom app.

For “add these 100 invoices,” the preferred architecture is:

```text
source file or payload
-> staged import record
-> dry-run parsing and validation
-> explicit mapping to ERPNext documents
-> user confirmation or approved commit action
-> enqueue after transaction commit
-> normal document insert/submit paths
-> durable per-row results and idempotency keys
-> reconciliation and audit record
```

## Use this when

Use this note for API authentication, REST versions, agent integration, batch imports, background workers, scheduling, tests, or retry design.

## Official model

The official [REST API](https://docs.frappe.io/framework/user/en/api/rest) documents API-key, session, and OAuth authentication plus resource and method routes. [Background Jobs](https://docs.frappe.io/framework/user/en/api/background_jobs) documents RQ queues and scheduler events. [Testing](https://docs.frappe.io/framework/user/en/testing) describes test execution, but some examples are stale for pinned v16.

## Pinned implementation

### Authentication

[`validate_auth`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/auth.py#L629-L644) tries bearer OAuth and API keys before custom auth hooks. [`validate_api_key_secret`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/auth.py#L687-L739) accepts Basic or token authentication, verifies the secret, and sets the request user.

An API credential acts with that user's roles and permissions. Never store the key or secret in Git, the KB, job arguments, or logs.

### REST routes

[`frappe.api`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/api/__init__.py#L23-L100) mounts legacy, v1, and v2 routes.

| Operation | v1 | v2 |
|---|---|---|
| List | `GET /api/resource/{doctype}` | `GET /api/v2/document/{doctype}` |
| Create | `POST /api/resource/{doctype}` | `POST /api/v2/document/{doctype}` |
| Read | `GET /api/resource/{doctype}/{name}` | `GET /api/v2/document/{doctype}/{name}/` |
| Update | `PUT /api/resource/{doctype}/{name}` | `PATCH` or `PUT /api/v2/document/{doctype}/{name}/` |
| Delete | `DELETE /api/resource/{doctype}/{name}` | `DELETE /api/v2/document/{doctype}/{name}/` |
| Method | `/api/method/{path}` | `/api/v2/method/{path}` |

[`frappe.api.v1`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/api/v1.py#L11-L87) and [`frappe.api.v2`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/api/v2.py#L171-L236) create and update through normal `insert()` and `save()` paths.

Choose one API version for the integration client and pin it. v2's internal Python callables are explicitly not a stable Python API even though its HTTP surface is public.

### Why a custom method is better for a batch

One whitelisted POST method can enforce:

- a versioned payload schema;
- explicit user authorization;
- Czech and ERPNext boundary validation;
- stable external identifiers;
- dry-run versus commit separation;
- mapping rules for suppliers, accounts, taxes, dates, and currencies;
- structured per-row results;
- an explicit atomic or resumable transaction contract.

Generic resource CRUD remains useful for one normal document, but 100 independent calls do not create a coherent batch audit model.

### Queue execution

[`enqueue`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/utils/background_jobs.py#L76-L209) supports site and user capture, queue selection, job IDs, callbacks, deduplication, and `enqueue_after_commit`.

[`execute_job`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/utils/background_jobs.py#L239-L317) initializes the site, restores user context, commits on success, rolls back on failure, and applies retry behavior.

Default queues are short, default, and long, with pinned timeouts in [`background_jobs.py`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/utils/background_jobs.py#L55-L73).

Persist batch progress in domain records. RQ status alone is not the accounting audit trail.

### Scheduler documentation conflict

Current official pages disagree about a one-minute versus four-minute `all` cadence and mix `scheduler_tick_interval` with `scheduler_interval`.

Pinned v16 separates them:

- scheduler wake-up uses `scheduler_tick_interval` with default 240 seconds in [`scheduler.py`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/utils/scheduler.py#L25-L26);
- the generated `All` event cadence uses `scheduler_interval`, also defaulting to 240 seconds, in [`scheduled_job_type.py`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/scheduled_job_type/scheduled_job_type.py#L113-L130).

Do not promise one-minute execution. Configure and verify both controls if sub-four-minute behavior is required.

### Pinned test architecture

Frappe v16 provides:

- [`UnitTestCase`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/classes/unit_test_case.py#L29-L56) for unit-style framework helpers;
- [`IntegrationTestCase`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/tests/classes/integration_test_case.py#L20-L73) for site/database setup and rollback.

The current Testing page still shows `--skip-test-records`. Pinned CLI marks it deprecated and exits without running tests in [`testing.py`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/commands/testing.py#L304-L305). Never use that option.

The test CLI requires `allow_tests` unless CI is set, enforced in [`testing.py`](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/commands/testing.py#L347-L360).

## Implementation runbook

### Agent integration

1. Create a dedicated API user and least-privilege role set.
2. Define a custom Batch Import DocType and child/result records if durable progress is required.
3. Add a versioned schema validator at the API boundary.
4. Add a dry-run method that performs parsing, duplicate detection, mapping, and totals without writes.
5. Add a commit method that checks the approved dry-run revision.
6. Use an external ID unique field per source invoice.
7. Enqueue large execution only after the request commits.
8. Create ERPNext documents through their normal lifecycle.
9. Decide explicitly between all-or-nothing and resumable per-record commits.
10. Reconcile input counts and amounts to created documents and ledgers.

### Minimum failure scenarios

- duplicate upload;
- duplicate source ID within one file;
- retry after worker termination;
- row 57 validation failure;
- missing supplier/account/tax mapping;
- closed accounting period;
- foreign-currency rate missing;
- user can create drafts but cannot submit;
- source invoice already exists or is already submitted;
- enqueue request rolls back before commit.

### Test commands

Pinned command shape:

```bash
bench --site <test_site> set-config allow_tests true
bench --site <test_site> run-tests --app <custom_app>
bench --site <test_site> run-tests --module <python.module>
bench --site <test_site> run-tests --doctype "<DocType>"
```

Use the actual command result, site, commit, and date when promoting a note to test-verified.

## Files and commands

Expected custom-app surfaces:

```text
<app>/<app>/api.py
<app>/<app>/hooks.py
<app>/<app>/<module>/doctype/<batch_doctype>/
<app>/<app>/<module>/doctype/<batch_row_doctype>/
<app>/<app>/tests/
```

Do not expose arbitrary Python execution, Bench Console, or database access to an agent integration.

## Failure modes

- **Use Administrator token:** hides permission failures and grants destructive scope.
- **Put API secret in `.env` output or KB:** credentials must remain secret.
- **Issue 100 generic creates without idempotency:** retry creates duplicates.
- **Submit immediately during initial import:** removes the review boundary.
- **Queue before commit:** worker can observe rolled-back state.
- **Assume RQ status is durable audit evidence:** jobs expire and lack domain reconciliation.
- **Assume deduplication makes business logic idempotent:** it only controls queue duplication under defined conditions.
- **Rely on one-minute scheduler docs:** pinned defaults are 240 seconds and keys control different stages.
- **Use stale `--skip-test-records`:** pinned CLI exits without running tests.

## Verification

### Checked

- Current official REST, background jobs, and testing docs.
- Exact v16.27.1 auth, routes, document API persistence, enqueue/worker behavior, scheduler controls, test classes, and CLI.
- Upstream tests for enqueue-after-commit and scheduler synchronization were located.

### Open verification

- Actual API-key request on the local site.
- Selected API version.
- Batch transaction and review policy.
- Redis worker, commit/rollback, retry, and scheduler behavior on the Mac.
- Project integration test suite.

## Source map

### Official documentation

- [REST API](https://docs.frappe.io/framework/user/en/api/rest)
- [Background Jobs](https://docs.frappe.io/framework/user/en/api/background_jobs)
- [Background Services](https://docs.frappe.io/framework/user/en/bench/resources/background-services)
- [Testing](https://docs.frappe.io/framework/user/en/testing)

### Pinned source

- [Authentication](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/auth.py#L629-L744)
- [API routing](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/api/__init__.py#L23-L100)
- [v2 document routes](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/api/v2.py#L171-L299)
- [Enqueue and job execution](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/utils/background_jobs.py#L76-L317)
- [Test CLI](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/commands/testing.py#L285-L380)

### Pinned tests

- [Enqueue-after-commit test](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/rq_job/test_rq_job.py#L144-L162)
- [Scheduler synchronization test](https://github.com/frappe/frappe/blob/f33ac3f00ab818e21b25ddbec93efb653fd9aa1b/frappe/core/doctype/scheduled_job_type/test_scheduled_job_type.py#L46-L64)
