# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""The Nezařazené účty report flags posting accounts that lack a CZ- statement category."""
import frappe
from frappe.tests import IntegrationTestCase

from czech_accounting.czech_accounting.report.nezarazene_ucty import nezarazene_ucty


class TestNezarazeneUcty(IntegrationTestCase):
    def test_flags_uncategorized_posting_account(self):
        company = frappe.get_all("Company", limit=1, pluck="name")[0]
        abbr = frappe.get_cached_value("Company", company, "abbr")
        parent = frappe.db.get_value(
            "Account",
            {"company": company, "root_type": "Asset", "is_group": 1, "parent_account": ["in", ["", None]]},
            "name",
        )
        unmapped = frappe.get_doc({
            "doctype": "Account", "account_name": "CZ Unmapped Test", "account_number": "099099",
            "company": company, "parent_account": parent, "is_group": 0, "root_type": "Asset",
        }).insert(ignore_permissions=True)

        _cols, data = nezarazene_ucty.execute({"company": company})
        names = {r["name"] for r in data}
        self.assertIn(unmapped.name, names, "an account with no CZ- category must be flagged")

        # A categorized account must NOT be flagged.
        unmapped.account_category = "CZ-rozvaha-aktiva-b-ii-2"
        unmapped.save(ignore_permissions=True)
        _cols, data2 = nezarazene_ucty.execute({"company": company})
        self.assertNotIn(unmapped.name, {r["name"] for r in data2})
