"""Czech tax depreciation for the CZ-Daňové odpisy Finance Book.

ERPNext builds a straight-line schedule for every finance book. After an Asset is submitted we
overwrite the CZ-Daňové odpisy schedule with the statutory § 31 / § 32 amounts. Daňové odpisy
are a parallel tax calculation (feeding the tax return and deferred tax via 592/481), distinct
from účetní odpisy which the CZ-Účetní odpisy book posts to 551/08x.

The rewrite is done directly on the schedule's child rows (the parent Asset Depreciation
Schedule is already submitted), which sidesteps ERPNext rebuilding a straight line during the
document lifecycle.
"""
import frappe
from frappe.utils import add_years, getdate

from czech_accounting.assets.tax_depreciation import tax_depreciation_schedule

TAX_FINANCE_BOOK = "CZ-Daňové odpisy"
METHOD_BY_LABEL = {"Rovnoměrné (§ 31)": "linear", "Zrychlené (§ 32)": "accelerated"}


def apply_czech_tax_depreciation(asset, method=None):
    """on_submit hook on Asset: put statutory § 31/§ 32 amounts on the tax book schedule."""
    category = frappe.db.get_value(
        "Asset Category", asset.asset_category, ["cz_tax_group", "cz_tax_method"], as_dict=True
    )
    if not category or not category.get("cz_tax_group"):
        return  # category not configured for statutory tax depreciation

    ads_name = frappe.db.get_value(
        "Asset Depreciation Schedule",
        {"asset": asset.name, "finance_book": TAX_FINANCE_BOOK, "docstatus": ["<", 2]},
        "name",
    )
    if not ads_name:
        return

    group = int(category.cz_tax_group)
    tax_method = METHOD_BY_LABEL.get(category.get("cz_tax_method"), "linear")
    amounts = tax_depreciation_schedule(asset.gross_purchase_amount, group, tax_method)

    first_date = frappe.db.get_value(
        "Depreciation Schedule", {"parent": ads_name}, "schedule_date", order_by="idx asc"
    )
    base_date = getdate(first_date) if first_date else getdate(asset.available_for_use_date)

    frappe.db.delete("Depreciation Schedule", {"parent": ads_name})
    accumulated = 0.0
    for index, amount in enumerate(amounts):
        accumulated += amount
        row = frappe.new_doc("Depreciation Schedule")
        row.update({
            "parent": ads_name,
            "parenttype": "Asset Depreciation Schedule",
            "parentfield": "depreciation_schedule",
            "idx": index + 1,
            "schedule_date": add_years(base_date, index),
            "depreciation_amount": amount,
            "accumulated_depreciation_amount": accumulated,
        })
        row.docstatus = 1
        row.db_insert()

    frappe.db.set_value(
        "Asset Depreciation Schedule", ads_name,
        "total_number_of_depreciations", len(amounts), update_modified=False,
    )
