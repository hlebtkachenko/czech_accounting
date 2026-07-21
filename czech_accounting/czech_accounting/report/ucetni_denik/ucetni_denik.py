# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Účetní deník — chronological journal (Act 563/1991 Sb., § 13).

The statutory chronological book: every accounting entry in time order with the § 13
content — evidenční (pořadové) číslo, datum uskutečnění účetního případu, účet MD/Dal,
částka, popis, and a reference to the source účetní doklad (drill-down to the voucher,
where its attachment lives).

It reads GL Entry directly (the single book of record — no second ledger, per the
ERPNext ledger-architecture KB) and reconciles by construction: total MD = total Dal.
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate

from .._common import finance_book_condition, require_company_and_to_date


def execute(filters=None):
    filters = frappe._dict(filters or {})
    require_company_and_to_date(filters)
    # No finance-book default here: the deník is a chronological listing of every entry, not
    # an aggregate, so it shows all books unless the user narrows to one.

    entries = _get_entries(filters)
    data = _build_rows(entries)
    return _columns(), data


def _columns():
    return [
        {"label": _("Evid. číslo"), "fieldname": "entry_no", "fieldtype": "Int", "width": 90},
        {"label": _("Datum"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Typ dokladu"), "fieldname": "voucher_type", "fieldtype": "Data", "width": 130},
        {"label": _("Číslo dokladu"), "fieldname": "voucher_no", "fieldtype": "Dynamic Link",
         "options": "voucher_type", "width": 170},
        {"label": _("Účet"), "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 220},
        {"label": _("Má dáti"), "fieldname": "debit", "fieldtype": "Currency", "width": 130},
        {"label": _("Dal"), "fieldname": "credit", "fieldtype": "Currency", "width": 130},
        {"label": _("Protiúčet"), "fieldname": "against", "fieldtype": "Data", "width": 160},
        {"label": _("Účastník"), "fieldname": "party", "fieldtype": "Data", "width": 140},
        {"label": _("Středisko"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 130},
        {"label": _("Projekt"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 130},
        {"label": _("Popis"), "fieldname": "remarks", "fieldtype": "Data", "width": 300},
    ]


def _get_entries(filters):
    conditions = [
        "gle.company = %(company)s",
        "gle.is_cancelled = 0",
        "gle.posting_date <= %(to_date)s",
    ]
    params = {"company": filters.company, "to_date": getdate(filters.to_date)}

    if filters.get("from_date"):
        conditions.append("gle.posting_date >= %(from_date)s")
        params["from_date"] = getdate(filters.from_date)
    fb = finance_book_condition(filters, params)
    if fb:
        conditions.append(fb)
    if filters.get("voucher_no"):
        conditions.append("gle.voucher_no = %(voucher_no)s")
        params["voucher_no"] = filters.voucher_no
    if filters.get("cost_center"):
        conditions.append("gle.cost_center = %(cost_center)s")
        params["cost_center"] = filters.cost_center
    if filters.get("project"):
        conditions.append("gle.project = %(project)s")
        params["project"] = filters.project

    return frappe.db.sql(
        """
        SELECT gle.posting_date, gle.voucher_type, gle.voucher_no, gle.account,
               gle.debit, gle.credit, gle.against, gle.party, gle.cost_center,
               gle.project, gle.remarks
        FROM `tabGL Entry` gle
        WHERE {conditions}
        ORDER BY gle.posting_date, gle.voucher_no, gle.creation
        """.format(conditions=" AND ".join(conditions)),
        params,
        as_dict=True,
    )


def _build_rows(entries):
    data = []
    total_debit = 0.0
    total_credit = 0.0
    for i, e in enumerate(entries, start=1):
        e["entry_no"] = i
        total_debit += flt(e.debit)
        total_credit += flt(e.credit)
        data.append(e)

    if data:
        # The label goes in the Data "Typ dokladu" column, not the Link "Účet" column: a label in
        # a Link cell renders as a clickable account that 404s (no such Account).
        data.append(
            {
                "voucher_type": _("Součet (MD = Dal)"),
                "debit": total_debit,
                "credit": total_credit,
                "entry_no": None,
            }
        )
    return data
