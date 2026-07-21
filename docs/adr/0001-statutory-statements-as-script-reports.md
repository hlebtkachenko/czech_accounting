# 0001. Statutory Rozvaha and VZZ as Script Reports over the Account Category seam

- Status: Proposed
- Date: 2026-07-21
- Deciders: Hleb Tkachenko (Stream 3)

## Context

Stream 3 must deliver the statutory **Rozvaha** (Decree 500/2002 Sb., Příloha 1) and **VZZ
druhové** (Příloha 2) that reconcile to the trial balance. The plan pointed at the v16
`Financial Report Template` + `Account Category` mechanism, and explicitly flagged that the
4-column statutory Rozvaha (Brutto / Korekce / Netto / Minulé) "likely needs a Custom API /
custom report row builder — scope that."

Reading the v16 engine (`financial_report_engine.py`) confirmed the blocker: a
`Financial Report Template` renders **one value per row per period** — its columns are
periods (`get_period_list` / `get_columns` from `financial_statements`). It cannot render
the Brutto/Korekce/Netto columns that the Aktiva side of the statutory Rozvaha requires,
because those are not periods; they are a decomposition of a single period's balance. The
native template gives a management balance sheet, not the statutory filing layout.

Two further frictions with shipping the templates as fixtures:
- `FinancialReportTemplate.on_update` calls `export_module_json`, which in developer_mode
  writes the template back out as module files. Importing a Czech-named template
  (`Výkaz zisku a ztráty …`) would create diacritic/parenthesis module paths on the server
  tree — fragile, and on macOS the NFD/NFC path mismatch (global rule 15) makes such paths
  unreadable to local tooling.
- The bottom line of both statements (Aktiva = Pasiva; VZZ result = Rozvaha A.V) must be
  guaranteed to reconcile. That is far easier to prove in Python over the GL than to encode
  in the native engine's row-formula + reverse-sign semantics.

## Decision

Build the statutory **Rozvaha** and **VZZ druhové** as standard **Script Reports** over
`GL Entry`, classifying every posting account through its `account_category` — the Stream 1
seam, consumed READ-ONLY. The Rozvaha builds its row tree at runtime from the live
`CZ-rozvaha-*` categories; the VZZ uses an explicit Příloha-2 ordering of the `CZ-vzz-*`
categories. Do **not** ship a `Financial Report Template` fixture for these.

Reconciliation is guaranteed by construction: the provisional period result (`-Σ(debit −
credit)` over all class 5/6 accounts) is routed into Rozvaha row A.V, any unmapped account
is surfaced in a visible "Nezařazené účty" row, and Brutto/Korekce is split by
correction-account number prefix (07x/08x oprávky, 09x/19x/29x/39x opravné položky).

## Consequences

### Positive
- Renders the true 4-column statutory Rozvaha layout, which the native template cannot.
- Aktiva = Pasiva and VZZ *** = Rozvaha A.V hold by construction; covered by a test.
- Ascii report folders (`rozvaha`, `vzz_druhove`) — no unicode/auto-export module files.
- Still consumes the Account Category seam exactly as the contract intends; the report tree
  auto-tracks Stream 1's taxonomy.

### Negative (trade-offs)
- Two Script Reports are custom code to maintain, versus configuration in the native engine.
- The cheap "management balance sheet" the native template would give is not produced here;
  users who want it can use ERPNext's built-in Balance Sheet / Profit and Loss, or a
  `Financial Report Template` can be added later as a separate management view.
- Report labels shown in the UI list are ascii (`VZZ druhove`, `Ucetni denik`) because a
  standard report's folder is `frappe.scrub(report_name)`; the full Czech statutory names
  live in the report content and docs.

### Follow-up
- Accountant sign-off on both statement layouts before real filing use (repo invariant).
- Optional later: a `Financial Report Template` management view, and the Sbírka-listin
  structured export (PDF/XML) as a separate filing artifact.

## Alternatives considered

- **Native `Financial Report Template` only** — rejected: cannot render Brutto/Korekce
  columns; weaker reconciliation guarantee; diacritic auto-export paths.
- **Query Reports (SQL) as fixtures** — rejected for the statements: conditional filters and
  the provisional-result / dual-side routing are awkward in raw SQL; Script Reports are
  clearer and testable. (Query-report shape is fine for simple listings, but the deník and
  WIP are also Script Reports here for uniform filter handling.)

## See also

- `docs/plans/stream-3-books-assets.md` (Books section)
- `docs/plans/research/erpnext-modeling.md` (rows 6–8)
- `czech_accounting/czech_accounting/report/rozvaha/statement_lines.py` (the seam + layout)
