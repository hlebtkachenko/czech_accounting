# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Nezařazené účty — posting accounts with no Czech statement Account Category.

Every posting account should map to a Rozvaha/VZZ row via a CZ- Account Category, or the
statements silently drop it into "Nezařazené účty". This report lists the accounts that need a
category, so chart drift is caught before it corrupts a statement.
"""
import frappe


def execute(filters=None):
    filters = filters or {}
    conditions = {"is_group": 0, "disabled": 0}
    if filters.get("company"):
        conditions["company"] = filters["company"]

    accounts = frappe.get_all(
        "Account",
        filters=conditions,
        fields=["name", "account_number", "account_name", "company", "account_category"],
        order_by="account_number",
    )
    data = [a for a in accounts if not (a.account_category or "").startswith("CZ-")]

    columns = [
        {"label": "Účet", "fieldname": "name", "fieldtype": "Link", "options": "Account", "width": 320},
        {"label": "Číslo", "fieldname": "account_number", "fieldtype": "Data", "width": 100},
        {"label": "Název", "fieldname": "account_name", "fieldtype": "Data", "width": 260},
        {"label": "Společnost", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 200},
    ]
    return columns, data
