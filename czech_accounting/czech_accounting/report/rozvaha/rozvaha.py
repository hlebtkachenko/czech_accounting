# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Rozvaha (balance sheet) — statutory 4-column filing layout.

Decree 500/2002 Sb., Příloha 1: Brutto / Korekce / Netto (běžné období) / Netto
(minulé období). The native v16 Financial Report Template renders one value per row per
period (its columns are periods), so it cannot produce the Brutto/Korekce split the Aktiva
side requires — hence this dedicated report (the "custom report row builder" scoped in the
Stream 3 plan).

The row tree is built at runtime from the live ``CZ-rozvaha-*`` Account Categories (the
Stream 1 seam, READ-ONLY here) so it stays in sync with Stream 1's taxonomy. It reads the
same GL the Trial Balance reads (no second ledger) and reconciles Aktiva = Pasiva by routing
the provisional period result into A.V and any unmapped account into a visible
"Nezařazené účty" row. Draft-for-accountant-signoff (repo domain invariant).
"""

import frappe
from frappe import _
from frappe.utils import add_years, flt, getdate

from .statement_lines import (
    DUAL_SIDE_ROUTING,
    RESULT_CATEGORY,
    ROZVAHA_PREFIX,
    UNMAPPED_ASSET,
    UNMAPPED_ASSET_LABEL,
    UNMAPPED_LIABILITY,
    UNMAPPED_LIABILITY_LABEL,
    category_side,
    category_sort_key,
    is_correction_account,
)

RECONCILE_TOLERANCE = 0.01
ZERO = 0.005


def execute(filters=None):
    filters = frappe._dict(filters or {})
    _validate(filters)

    to_date = getdate(filters.to_date)
    prev_to = getdate(filters.previous_to_date) if filters.get("previous_to_date") else add_years(to_date, -1)

    accounts = _accounts(filters.company)
    bal_cur = _balances(filters, to_date)
    bal_prev = _balances(filters, prev_to)

    cats = _categories()
    tree = _tree(cats)

    own, result_cur, result_prev = _classify(accounts, bal_cur, bal_prev, cats)
    # provisional / booked result of the period -> A.V (raw terms; presented as credit +)
    own.setdefault(RESULT_CATEGORY, _zero())
    own[RESULT_CATEGORY]["bc"] += result_cur
    own[RESULT_CATEGORY]["bp"] += result_prev

    displayed = _rollup(tree, own)
    return _columns(), _rows(filters, tree, cats, displayed, own)


def _validate(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is mandatory"))
    if not filters.get("to_date"):
        frappe.throw(_("To Date is mandatory"))


def _columns():
    return [
        {"label": _("Ukazatel"), "fieldname": "ukazatel", "fieldtype": "Data", "width": 460},
        {"label": _("Brutto"), "fieldname": "brutto", "fieldtype": "Currency", "width": 140},
        {"label": _("Korekce"), "fieldname": "korekce", "fieldtype": "Currency", "width": 140},
        {"label": _("Netto — běžné období"), "fieldname": "netto", "fieldtype": "Currency", "width": 155},
        {"label": _("Netto — minulé období"), "fieldname": "minule", "fieldtype": "Currency", "width": 155},
    ]


def _accounts(company):
    return frappe.db.get_all(
        "Account",
        filters={"company": company, "is_group": 0},
        fields=["name", "account_number", "account_category", "root_type"],
    )


def _balances(filters, date):
    conditions = ["gle.company = %(company)s", "gle.is_cancelled = 0", "gle.posting_date <= %(date)s"]
    params = {"company": filters.company, "date": date}
    if filters.get("finance_book"):
        conditions.append("(gle.finance_book = %(fb)s OR gle.finance_book IS NULL OR gle.finance_book = '')")
        params["fb"] = filters.finance_book
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


def _categories():
    rows = frappe.db.get_all(
        "Account Category",
        filters={"name": ["like", ROZVAHA_PREFIX + "%"]},
        fields=["name", "description"],
    )
    return {r.name: {"desc": r.description or r.name, "side": category_side(r.name)} for r in rows}


def _tree(cats):
    """Return {parent -> [children]} and {name -> parent} using longest-existing-prefix."""
    names = list(cats)
    seg = {n: n[len(ROZVAHA_PREFIX):].split("-") for n in names}
    by_side = {"A": set(), "P": set()}
    for n in names:
        by_side[cats[n]["side"]].add(n)

    parent = {}
    for n in names:
        best = None
        for cand in by_side[cats[n]["side"]]:
            if cand == n:
                continue
            cs = seg[cand]
            if len(cs) < len(seg[n]) and seg[n][: len(cs)] == cs:
                if best is None or len(cs) > len(seg[best]):
                    best = cand
        parent[n] = best

    children = {n: [] for n in names}
    roots = {"A": [], "P": []}
    for n in names:
        if parent[n] is None:
            roots[cats[n]["side"]].append(n)
        else:
            children[parent[n]].append(n)

    for n in names:
        children[n].sort(key=category_sort_key)
    roots["A"].sort(key=category_sort_key)
    roots["P"].sort(key=category_sort_key)
    return {"children": children, "roots": roots}


def _zero():
    return {"bc": 0.0, "kc": 0.0, "bp": 0.0, "kp": 0.0}


def _route(category, signed_balance):
    if category in DUAL_SIDE_ROUTING and signed_balance > 0:
        return DUAL_SIDE_ROUTING[category]
    return category


def _classify(accounts, bal_cur, bal_prev, cats):
    own = {}
    result_cur = 0.0
    result_prev = 0.0

    def bucket(cat):
        return own.setdefault(cat, _zero())

    for acc in accounts:
        b_cur = bal_cur.get(acc.name, 0.0)
        b_prev = bal_prev.get(acc.name, 0.0)
        if abs(b_cur) < ZERO and abs(b_prev) < ZERO:
            continue
        if acc.root_type in ("Income", "Expense"):
            result_cur += b_cur
            result_prev += b_prev
            continue

        category = acc.account_category
        cat_cur = _target(category, b_cur, cats)
        cat_prev = _target(category, b_prev, cats)
        corr = is_correction_account(acc.account_number)
        if corr:
            bucket(cat_cur)["kc"] += b_cur
            bucket(cat_prev)["kp"] += b_prev
        else:
            bucket(cat_cur)["bc"] += b_cur
            bucket(cat_prev)["bp"] += b_prev

    return own, result_cur, result_prev


def _target(category, signed_balance, cats):
    if not category:
        return UNMAPPED_ASSET if signed_balance > 0 else UNMAPPED_LIABILITY
    routed = _route(category, signed_balance)
    if routed not in cats:
        return UNMAPPED_ASSET if signed_balance > 0 else UNMAPPED_LIABILITY
    return routed


def _rollup(tree, own):
    """displayed[cat] = own[cat] + sum(displayed[child]) (post-order)."""
    displayed = {}

    def visit(n):
        agg = dict(own.get(n, _zero()))
        for ch in tree["children"].get(n, []):
            cv = visit(ch)
            for k in agg:
                agg[k] += cv[k]
        displayed[n] = agg
        return agg

    for side in ("A", "P"):
        for r in tree["roots"][side]:
            visit(r)
    return displayed


def _present(side, raw):
    factor = 1 if side == "A" else -1
    return {
        "brutto": raw["bc"] * factor,
        "korekce": raw["kc"] * factor,
        "netto": (raw["bc"] + raw["kc"]) * factor,
        "minule": (raw["bp"] + raw["kp"]) * factor,
    }


def _rows(filters, tree, cats, displayed, own):
    show_zero = int(filters.get("show_zero_rows") or 0)
    data = []

    for side, label, unmapped in (
        ("A", "AKTIVA CELKEM", (UNMAPPED_ASSET, UNMAPPED_ASSET_LABEL)),
        ("P", "PASIVA CELKEM", (UNMAPPED_LIABILITY, UNMAPPED_LIABILITY_LABEL)),
    ):
        total = _zero()
        for r in tree["roots"][side]:
            for k in total:
                total[k] += displayed[r][k]
        unmapped_raw = own.get(unmapped[0])
        if unmapped_raw:
            for k in total:
                total[k] += unmapped_raw[k]

        tp = _present(side, total)
        data.append(_row(label, tp, side, indent=0, group=True))

        for r in tree["roots"][side]:
            _emit(data, tree, cats, displayed, r, side, 1, show_zero)

        if unmapped_raw and (abs(unmapped_raw["bc"] + unmapped_raw["kc"]) > ZERO or abs(unmapped_raw["bp"] + unmapped_raw["kp"]) > ZERO):
            data.append(_row(unmapped[1], _present(side, unmapped_raw), side, indent=1, group=True))

    _reconcile(data)
    return data


def _emit(data, tree, cats, displayed, name, side, indent, show_zero):
    p = _present(side, displayed[name])
    kids = tree["children"].get(name, [])
    if not show_zero and abs(p["netto"]) < ZERO and abs(p["minule"]) < ZERO:
        return
    data.append(_row(cats[name]["desc"], p, side, indent=indent, group=bool(kids)))
    for ch in kids:
        _emit(data, tree, cats, displayed, ch, side, indent + 1, show_zero)


def _row(label, p, side, indent, group):
    show_bk = side == "A"
    return {
        "ukazatel": label,
        "brutto": p["brutto"] if show_bk else None,
        "korekce": p["korekce"] if show_bk else None,
        "netto": p["netto"],
        "minule": p["minule"],
        "indent": indent,
        "is_group": 1 if group else 0,
    }


def _reconcile(data):
    aktiva = next((r["netto"] for r in data if r["ukazatel"] == "AKTIVA CELKEM"), 0.0)
    pasiva = next((r["netto"] for r in data if r["ukazatel"] == "PASIVA CELKEM"), 0.0)
    diff = flt(aktiva) - flt(pasiva)
    if abs(diff) > RECONCILE_TOLERANCE:
        data.append({"ukazatel": "", "netto": None})
        data.append({"ukazatel": _("KONTROLA — Aktiva − Pasiva (musí být 0)"), "netto": diff, "indent": 0, "is_group": 1})
