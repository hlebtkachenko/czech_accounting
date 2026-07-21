# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Výkaz zisku a ztráty — druhové členění (by-nature P&L).

Decree 500/2002 Sb., Příloha 2. Two columns: běžné období / minulé období. Class 5
(náklady) and class 6 (výnosy) accounts are classified through their ``account_category``
(the Stream 1 seam, READ-ONLY here).

The bottom line "*** Výsledek hospodaření za účetní období" is computed directly from the
GL as ``-sum(debit - credit)`` over every class 5/6 account, so it always reconciles to
Rozvaha row A.V regardless of how intermediate rows present their sign. Any class 5/6
account whose category is not laid out here surfaces in a visible "Nezařazené" row.

Draft-for-accountant-signoff (repo domain invariant).
"""

import frappe
from frappe import _
from frappe.utils import add_years, flt, getdate

from ..rozvaha.statement_lines import VZZ_LAYOUT

UNMAPPED_PL = "__unmapped_pl__"
UNMAPPED_LABEL = "Nezařazené náklady a výnosy"

LEAF_BY_CATEGORY = {row["category"]: row for row in VZZ_LAYOUT if row["kind"] == "L" and row.get("category")}


def execute(filters=None):
    filters = frappe._dict(filters or {})
    if not filters.get("company"):
        frappe.throw(_("Company is mandatory"))
    if not filters.get("to_date"):
        frappe.throw(_("To Date is mandatory"))

    to_date = getdate(filters.to_date)
    from_date = getdate(filters.from_date) if filters.get("from_date") else _fy_start(filters.company, to_date)
    prev_to = getdate(filters.previous_to_date) if filters.get("previous_to_date") else add_years(to_date, -1)
    prev_from = add_years(from_date, -1)

    accounts = _pl_accounts(filters.company)
    move_cur = _movements(filters, accounts, from_date, to_date)
    move_prev = _movements(filters, accounts, prev_from, prev_to)

    rows = _build_rows(accounts, move_cur, move_prev)
    return _columns(), rows


def _columns():
    return [
        {"label": _("Ukazatel"), "fieldname": "ukazatel", "fieldtype": "Data", "width": 480},
        {"label": _("Běžné období"), "fieldname": "current", "fieldtype": "Currency", "width": 170},
        {"label": _("Minulé období"), "fieldname": "previous", "fieldtype": "Currency", "width": 170},
    ]


def _fy_start(company, date):
    fy = frappe.db.sql(
        """
        SELECT year_start_date FROM `tabFiscal Year` fy
        INNER JOIN `tabFiscal Year Company` fyc ON fyc.parent = fy.name
        WHERE fyc.company = %(company)s AND %(date)s BETWEEN fy.year_start_date AND fy.year_end_date
        ORDER BY fy.year_start_date DESC LIMIT 1
        """,
        {"company": company, "date": date},
    )
    if fy:
        return getdate(fy[0][0])
    return getdate(date).replace(month=1, day=1)


def _pl_accounts(company):
    return frappe.db.get_all(
        "Account",
        filters={"company": company, "is_group": 0, "root_type": ["in", ["Income", "Expense"]]},
        fields=["name", "account_category"],
    )


def _movements(filters, accounts, from_date, to_date):
    """Period movement (debit - credit) per class 5/6 account within [from, to]."""
    if not accounts:
        return {}
    conditions = [
        "gle.company = %(company)s",
        "gle.is_cancelled = 0",
        "gle.posting_date >= %(from_date)s",
        "gle.posting_date <= %(to_date)s",
        "gle.is_opening = 'No'",
    ]
    params = {"company": filters.company, "from_date": from_date, "to_date": to_date}
    if filters.get("finance_book"):
        conditions.append("(gle.finance_book = %(fb)s OR gle.finance_book IS NULL OR gle.finance_book = '')")
        params["fb"] = filters.finance_book

    rows = frappe.db.sql(
        """
        SELECT gle.account AS account, SUM(gle.debit - gle.credit) AS mv
        FROM `tabGL Entry` gle
        WHERE {conditions}
        GROUP BY gle.account
        """.format(conditions=" AND ".join(conditions)),
        params,
        as_dict=True,
    )
    return {r.account: flt(r.mv) for r in rows}


def _build_rows(accounts, move_cur, move_prev):
    # category -> {b_cur, b_prev}
    cat = {}
    total_cur = 0.0
    total_prev = 0.0
    for acc in accounts:
        b_cur = move_cur.get(acc.name, 0.0)
        b_prev = move_prev.get(acc.name, 0.0)
        total_cur += b_cur
        total_prev += b_prev
        category = acc.account_category if acc.account_category in LEAF_BY_CATEGORY else UNMAPPED_PL
        c = cat.setdefault(category, {"b_cur": 0.0, "b_prev": 0.0})
        c["b_cur"] += b_cur
        c["b_prev"] += b_prev

    # present (display magnitude) and contribution (-b, contribution to profit) per leaf code
    present = {}   # code -> (cur, prev)
    contrib = {}   # code -> (cur, prev)
    leaf_codes = []
    for row in VZZ_LAYOUT:
        if row["kind"] != "L":
            continue
        c = cat.get(row["category"], {"b_cur": 0.0, "b_prev": 0.0})
        b_cur, b_prev = c["b_cur"], c["b_prev"]
        sign = -1 if row["nature"] == "revenue" else 1
        present[row["code"]] = (b_cur * sign, b_prev * sign)
        contrib[row["code"]] = (-b_cur, -b_prev)
        leaf_codes.append(row["code"])

    # subtotals present = sum of child-leaf present values
    def leaves_of(code, seen=None):
        seen = seen or set()
        row = _row(code)
        if row["kind"] == "L":
            return [code]
        out = []
        for m in row["members"]:
            out.extend(leaves_of(m, seen))
        return out

    for row in VZZ_LAYOUT:
        if row["kind"] == "S":
            lv = leaves_of(row["code"])
            present[row["code"]] = (
                sum(present.get(x, (0, 0))[0] for x in lv),
                sum(present.get(x, (0, 0))[1] for x in lv),
            )

    data = []
    for row in VZZ_LAYOUT:
        if row["kind"] in ("L", "S"):
            cur, prev = present.get(row["code"], (0.0, 0.0))
        elif row["kind"] == "R":
            lv = _expand_result_members(row["members"])
            cur = sum(contrib.get(x, (0, 0))[0] for x in lv)
            prev = sum(contrib.get(x, (0, 0))[1] for x in lv)
        else:  # "T" — total, computed straight from GL so it always reconciles to A.V
            cur, prev = -total_cur, -total_prev
        data.append(
            {
                "ukazatel": row["label"],
                "current": cur,
                "previous": prev,
                "indent": row["indent"],
                "is_group": 1 if row["kind"] in ("S", "R", "T") else 0,
            }
        )

    _append_unmapped(cat, data)
    return data


def _row(code):
    for row in VZZ_LAYOUT:
        if row["code"] == code:
            return row
    raise KeyError(code)


def _expand_result_members(members):
    out = []
    for code in members:
        row = _row(code)
        if row["kind"] == "L":
            out.append(code)
        else:
            out.extend(_expand_result_members(row["members"]))
    return out


def _append_unmapped(cat, data):
    u = cat.get(UNMAPPED_PL)
    if u and (abs(u["b_cur"]) > 0.01 or abs(u["b_prev"]) > 0.01):
        data.append(
            {
                "ukazatel": _(UNMAPPED_LABEL),
                "current": u["b_cur"],
                "previous": u["b_prev"],
                "indent": 0,
                "is_group": 1,
            }
        )
