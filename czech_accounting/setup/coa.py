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

# 548 Jiné provozní náklady — the Czech home for invoice rounding (zaokrouhlení na celé koruny).
# ERPNext needs a Round Off Account before it can post that rounding line, and its
# set_default_accounts cannot map one because the Czech chart has no account named "Round Off".
ROUND_OFF_ACCOUNT_NUMBER = "548"

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

    Destructive (deletes and rebuilds the company's accounts), so it is restricted to an
    Accounts Manager with write access to the company and refuses to run once the company has
    any transactional documents.
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
    set_round_off_account(company)
    frappe.db.commit()

    return {"company": company, "accounts": frappe.db.count("Account", {"company": company})}


def set_round_off_account(company):
    """Point the company's Round Off Account (and cost center) at 548 so rounded invoices post."""
    account = frappe.db.get_value(
        "Account",
        {"company": company, "account_number": ROUND_OFF_ACCOUNT_NUMBER, "is_group": 0},
        "name",
    )
    if not account:
        return
    frappe.db.set_value(
        "Company",
        company,
        {
            "round_off_account": account,
            "round_off_cost_center": frappe.get_cached_value("Company", company, "cost_center"),
        },
    )


@frappe.whitelist()
def provision_czech_company(company):
    """Go-live in one call: build the Czech chart, then the Czech VAT setup.

    Wraps apply_czech_coa (chart) and setup_company_vat (DPH/PDP templates, cash/bank payment
    modes, and removal of ERPNext's seeded default VAT templates). Run once on a brand-new
    company. The permission and no-transactions gate is enforced by apply_czech_coa.
    """
    from czech_accounting.setup.vat_templates import setup_company_vat

    result = apply_czech_coa(company)
    setup_company_vat(company)
    result["sales_tax_templates"] = frappe.db.count(
        "Sales Taxes and Charges Template", {"company": company}
    )
    return result
