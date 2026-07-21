# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Shared GL access for the Czech statutory reports.

All statutory books read the same `GL Entry` (no second ledger). This module centralises
the pieces every report repeats: mandatory-filter validation, the Finance Book scope, and
the two GL aggregations (cumulative balance for the balance sheet, period movement for the
profit-and-loss and the period result).

Finance Book scope: when the user does not pick one, fall back to the Company's
``default_finance_book`` (mirrors ERPNext's General Ledger report). This keeps the statutory
statements on the accounting book (Účetní odpisy) instead of silently summing the účetní and
daňové depreciation books together.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate


def require_company_and_to_date(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is mandatory"))
    if not filters.get("to_date"):
        frappe.throw(_("To Date is mandatory"))


def resolve_finance_book(filters):
    """Default an unset Finance Book to the Company's default (accounting) book."""
    if not filters.get("finance_book"):
        filters.finance_book = frappe.get_cached_value("Company", filters.company, "default_finance_book")


def finance_book_condition(filters, params):
    """Return the SQL predicate for the selected book (plus book-agnostic postings), or None."""
    if filters.get("finance_book"):
        params["fb"] = filters.finance_book
        return "(gle.finance_book = %(fb)s OR gle.finance_book IS NULL OR gle.finance_book = '')"
    return None


def fiscal_year_start(company, date):
    fy = frappe.db.sql(
        """
        SELECT year_start_date FROM `tabFiscal Year` fy
        INNER JOIN `tabFiscal Year Company` fyc ON fyc.parent = fy.name
        WHERE fyc.company = %(company)s AND %(date)s BETWEEN fy.year_start_date AND fy.year_end_date
        ORDER BY fy.year_start_date DESC LIMIT 1
        """,
        {"company": company, "date": getdate(date)},
    )
    if fy:
        return getdate(fy[0][0])
    return getdate(date).replace(month=1, day=1)


def account_balances(filters, to_date, account_names=None):
    """Cumulative signed balance (debit - credit) per account as of ``to_date``."""
    conditions = ["gle.company = %(company)s", "gle.is_cancelled = 0", "gle.posting_date <= %(to_date)s"]
    params = {"company": filters.company, "to_date": getdate(to_date)}
    _apply(conditions, params, filters, account_names)
    return _run(conditions, params)


def account_movements(filters, from_date, to_date, account_names=None):
    """Period movement (debit - credit) per account within [from_date, to_date], excluding
    opening entries (the basis for the P&L and the period result)."""
    conditions = [
        "gle.company = %(company)s",
        "gle.is_cancelled = 0",
        "gle.is_opening = 'No'",
        "gle.posting_date >= %(from_date)s",
        "gle.posting_date <= %(to_date)s",
    ]
    params = {"company": filters.company, "from_date": getdate(from_date), "to_date": getdate(to_date)}
    _apply(conditions, params, filters, account_names)
    return _run(conditions, params)


def _apply(conditions, params, filters, account_names):
    fb = finance_book_condition(filters, params)
    if fb:
        conditions.append(fb)
    if account_names is not None:
        params["accounts"] = tuple(account_names) or ("",)
        conditions.append("gle.account IN %(accounts)s")


def _run(conditions, params):
    rows = frappe.db.sql(
        """
        SELECT gle.account AS account, SUM(gle.debit - gle.credit) AS bal
        FROM `tabGL Entry` gle
        WHERE {c}
        GROUP BY gle.account
        """.format(c=" AND ".join(conditions)),
        params,
        as_dict=True,
    )
    return {r.account: flt(r.bal) for r in rows}
