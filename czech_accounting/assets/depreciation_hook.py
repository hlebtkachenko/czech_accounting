"""Czech tax depreciation for the CZ-Daňové odpisy Finance Book.

ERPNext builds a straight-line schedule for every finance book. For the Czech tax book we
replace it with the statutory § 31 / § 32 amounts. Daňové odpisy are a parallel tax calculation
(feeding the tax return and deferred tax via 592/481), distinct from účetní odpisy which the
CZ-Účetní odpisy book posts to 551/08x. Whether ERPNext posts the tax book to the GL is left to
ERPNext's per-book behaviour; confirm before running live depreciation.
"""
import frappe
from frappe.utils import add_years, getdate

from czech_accounting.assets.tax_depreciation import tax_depreciation_schedule

TAX_FINANCE_BOOK = "CZ-Daňové odpisy"
METHOD_BY_LABEL = {"Rovnoměrné (§ 31)": "linear", "Zrychlené (§ 32)": "accelerated"}


def set_czech_tax_schedule(doc, method=None):
    """validate hook on Asset Depreciation Schedule: impose the statutory tax schedule."""
    if doc.finance_book != TAX_FINANCE_BOOK:
        return
    asset = frappe.get_doc("Asset", doc.asset)
    category = frappe.db.get_value(
        "Asset Category", asset.asset_category, ["cz_tax_group", "cz_tax_method"], as_dict=True
    )
    if not category or not category.get("cz_tax_group"):
        return  # category not configured for statutory tax depreciation; leave ERPNext's schedule

    group = int(category.cz_tax_group)
    tax_method = METHOD_BY_LABEL.get(category.get("cz_tax_method"), "linear")
    amounts = tax_depreciation_schedule(asset.gross_purchase_amount, group, tax_method)

    base_date = (
        getdate(doc.depreciation_schedule[0].schedule_date)
        if doc.depreciation_schedule
        else getdate(asset.available_for_use_date)
    )
    doc.depreciation_schedule = []
    accumulated = 0.0
    for year, amount in enumerate(amounts):
        accumulated += amount
        doc.append(
            "depreciation_schedule",
            {
                "schedule_date": add_years(base_date, year),
                "depreciation_amount": amount,
                "accumulated_depreciation_amount": accumulated,
            },
        )
    doc.total_number_of_depreciations = len(amounts)
