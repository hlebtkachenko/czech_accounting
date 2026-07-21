# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Genuine fixed asset (automobil) depreciates on both Finance Books.

Builds the CZ-Automobil Asset Category programmatically (its accounts are per-company, so it is
not a fixture) with the two finance books from fixtures/finance_book.json (CZ-Účetní odpisy
monthly, CZ-Daňové odpisy annual), creates an Asset that uses it, submits it, and asserts two
parallel schedules exist — účetní (straight line) vs daňové (statutory § 31/§ 32, non-posting).
The IntegrationTestCase data is cancelled/removed in teardown.
"""

import frappe
from frappe.tests import IntegrationTestCase

from czech_accounting.assets.tax_depreciation import tax_depreciation_schedule

FINANCE_BOOKS = [
    ("CZ-Účetní odpisy", "Straight Line", 60, 1),
    ("CZ-Daňové odpisy", "Straight Line", 5, 12),
]
GROSS = 300_000.0


class TestAssetDepreciation(IntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = frappe.get_all("Company", limit=1, pluck="name")[0]
        cls.abbr = frappe.get_cached_value("Company", cls.company, "abbr")
        _ensure_finance_books()
        accounts = _ensure_asset_accounts(cls.company, cls.abbr)
        _ensure_category(cls.company, *accounts)
        _ensure_item()
        _ensure_location()

    def test_two_finance_books_depreciate(self):
        asset = frappe.new_doc("Asset")
        asset.update({
            "asset_name": "CZ Test Car Depreciation",
            "asset_category": "CZ-Automobil",
            "item_code": "CZ-TEST-CAR",
            "company": self.company,
            "purchase_date": "2026-01-01",
            "available_for_use_date": "2026-01-01",
            "gross_purchase_amount": GROSS,
            "net_purchase_amount": GROSS,
            "purchase_amount": GROSS,
            "calculate_depreciation": 1,
            "location": "CZ Test Location",
            "asset_owner": "Company",
            "asset_quantity": 1,
        })
        for fb, method, total, freq in FINANCE_BOOKS:
            asset.append("finance_books", {
                "finance_book": fb,
                "depreciation_method": method,
                "total_number_of_depreciations": total,
                "frequency_of_depreciation": freq,
                "depreciation_start_date": "2026-01-31",
            })
        asset.insert(ignore_permissions=True)
        asset.submit()
        self.addCleanup(_delete_asset, asset.name)

        # In production this runs from the Asset on_submit hook after commit; call it directly
        # here since the test transaction never commits.
        from czech_accounting.assets.cz_ads import apply_czech_tax_depreciation

        apply_czech_tax_depreciation(asset.name)

        schedules = frappe.get_all(
            "Asset Depreciation Schedule",
            filters={"asset": asset.name, "docstatus": 1},
            fields=["name", "finance_book"],
        )
        books = {s.finance_book for s in schedules}
        self.assertEqual(len(schedules), 2, f"expected 2 schedules, got {schedules}")
        self.assertEqual(books, {"CZ-Účetní odpisy", "CZ-Daňové odpisy"})
        for s in schedules:
            rows = frappe.db.count("Depreciation Schedule", {"parent": s.name})
            self.assertGreater(rows, 0, f"no depreciation rows for {s.finance_book}")

        # The tax book must carry the statutory § 31 amounts, not ERPNext straight line.
        tax = next(s for s in schedules if s.finance_book == "CZ-Daňové odpisy")
        tax_rows = frappe.get_all(
            "Depreciation Schedule",
            filters={"parent": tax.name},
            fields=["depreciation_amount"],
            order_by="idx",
        )
        self.assertEqual(
            [r.depreciation_amount for r in tax_rows],
            tax_depreciation_schedule(GROSS, 2, "linear"),
            "CZ-Daňové odpisy must use statutory § 31 amounts, not ERPNext straight line",
        )


def _delete_asset(name):
    try:
        doc = frappe.get_doc("Asset", name)
        if doc.docstatus == 1:
            doc.cancel()
        frappe.delete_doc("Asset", name, force=True, ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()


def _ensure_finance_books():
    for name in ("CZ-Účetní odpisy", "CZ-Daňové odpisy"):
        if not frappe.db.exists("Finance Book", name):
            frappe.get_doc({"doctype": "Finance Book", "finance_book_name": name}).insert(ignore_permissions=True)


def _group_parent(company, abbr, root_type):
    parent = f"CZ Asset Test {root_type} - {abbr}"
    if not frappe.db.exists("Account", parent):
        root = frappe.db.get_value(
            "Account",
            {"company": company, "root_type": root_type, "is_group": 1, "parent_account": ["in", ["", None]]},
            "name",
        )
        frappe.get_doc({
            "doctype": "Account", "account_name": f"CZ Asset Test {root_type}", "company": company,
            "parent_account": root, "is_group": 1, "root_type": root_type,
        }).insert(ignore_permissions=True)
    return parent


def _account(company, abbr, number, name, root_type, account_type):
    existing = frappe.db.get_value("Account", {"account_number": number, "company": company}, "name")
    if existing:
        return existing
    parent = _group_parent(company, abbr, root_type)
    doc = frappe.get_doc({
        "doctype": "Account", "account_name": name, "account_number": number, "company": company,
        "parent_account": parent, "is_group": 0, "root_type": root_type, "account_type": account_type,
    })
    doc.insert(ignore_permissions=True)
    return doc.name


def _ensure_asset_accounts(company, abbr):
    fa = _account(company, abbr, "0229", "Automobil (asset test)", "Asset", "Fixed Asset")
    ad = _account(company, abbr, "0829", "Oprávky k automobilu (asset test)", "Asset", "Accumulated Depreciation")
    de = _account(company, abbr, "5519", "Odpisy DHM (asset test)", "Expense", "Depreciation")
    return fa, ad, de


def _ensure_category(company, fa, ad, de):
    if frappe.db.exists("Asset Category", "CZ-Automobil"):
        cat = frappe.get_doc("Asset Category", "CZ-Automobil")
    else:
        cat = frappe.new_doc("Asset Category")
        cat.asset_category_name = "CZ-Automobil"
        cat.enable_cwip_accounting = 0
        for fb, method, total, freq in FINANCE_BOOKS:
            cat.append("finance_books", {
                "finance_book": fb, "depreciation_method": method,
                "total_number_of_depreciations": total, "frequency_of_depreciation": freq,
            })
    if not any(a.company_name == company for a in cat.accounts):
        cat.append("accounts", {
            "company_name": company,
            "fixed_asset_account": fa,
            "accumulated_depreciation_account": ad,
            "depreciation_expense_account": de,
        })
    cat.cz_tax_group = "2"  # osobní automobil -> group 2 (5 years)
    cat.cz_tax_method = "Rovnoměrné (§ 31)"
    cat.save(ignore_permissions=True)


def _ensure_item():
    if not frappe.db.exists("Item", "CZ-TEST-CAR"):
        frappe.get_doc({
            "doctype": "Item", "item_code": "CZ-TEST-CAR", "item_name": "CZ Test Car",
            "item_group": "All Item Groups", "stock_uom": "Nos", "is_stock_item": 0,
            "is_fixed_asset": 1, "asset_category": "CZ-Automobil",
        }).insert(ignore_permissions=True)


def _ensure_location():
    if not frappe.db.exists("Location", "CZ Test Location"):
        frappe.get_doc({"doctype": "Location", "location_name": "CZ Test Location"}).insert(ignore_permissions=True)
