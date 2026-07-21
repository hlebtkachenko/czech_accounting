# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Výkaz zisku a ztráty — druhové členění (by-nature P&L).

Decree 500/2002 Sb., Příloha 2. Two columns: běžné období / minulé období. Class 5 (náklady)
and class 6 (výnosy) accounts are classified through their ``account_category`` (the Stream 1
seam, READ-ONLY here).

The bottom line "*** Výsledek hospodaření za účetní období" is computed directly from the GL as
``-sum(debit - credit)`` over every class 5/6 account, so it always reconciles to Rozvaha row
A.V (which uses the same fiscal-year movement basis). Any class 5/6 account whose category is
not laid out here surfaces in a visible "Nezařazené" row. Draft-for-accountant-signoff.
"""

import frappe
from frappe import _
from frappe.utils import add_years, getdate

from .._common import account_movements, fiscal_year_start, require_company_and_to_date, resolve_finance_book
from ..rozvaha.statement_lines import VZZ_LAYOUT

UNMAPPED_PL = "__unmapped_pl__"
UNMAPPED_LABEL = "Nezařazené náklady a výnosy"

LEAF_BY_CATEGORY = {row["category"]: row for row in VZZ_LAYOUT if row["kind"] == "L" and row.get("category")}
ROW_BY_CODE = {row["code"]: row for row in VZZ_LAYOUT}


def execute(filters=None):
    filters = frappe._dict(filters or {})
    require_company_and_to_date(filters)
    resolve_finance_book(filters)

    to_date = getdate(filters.to_date)
    from_date = getdate(filters.from_date) if filters.get("from_date") else fiscal_year_start(filters.company, to_date)
    prev_to = getdate(filters.previous_to_date) if filters.get("previous_to_date") else add_years(to_date, -1)
    prev_from = add_years(from_date, -1)

    accounts = _pl_accounts(filters.company)
    names = [a.name for a in accounts]
    move_cur = account_movements(filters, from_date, to_date, names)
    move_prev = account_movements(filters, prev_from, prev_to, names)

    return _columns(), _build_rows(accounts, move_cur, move_prev)


def _columns():
    return [
        {"label": _("Ukazatel"), "fieldname": "ukazatel", "fieldtype": "Data", "width": 480},
        {"label": _("Běžné období"), "fieldname": "current", "fieldtype": "Currency", "width": 170},
        {"label": _("Minulé období"), "fieldname": "previous", "fieldtype": "Currency", "width": 170},
    ]


def _pl_accounts(company):
    return frappe.db.get_all(
        "Account",
        filters={"company": company, "is_group": 0, "root_type": ["in", ["Income", "Expense"]]},
        fields=["name", "account_category"],
    )


def _expand_to_leaves(members):
    out = []
    for code in members:
        row = ROW_BY_CODE[code]
        if row["kind"] == "L":
            out.append(code)
        else:
            out.extend(_expand_to_leaves(row["members"]))
    return out


def _build_rows(accounts, move_cur, move_prev):
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
    present = {}
    contrib = {}
    for row in VZZ_LAYOUT:
        if row["kind"] != "L":
            continue
        c = cat.get(row["category"], {"b_cur": 0.0, "b_prev": 0.0})
        b_cur, b_prev = c["b_cur"], c["b_prev"]
        sign = -1 if row["nature"] == "revenue" else 1
        present[row["code"]] = (b_cur * sign, b_prev * sign)
        contrib[row["code"]] = (-b_cur, -b_prev)

    for row in VZZ_LAYOUT:
        if row["kind"] == "S":
            lv = _expand_to_leaves(row["members"])
            present[row["code"]] = (
                sum(present.get(x, (0, 0))[0] for x in lv),
                sum(present.get(x, (0, 0))[1] for x in lv),
            )

    data = []
    for row in VZZ_LAYOUT:
        if row["kind"] in ("L", "S"):
            cur, prev = present.get(row["code"], (0.0, 0.0))
        elif row["kind"] == "R":
            lv = _expand_to_leaves(row["members"])
            cur = sum(contrib.get(x, (0, 0))[0] for x in lv)
            prev = sum(contrib.get(x, (0, 0))[1] for x in lv)
        else:  # "T" — computed straight from GL so it always reconciles to Rozvaha A.V
            cur, prev = -total_cur, -total_prev
        data.append({
            "ukazatel": row["label"],
            "current": cur,
            "previous": prev,
            "indent": row["indent"],
            "is_group": 1 if row["kind"] in ("S", "R", "T") else 0,
        })

    _append_unmapped(cat, data)
    return data


def _append_unmapped(cat, data):
    u = cat.get(UNMAPPED_PL)
    if u and (abs(u["b_cur"]) > 0.01 or abs(u["b_prev"]) > 0.01):
        data.append({
            "ukazatel": _(UNMAPPED_LABEL),
            "current": u["b_cur"],
            "previous": u["b_prev"],
            "indent": 0,
            "is_group": 1,
        })
