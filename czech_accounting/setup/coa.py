"""Apply the versioned Czech chart of accounts to a company.

A company's chart is fixed at creation, so a Czech company is created on any chart and then
switched to the Czech one here, before it has any transactions. Reuses ERPNext's own reset
(unset_existing_data) and create_charts(custom_chart=...) so we do not fork core.
"""
import json

import frappe
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import create_charts
from erpnext.accounts.doctype.chart_of_accounts_importer.chart_of_accounts_importer import (
    set_default_accounts,
    unset_existing_data,
)

CHART_FILE = ("chart_of_accounts", "cz_coa.json")


def load_cz_chart():
    """Load the versioned Czech chart tree shipped with the app."""
    with open(frappe.get_app_path("czech_accounting", *CHART_FILE), encoding="utf-8") as f:
        return json.load(f)


def ensure_account_categories(tree):
    """Create every Account Category the tree references but the site does not have yet."""
    created = []

    def walk(node, parent_root):
        for _key, child in node.items():
            if not isinstance(child, dict):
                continue
            root_type = child.get("root_type") or parent_root
            category = child.get("account_category")
            if category and not frappe.db.exists("Account Category", category):
                frappe.get_doc(
                    {
                        "doctype": "Account Category",
                        "account_category_name": category,
                        "root_type": root_type,
                    }
                ).insert(ignore_permissions=True)
                created.append(category)
            walk(child, root_type)

    walk(tree, None)
    return created


@frappe.whitelist()
def apply_czech_coa(company):
    """Build the Czech chart of accounts on a zero-transaction company.

    Refuses to run once the company has GL entries.
    """
    if frappe.db.count("GL Entry", {"company": company}):
        frappe.throw(f"Company {company} already has GL entries; refusing to rebuild its chart.")

    chart = load_cz_chart()
    ensure_account_categories(chart["tree"])
    unset_existing_data(company)
    create_charts(company, custom_chart=chart["tree"])
    set_default_accounts(company)
    frappe.db.commit()

    return {"company": company, "accounts": frappe.db.count("Account", {"company": company})}
