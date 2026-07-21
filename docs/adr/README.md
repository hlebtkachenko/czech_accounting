# Architecture Decision Records

Short, immutable records of decisions that shape the app. One decision per file, named
`NNNN-kebab-slug.md` (zero-padded, sequential). Once merged, an ADR is not rewritten; it is
superseded by a new one.

## Index

| # | Title | Status |
|---|---|---|
| _none yet_ | | |

## When to write an ADR

Write one when a choice is hard to reverse or will be questioned later: extending vs forking
a core behavior, a chart-of-accounts structure, a statement-mapping approach, a VAT-schema
version, an integration boundary, a permission model.

Do **not** write one for routine changes with no lasting trade-off.

## Status lifecycle

`Proposed` → `Accepted` → (`Superseded by NNNN` | `Deprecated`).

## Rules

- Use [`_TEMPLATE.md`](_TEMPLATE.md).
- Trade-offs are mandatory. An ADR with no Negative bullet is incomplete.
- Statutory decisions carry the effective date and the legal source.
