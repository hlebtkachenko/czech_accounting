# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Nedokončená výroba — developer WIP inventory (účet 121) by project / block / unit.

The build-to-sell flats are inventory, not fixed assets (LOCKED decision, 00-master.md §2):
construction costs accumulate in 121 Nedokončená výroba (method A) via Journal Entries
carrying a Project + Cost Center dimension, then the period-end change-in-state books
MD 121 / D 611. This report surfaces the 121 balance broken down by Project and Cost
Center (the block/unit analytics) so each development's WIP is auditable and feeds the
Rozvaha row C.I.2.

WIP accounts are identified through their ``account_category`` (AKT-C.I.2, the Stream 1
seam) with an account-number fallback (12x) for sites where categories are not yet
assigned.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate

WIP_CATEGORY = "AKT-C.I.2"


def execute(filters=None):
    filters = frappe._dict(filters or {})
    if not filters.get("company"):
        frappe.throw(_("Company is mandatory"))
    if not filters.get("to_date"):
        frappe.throw(_("To Date is mandatory"))

    accounts = _wip_accounts(filters.company)
    if not accounts:
        return _columns(), []

    rows = _balances(filters, accounts)
    return _columns(), _build_rows(rows)


def _columns():
    return [
        {"label": _("Projekt"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 200},
        {"label": _("Středisko"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 200},
        {"label": _("Účet"), "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 240},
        {"label": _("Zůstatek NV"), "fieldname": "balance", "fieldtype": "Currency", "width": 160},
    ]


def _wip_accounts(company):
    return frappe.db.sql(
        """
        SELECT name FROM `tabAccount`
        WHERE company = %(company)s AND is_group = 0
          AND (account_category = %(cat)s OR account_number LIKE '121%%' OR account_number LIKE '122%%')
        """,
        {"company": company, "cat": WIP_CATEGORY},
        pluck=True,
    )


def _balances(filters, accounts):
    conditions = [
        "gle.company = %(company)s",
        "gle.is_cancelled = 0",
        "gle.posting_date <= %(to_date)s",
        "gle.account IN %(accounts)s",
    ]
    params = {"company": filters.company, "to_date": getdate(filters.to_date), "accounts": tuple(accounts)}
    if filters.get("project"):
        conditions.append("gle.project = %(project)s")
        params["project"] = filters.project
    if filters.get("finance_book"):
        conditions.append("(gle.finance_book = %(fb)s OR gle.finance_book IS NULL OR gle.finance_book = '')")
        params["fb"] = filters.finance_book

    return frappe.db.sql(
        """
        SELECT gle.project AS project, gle.cost_center AS cost_center, gle.account AS account,
               SUM(gle.debit - gle.credit) AS balance
        FROM `tabGL Entry` gle
        WHERE {conditions}
        GROUP BY gle.project, gle.cost_center, gle.account
        HAVING ABS(SUM(gle.debit - gle.credit)) > 0.005
        ORDER BY gle.project, gle.cost_center, gle.account
        """.format(conditions=" AND ".join(conditions)),
        params,
        as_dict=True,
    )


def _build_rows(rows):
    data = []
    total = 0.0
    for r in rows:
        r["balance"] = flt(r.balance)
        total += r["balance"]
        data.append(r)
    if data:
        data.append({"account": _("Celkem nedokončená výroba"), "balance": total})
    return data
