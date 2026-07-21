"""Czech tax depreciation (daňové odpisy) on the CZ-Daňové odpisy Finance Book.

ERPNext builds and repeatedly rebuilds a straight-line schedule through the asset submit
lifecycle, so it must be corrected *after* ERPNext has finished. `apply_czech_tax_depreciation`
rewrites the active tax schedule with the statutory § 31/§ 32 amounts; the Asset on_submit hook
runs it after the transaction commits. It is idempotent, so re-running is safe.

Daňové odpisy are a parallel tax calculation (feeding the tax return and deferred tax via
592/481), distinct from účetní odpisy which the CZ-Účetní odpisy book posts to 551/08x.
"""
import frappe
from frappe.utils import add_years, getdate

from czech_accounting.assets.tax_depreciation import tax_depreciation_schedule

TAX_FINANCE_BOOK = "CZ-Daňové odpisy"
METHOD_BY_LABEL = {"Rovnoměrné (§ 31)": "linear", "Zrychlené (§ 32)": "accelerated"}


def apply_after_submit(asset, method=None):
    """Asset on_submit hook: apply the tax schedule after commit, once ERPNext has finalised
    the asset's depreciation schedules."""
    asset_name = asset.name
    frappe.db.after_commit.add(lambda: apply_czech_tax_depreciation(asset_name))


@frappe.whitelist()
def apply_czech_tax_depreciation(asset_name):
    """Put statutory § 31/§ 32 amounts on the asset's CZ-Daňové odpisy schedule. Idempotent."""
    asset = frappe.db.get_value(
        "Asset", asset_name, ["asset_category", "purchase_amount", "available_for_use_date"],
        as_dict=True,
    )
    if not asset:
        return
    category = frappe.db.get_value(
        "Asset Category", asset.asset_category, ["cz_tax_group", "cz_tax_method"], as_dict=True
    )
    if not category or not category.get("cz_tax_group"):
        return
    ads_name = frappe.db.get_value(
        "Asset Depreciation Schedule",
        {"asset": asset_name, "finance_book": TAX_FINANCE_BOOK, "docstatus": 1},
        "name",
    )
    if not ads_name:
        return

    group = int(category.cz_tax_group)
    method = METHOD_BY_LABEL.get(category.get("cz_tax_method"), "linear")
    amounts = tax_depreciation_schedule(asset.purchase_amount, group, method)

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
