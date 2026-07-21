# Reuse review: Frappe Assistant Core (FAC)

Source: https://github.com/buildswithpaul/Frappe_Assistant_Core (shallow clone `/tmp/assistant-core`, HEAD `e50c5c3`).
Reviewed read-only for our DEFERRED "assisted data entry" phase. This is an UNVERIFIED third-party app; nothing here is trusted or run.
Licence: **AGPL-3.0** (see licence note at bottom). ~35k LOC Python, 176 files, MCP 2025-06-18, "24 tools", Frappe Cloud marketplace app, actively maintained.

---

## 1. Architecture — how Frappe is exposed to the LLM

- **Custom MCP server over StreamableHTTP** (not the official MCP SDK). Single Frappe whitelisted endpoint:
  `/api/method/frappe_assistant_core.api.fac_endpoint.handle_mcp` (`@mcp.register(allow_guest=True, ...)` — guest allowed at the route, but auth is enforced inside before anything runs). JSON-RPC 2.0; `initialize` advertises `protocolVersion` + tools/prompts/resources/logging capabilities.
- **Plugin-based tool registry.** Tools are `BaseTool` subclasses (`name`, `description`, JSON `inputSchema`, `execute()`), discovered by a plugin manager, exposed via `tools/list` + `tools/call`. Third-party Frappe apps can contribute tools through an `assistant_tools` hook.
- **Per-request, per-user registry** (`_build_tool_registry`): a fresh `OrderedDict` is built on the call stack per request (issue #197 isolation) and filtered by the requesting user's permissions — concurrent requests can't clobber each other's tool set. MCP annotations (read-only vs write) are derived from each tool's category so clients can group them.
- Verdict: **REUSE-IDEA** — thin whitelisted-endpoint + typed tool-registry + per-request/per-user tool set is a clean, safe shape to imitate. **AVOID** the "generic Frappe passthrough" tool design that rides on top of it (section 2).

## 2. Tool surface — what the agent can do

Fully generic, not domain-scoped. Operations available (role-gated, see section 3):

| Tool | Operation | Risk |
|------|-----------|------|
| `get_document` / `list_documents` / `search_*` / `metadata_*` / `get_doctype_info` | read/introspect any doctype | low |
| `generate_report` / `report_execute` / `report_list` | run any Frappe report (query reports can embed SQL) | medium |
| `create_document` | create on **any** doctype; **`submit: true` auto-submits** | HIGH |
| `update_document` | update **any** doctype, incl. child-table patch/replace | HIGH |
| `submit_document` | submit a draft (docstatus 0→1) | HIGH |
| `delete_document` | delete **any** doctype; **`force: true`** bypasses link constraints | HIGH |
| `run_workflow` / `workflow_action` | drive workflow transitions | HIGH |
| `run_database_query` (`query_and_analyze`) | **raw `frappe.db.sql`**, SELECT-only via regex blacklist | CRITICAL |
| `run_python_code` (`execute_python_code`) | **arbitrary Python via `exec()`** in a sandboxed subprocess | CRITICAL |
| `extract_file_content` | OCR / file parsing (PaddleOCR) | medium |
| `create_dashboard*` | visualization/dashboard doc creation | medium |

Verdict: **AVOID** the whole generic-mutation surface for our phase. Our layer must expose a small set of domain-scoped, draft-only tools — not `create/update/delete/submit_document(doctype=*)`.

## 3. Permission / safety model — the genuinely good part

- **Runs as the real end user, never Administrator.** Auth resolves an OAuth Bearer token → `frappe.set_user(bearer_token.user)`; the code-exec subprocess connects with `set_admin_as_user=False` then `set_user(user)`. No Administrator token anywhere in the tool path.
- **Enforces Frappe permissions** (does NOT bypass): doc tools call `validate_document_access()` → `frappe.has_permission(doctype, perm_type, user=user)` at both doctype and document level. `ignore_permissions=True` appears 54× but only in migrations/patches/audit-log inserts/plugin+oauth config — **never in the data tools**.
- **Four-layer gating** in the registry (`get_available_tools` / `execute_tool`): (1) plugin enabled → (2) tool enabled (`FAC Tool Configuration`) → (3) role access (`FAC Tool Role Access`, per-tool allow-list DocType) → (4) Frappe permission. Admin-configurable via a DocType, not just code.
- **Code-defined role matrix** (`ROLE_TOOL_ACCESS`): `execute_python_code` + `query_and_analyze` restricted to `System Manager`; roles `Assistant User` / `Assistant Admin` exist for lower tiers.
- **Defense-in-depth field/doctype filters** (`security_config.py`): `SENSITIVE_FIELDS` (credentials → `***RESTRICTED***`), `ADMIN_ONLY_FIELDS` (hidden from Assistant Users), `RESTRICTED_DOCTYPES` (system doctypes blocked for Assistant Users), and restricted-field write rejection on create/update.
- **Audit log on every call** (`BaseTool._safe_execute` → `log_tool_execution`): `Assistant Audit Log` DocType captures tool, user, status, timing, target_doctype/target_name, input/output (truncated), traceback, client_id, session_id, ip — with credential-key redaction (`_is_sensitive_key`).

Verdict:
- **REUSE-IDEA** — real-user execution + `frappe.has_permission` enforcement + full audit log with redaction + admin-configurable per-tool role DocType. This is exactly the enforcement spine we want.
- **ADAPT** — the role tiers are close but NOT a minimally-scoped role: `Assistant User` still gets generic CRUD on everything its underlying Frappe user can touch. We need a **dedicated custom role scoped to a whitelist of doctypes + draft-only**, not "whatever the user can do."

## 4. Auth — how credentials are handled

- **OAuth 2.0 Bearer** (primary): validates Frappe `OAuth Bearer Token` (status Active + not expired) → maps to real user. Full OAuth discovery, dynamic client registration, `.well-known/oauth-protected-resource`, proper 401 + `WWW-Authenticate` challenges.
- **API key:secret** fallback for STDIO clients (`Authorization: token <key>:<secret>`, decrypted-secret compare).
- Per-user `assistant_enabled` flag gate on top of auth.
- Verdict: **REUSE-IDEA** — OAuth-token-as-real-user with a per-user enable flag is the right auth model; no static Administrator tokens.

## 5. Code quality / licence / maintenance

- Structure is reasonable (plugins, tool registry, `BaseTool`, audit, security_config). Tests present. Sandbox engineering is genuinely sophisticated (subprocess isolation, `RLIMIT_CPU`/`RLIMIT_AS`/`SIGALRM`, restricted `__builtins__` + restricted `__import__`, `ReadOnlyDatabase` proxy, JSON-over-stdin, semgrep `nosemgrep` annotations).
- **But the code-exec + SQL safety is security-by-blacklist** (regex keyword lists, dangerous-module deny-lists) — fundamentally bypassable, and the authors know it (that's why it's `System Manager`-only). Do not treat it as a safe primitive.
- **Licence = AGPL-3.0 (strong copyleft).** Copying FAC code into our product would impose AGPL obligations (network-use source disclosure). **Learn the patterns and reimplement clean; do not vendor or copy code verbatim.**

---

## SAFETY ANTI-PATTERNS — must NOT copy

1. **Raw SQL tool** (`run_database_query` → `frappe.db.sql`). Even "SELECT-only" it **bypasses Frappe row-level `permission_query_conditions`** and the guard is a regex blacklist. Violates our "no raw SQL" rule outright.
2. **Arbitrary Python tool** (`run_python_code` → `exec()`). Blacklist sandboxing of `exec` is bypassable; this is literally "arbitrary Python." Violates "no arbitrary Python / shell."
3. **Generic doc mutation over `doctype=*`** (`create/update/delete_document`). No domain scoping, no draft-only invariant. Our layer must be doctype-whitelisted and draft-only (`docstatus=0`).
4. **Auto-submit** — `create_document(submit=true)` and `submit_document`. Directly violates "never auto-submit."
5. **Force delete** — `delete_document(force=true)` bypasses link-integrity constraints.
6. **Scope = underlying user's full permissions**, not a minimal dedicated role. We need a purpose-built minimally-scoped custom role.
7. **No idempotency / provenance.** Import is single-doc; there is no batch id, source hash, parser version, or agent-identity stamping, and no idempotency key. We must add all of these ourselves — FAC offers nothing to reuse here.

## TOP REUSABLE IDEAS (adapt, reimplement under our licence)

1. Thin whitelisted MCP endpoint + typed `BaseTool` registry, built **per-request and per-user**.
2. Execute as the **real OAuth-authenticated user** (never Administrator) and enforce `frappe.has_permission` inside every tool.
3. **Audit-log every tool call** (target doctype/name, input/output, actor, ip/session, traceback) with credential redaction — via a base-class wrapper so no tool can skip it.
4. **Admin-configurable per-tool role access as a DocType** (enable/disable + role allow-list), layered on top of Frappe perms.
5. Field/doctype **allow/deny lists** (sensitive-field redaction, restricted-doctype blocking, restricted-field write rejection) as defense-in-depth.

---

### Bottom line

- **Architecture (2-3 lines):** Custom MCP-over-StreamableHTTP server behind one whitelisted Frappe endpoint; OAuth-Bearer (or api-key) auth maps each request to a **real Frappe user**; a plugin tool-registry exposes ~24 generic `BaseTool`s that call `frappe.has_permission` and are gated by a four-layer enable/role/permission stack and fully audit-logged. It also ships raw-SQL and arbitrary-Python tools (System-Manager-only, sandboxed).
- **Safety verdict:** **CAUTIONARY.** The permission-enforcement + OAuth-real-user + audit + tool-registry layers are *safe-to-learn-from* and genuinely good; the tool *surface* (raw SQL, arbitrary Python, generic mutation, auto-submit, force-delete) is *dangerous* and violates our hard requirements head-on. Mine the spine, discard the surface.
- **Top reusable ideas:** per-request/per-user typed tool registry; run-as-real-user + `has_permission` in every tool; base-class audit logging with redaction; admin-configurable per-tool role DocType; sensitive-field/doctype filters.
- **Top anti-patterns to avoid:** raw-SQL tool, arbitrary-Python tool, generic `doctype=*` create/update/delete, auto-submit, force-delete, permission scope = full user rights, and total absence of idempotency/provenance for batch import.
