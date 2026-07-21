"""Czech tax depreciation on the CZ-Daňové odpisy Finance Book.

ERPNext builds a straight-line schedule for every finance book, and rebuilds it through the
asset lifecycle, so a doc-event hook cannot reliably win the race. Instead we subclass Asset
Depreciation Schedule (via override_doctype_class) and, once ERPNext has finished submitting the
schedule, rewrite the tax book's rows with the statutory § 31/§ 32 amounts.

Daňové odpisy are a parallel tax calculation (feeding the tax return and deferred tax via
592/481), distinct from účetní odpisy which the CZ-Účetní odpisy book posts to 551/08x.
"""
import frappe
from frappe.utils import add_years, getdate

from czech_accounting.assets.tax_depreciation import tax_depreciation_schedule
from erpnext.assets.doctype.asset_depreciation_schedule.asset_depreciation_schedule import (
    AssetDepreciationSchedule,
)

TAX_FINANCE_BOOK = "CZ-Daňové odpisy"
METHOD_BY_LABEL = {"Rovnoměrné (§ 31)": "linear", "Zrychlené (§ 32)": "accelerated"}


class CzechAssetDepreciationSchedule(AssetDepreciationSchedule):
    def on_submit(self):
        super().on_submit()
        apply_statutory_tax_schedule(self)


def apply_statutory_tax_schedule(doc):
    """Replace the active tax schedule's rows with the statutory § 31/§ 32 amounts."""
    if doc.finance_book != TAX_FINANCE_BOOK:
        return
    asset = frappe.db.get_value(
        "Asset", doc.asset, ["asset_category", "gross_purchase_amount", "available_for_use_date"],
        as_dict=True,
    )
    category = frappe.db.get_value(
        "Asset Category", asset.asset_category, ["cz_tax_group", "cz_tax_method"], as_dict=True
    )
    if not category or not category.get("cz_tax_group"):
        return

    group = int(category.cz_tax_group)
    method = METHOD_BY_LABEL.get(category.get("cz_tax_method"), "linear")
    amounts = tax_depreciation_schedule(asset.gross_purchase_amount, group, method)

    first_date = frappe.db.get_value(
        "Depreciation Schedule", {"parent": doc.name}, "schedule_date", order_by="idx asc"
    )
    base_date = getdate(first_date) if first_date else getdate(asset.available_for_use_date)

    frappe.db.delete("Depreciation Schedule", {"parent": doc.name})
    accumulated = 0.0
    for index, amount in enumerate(amounts):
        accumulated += amount
        row = frappe.new_doc("Depreciation Schedule")
        row.update({
            "parent": doc.name,
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
        "Asset Depreciation Schedule", doc.name,
        "total_number_of_depreciations", len(amounts), update_modified=False,
    )
