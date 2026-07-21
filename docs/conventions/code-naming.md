# Naming

## Python / Frappe

| Thing | Convention | Example |
|---|---|---|
| Module / file | `snake_case.py` | `vat_return.py` |
| Package / directory | `snake_case` | `czech_accounting/report/` |
| Class | `PascalCase` | `class VATReturn(Document)` |
| Function / method / variable | `snake_case` | `def build_dphdp3(...)` |
| Constant | `UPPER_SNAKE_CASE` | `REDUCED_VAT_RATE` |
| DocType name | Title Case words | `VAT Return`, `Czech CoA Mapping` |
| DocType fieldname | `snake_case` | `taxable_supply_date` |
| DB table / column | `snake_case` (Frappe derives these) | `tab...`, `variable_symbol` |

Do not invent abbreviations. Spell it out: `variable_symbol`, not `var_sym`.

## Imports

Group and order, blank line between groups:

1. Standard library.
2. Third party, including `frappe` and `erpnext`.
3. Local `czech_accounting` modules.

Prefer explicit named imports over wildcard. No unused imports.

## Effective-dated artifacts

When a fixture or mapping is versioned by effective date, put the date in the name or a
clearly labelled field so the active version is unambiguous, e.g.
`vat_rates_2024_01_01.json`. Never overwrite a past-dated rule in place.
