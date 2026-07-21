# Commit convention

[Conventional Commits](https://www.conventionalcommits.org/). One logical change per commit.

## Format

```
<type>(<optional scope>): <subject>

<optional body — the why, not the what>

<optional footer — BREAKING CHANGE:, issue links>
```

Subject: imperative, lower-case, no trailing period, aim for <= 72 chars.

## Types

| Type | When |
|---|---|
| `feat` | New behavior (a DocType, report, field, mapping, export) |
| `fix` | Corrects wrong behavior |
| `docs` | Documentation only |
| `refactor` | Restructure without behavior change |
| `test` | Add or change tests only |
| `chore` | Tooling, deps, config, housekeeping |

Scope is optional and names the area, e.g. `feat(coa):`, `fix(vat):`, `feat(reports):`.

## Body

Explain the reasoning and any statutory basis (law + effective date) when relevant. The
diff already shows what changed; the body says why.

## Footer

- `BREAKING CHANGE: <what and how to migrate>` for incompatible changes.
- Link issues with `Closes #12` / `Refs #12`.

## Examples

Good:
```
feat(coa): add Czech chart of accounts template (Annex 4, Decree 500/2002)

Classes 0-7 with synthetic accounts, root/account types, and statement-row
mapping. Selectable at Company creation. Effective from 2026-01-01.
```

Bad:
```
update stuff
```
