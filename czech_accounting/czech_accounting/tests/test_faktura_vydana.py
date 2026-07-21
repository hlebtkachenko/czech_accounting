# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""End-to-end agenda test: a faktura vydaná (Sales Invoice) with Czech output VAT posts the
expected předkontace to the general ledger — 311 (debtor) / 602 (revenue) + 343 (DPH výstup).

The site runs with immutable ledger + auto-commit on submit, so the invoice is posted once and
cancelled in teardown rather than relying on transaction rollback.
"""
import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

from czech_accounting.setup.coa import set_round_off_account
from czech_accounting.setup.vat_templates import sales_tax_rows

NET, RATE, VAT, GROSS = 100_000.0, 21, 21_000.0, 121_000.0
CUSTOMER = "CZ Test Odběratel"
ITEM = "CZ-TEST-SLUZBA"


class TestFakturaVydana(IntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = frappe.get_all("Company", limit=1, pluck="name")[0]
        cls.abbr = frappe.get_cached_value("Company", cls.company, "abbr")
        cls.cost_center = frappe.get_cached_value("Company", cls.company, "cost_center")
        cls.acc = _ensure_accounts(cls.company, cls.abbr)
        set_round_off_account(cls.company)  # rounded invoices need a Round Off Account to post
        _ensure_customer()
        _ensure_item(cls.acc["602"])
        _cancel_invoices(cls.company)
        cls.si = _make_invoice(cls.company, cls.acc, cls.cost_center)
        frappe.db.commit()  # noqa: manages its own data across the commit boundary

    @classmethod
    def tearDownClass(cls):
        _cancel_invoices(cls.company)
        frappe.db.commit()  # noqa
        super().tearDownClass()

    def test_predkontace_and_vat(self):
        gl = {}
        for row in frappe.get_all(
            "GL Entry", filters={"voucher_no": self.si}, fields=["account", "debit", "credit"]
        ):
            d, c = gl.get(row.account, (0.0, 0.0))
            gl[row.account] = (d + row.debit, c + row.credit)

        self.assertAlmostEqual(gl[self.acc["311"]][0], GROSS, places=2)   # 311 debit = gross
        self.assertAlmostEqual(gl[self.acc["602"]][1], NET, places=2)     # 602 credit = net revenue
        self.assertAlmostEqual(gl[self.acc["343"]][1], VAT, places=2)     # 343 credit = output VAT
        total_debit = sum(d for d, _ in gl.values())
        total_credit = sum(c for _, c in gl.values())
        self.assertAlmostEqual(total_debit, total_credit, places=2)       # balanced


def _make_invoice(company, acc, cost_center):
    si = frappe.new_doc("Sales Invoice")
    si.company = company
    si.customer = CUSTOMER
    si.posting_date = si.due_date = nowdate()
    si.cz_duzp = nowdate()  # datum uskutečnění zdanitelného plnění — required by Stream 2's validator
    si.debit_to = acc["311"]
    si.append("items", {
        "item_code": ITEM, "qty": 1, "rate": NET,
        "income_account": acc["602"], "cost_center": cost_center,
    })
    for row in sales_tax_rows(RATE, acc["343"]):
        si.append("taxes", {**row, "cost_center": cost_center})
    si.insert(ignore_permissions=True)
    si.submit()
    return si.name


def _cancel_invoices(company):
    for name in frappe.get_all(
        "Sales Invoice", filters={"company": company, "customer": CUSTOMER, "docstatus": 1}, pluck="name"
    ):
        frappe.get_doc("Sales Invoice", name).cancel()


def _group_parent(company, abbr, root_type):
    parent = f"CZ FV Test {root_type} - {abbr}"
    if frappe.db.exists("Account", parent):
        return parent
    root = frappe.db.get_value(
        "Account",
        {"company": company, "root_type": root_type, "is_group": 1, "parent_account": ["in", ["", None]]},
        "name",
    )
    frappe.get_doc({
        "doctype": "Account", "account_name": f"CZ FV Test {root_type}", "company": company,
        "parent_account": root, "is_group": 1, "root_type": root_type,
    }).insert(ignore_permissions=True)
    return parent


def _account(company, abbr, number, name, root_type, account_type):
    existing = frappe.db.get_value("Account", {"account_number": number, "company": company}, "name")
    if existing:
        return existing
    doc = frappe.get_doc({
        "doctype": "Account", "account_name": name, "account_number": number, "company": company,
        "parent_account": _group_parent(company, abbr, root_type), "is_group": 0,
        "root_type": root_type, "account_type": account_type,
    })
    doc.insert(ignore_permissions=True)
    return doc.name


def _ensure_accounts(company, abbr):
    return {
        "311": _account(company, abbr, "311901", "Odběratelé (FV test)", "Asset", "Receivable"),
        "602": _account(company, abbr, "602901", "Tržby ze služeb (FV test)", "Income", ""),
        "343": _account(company, abbr, "343901", "DPH na výstupu (FV test)", "Liability", "Tax"),
    }


def _ensure_customer():
    if not frappe.db.exists("Customer", CUSTOMER):
        frappe.get_doc({
            "doctype": "Customer", "customer_name": CUSTOMER, "customer_type": "Company",
            "customer_group": frappe.db.get_value("Customer Group", {"is_group": 0}, "name"),
            "territory": frappe.db.get_value("Territory", {"is_group": 0}, "name"),
        }).insert(ignore_permissions=True)


def _ensure_item(income_account):
    if not frappe.db.exists("Item", ITEM):
        frappe.get_doc({
            "doctype": "Item", "item_code": ITEM, "item_name": "CZ Test služba",
            "item_group": "All Item Groups", "stock_uom": "Nos", "is_stock_item": 0,
        }).insert(ignore_permissions=True)
