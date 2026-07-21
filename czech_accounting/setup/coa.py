"""Apply the versioned Czech chart of accounts to a company.

A company's chart is fixed at creation, so a Czech company is created on any chart and then
switched to the Czech one here, before it has any transactions. Reuses ERPNext's own reset
(unset_existing_data) and create_charts(custom_chart=...) so we do not fork core. The Czech
Account Category records the chart references ship as fixtures and are synced by migrate.
"""
import json

import frappe
from frappe import _
from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import create_charts
from erpnext.accounts.doctype.chart_of_accounts_importer.chart_of_accounts_importer import (
    set_default_accounts,
    unset_existing_data,
)

CHART_FILE = ("chart_of_accounts", "cz_coa.json")

# apply_czech_coa deletes and rebuilds the company's accounts, so it must only run on a company
# with no bookkeeping yet: not merely no posted GL entries, but no transactional documents at
# all, since drafts (docstatus=0) reference accounts without creating GL entries.
TRANSACTIONAL_DOCTYPES = (
    "GL Entry",
    "Journal Entry",
    "Payment Entry",
    "Sales Invoice",
    "Purchase Invoice",
    "Stock Entry",
    "Delivery Note",
    "Purchase Receipt",
)


def load_cz_chart():
    """Load the versioned Czech chart tree shipped with the app."""
    with open(frappe.get_app_path("czech_accounting", *CHART_FILE), encoding="utf-8") as f:
        return json.load(f)


@frappe.whitelist()
def apply_czech_coa(company):
    """Build the Czech chart of accounts on a brand-new, un-configured company.

    Destructive (deletes and rebuilds the company's accounts), so it is restricted to a System
    Manager with write access to the company and refuses to run once the company has any
    transactional documents.
    """
    frappe.only_for("Accounts Manager")
    if not isinstance(company, str) or not frappe.db.exists("Company", company):
        frappe.throw(_("Unknown company"))
    if not frappe.has_permission("Company", ptype="write", doc=company):
        raise frappe.PermissionError

    for doctype in TRANSACTIONAL_DOCTYPES:
        if frappe.db.count(doctype, {"company": company}):
            frappe.throw(
                _("Company {0} already has {1} records; refusing to rebuild its chart.").format(
                    company, doctype
                )
            )

    unset_existing_data(company)
    create_charts(company, custom_chart=load_cz_chart()["tree"])
    set_default_accounts(company)
    frappe.db.commit()

    return {"company": company, "accounts": frappe.db.count("Account", {"company": company})}
