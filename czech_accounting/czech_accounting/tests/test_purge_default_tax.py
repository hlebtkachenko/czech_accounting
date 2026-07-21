# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""purge_default_tax_setup must remove ERPNext's seeded default VAT templates and their bare,
unnumbered tax accounts, while never touching the Czech templates that post to the numbered 343
leaves. The failure mode that matters: the purge deleting a real Czech template (which references
a numbered account) and taking the company's VAT config down with it.
"""
import frappe
from frappe.tests import IntegrationTestCase

from czech_accounting.setup.vat_templates import purge_default_tax_setup

PREFIX = "ZZ Purge Test"


class TestPurgeDefaultTaxSetup(IntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = frappe.get_all("Company", limit=1, pluck="name")[0]

    def tearDown(self):
        for name in frappe.get_all(
            "Sales Taxes and Charges Template",
            filters={"company": self.company, "title": ["like", f"{PREFIX}%"]},
            pluck="name",
        ):
            frappe.delete_doc("Sales Taxes and Charges Template", name, force=1, ignore_permissions=True)
        for name in frappe.get_all(
            "Account", filters={"company": self.company, "account_name": ["like", f"{PREFIX}%"]}, pluck="name"
        ):
            frappe.delete_doc("Account", name, force=1, ignore_permissions=True)
        frappe.db.commit()  # noqa: this site commits on submit; clean up across the boundary

    def test_purges_unnumbered_keeps_numbered(self):
        junk_acc = self._tax_account(number=None, name=f"{PREFIX} Default VAT")
        kept_acc = self._tax_account(number="343991", name=f"{PREFIX} Numbered VAT")
        junk_tpl = self._sales_template(f"{PREFIX} Default", junk_acc)
        kept_tpl = self._sales_template(f"{PREFIX} Numbered", kept_acc)

        purge_default_tax_setup(self.company)

        self.assertFalse(frappe.db.exists("Sales Taxes and Charges Template", junk_tpl))
        self.assertFalse(frappe.db.exists("Account", junk_acc))
        self.assertTrue(frappe.db.exists("Sales Taxes and Charges Template", kept_tpl))
        self.assertTrue(frappe.db.exists("Account", kept_acc))

    def _tax_account(self, number, name):
        root = frappe.db.get_value(
            "Account",
            {"company": self.company, "root_type": "Liability", "is_group": 1, "parent_account": ["in", ["", None]]},
            "name",
        )
        doc = frappe.get_doc({
            "doctype": "Account", "account_name": name, "company": self.company,
            "parent_account": root, "is_group": 0, "root_type": "Liability", "account_type": "Tax",
        })
        if number:
            doc.account_number = number
        doc.insert(ignore_permissions=True)
        return doc.name

    def _sales_template(self, title, account_head):
        doc = frappe.new_doc("Sales Taxes and Charges Template")
        doc.title = title
        doc.company = self.company
        doc.append("taxes", {
            "charge_type": "On Net Total", "account_head": account_head, "rate": 21.0, "description": title,
        })
        doc.insert(ignore_permissions=True)
        return doc.name
