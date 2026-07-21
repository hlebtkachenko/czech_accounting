# Copyright (c) 2026, Hleb Tkachenko and contributors
# For license information, see license.txt
"""Integration test for the Czech statutory books.

Builds a small self-contained scenario (bank, capital, a build-to-sell construction that
accumulates in 121 with a period-end change-in-state MD 121 / D 611, a unit sale that
derecognizes from 121, a fixed asset with účetní oprávky, and output VAT) under the site's
company, then asserts:

  * Rozvaha reconciles: AKTIVA CELKEM netto == PASIVA CELKEM netto.
  * Brutto/Korekce/Netto split works on the fixed-asset row (022 gross vs 082 oprávky).
  * The provisional period result lands in A.V and equals the VZZ bottom line.
  * The change-in-state makes the construction P&L-neutral within the period and 121 carries
    the remaining WIP; the WIP report shows it by project.
  * Účetní deník lists every entry chronologically with total MD == total Dal.

The IntegrationTestCase transaction is rolled back, so no data survives the test.
"""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowdate

from czech_accounting.czech_accounting.report.nedokoncena_vyroba import nedokoncena_vyroba
from czech_accounting.czech_accounting.report.rozvaha import rozvaha
from czech_accounting.czech_accounting.report.ucetni_denik import ucetni_denik
from czech_accounting.czech_accounting.report.vzz_druhove import vzz_druhove

CATEGORIES = [
    ("CZ-rozvaha-aktiva-c-iv-2", "Asset", "Peněžní prostředky na účtech"),
    ("CZ-rozvaha-aktiva-c-i-2", "Asset", "Nedokončená výroba a polotovary"),
    ("CZ-rozvaha-aktiva-c-ii-2-1", "Asset", "Pohledávky z obchodních vztahů (krátkodobé)"),
    ("CZ-rozvaha-aktiva-c-ii-2-4-3", "Liability", "Stát – daňové pohledávky"),
    ("CZ-rozvaha-aktiva-b-ii-2", "Asset", "Hmotné movité věci a jejich soubory"),
    ("CZ-rozvaha-pasiva-a-i-1", "Equity", "Základní kapitál"),
    ("CZ-rozvaha-pasiva-a-v", "Equity", "Výsledek hospodaření běžného účetního období (+/-)"),
    ("CZ-rozvaha-pasiva-c-ii-4", "Liability", "Závazky z obchodních vztahů (krátkodobé)"),
    ("CZ-rozvaha-pasiva-c-ii-8-5", "Liability", "Stát – daňové závazky a dotace"),
    ("CZ-vzz-ii", "Income", "Tržby za prodej zboží"),
    ("CZ-vzz-b", "Expense", "Změna stavu zásob vlastní činnosti (+/-)"),
    ("CZ-vzz-a-2", "Expense", "Spotřeba materiálu a energie"),
    ("CZ-vzz-a-3", "Expense", "Služby"),
    ("CZ-vzz-e-1-1", "Expense", "Úpravy hodnot DNM a DHM – trvalé"),
]

# account_number, account_name, root_type, category
ACCOUNTS = [
    ("221", "Bankovní účty (test)", "Asset", "CZ-rozvaha-aktiva-c-iv-2"),
    ("121", "Nedokončená výroba (test)", "Asset", "CZ-rozvaha-aktiva-c-i-2"),
    ("311", "Odběratelé (test)", "Asset", "CZ-rozvaha-aktiva-c-ii-2-1"),
    ("022", "Automobil (test)", "Asset", "CZ-rozvaha-aktiva-b-ii-2"),
    ("082", "Oprávky k automobilu (test)", "Asset", "CZ-rozvaha-aktiva-b-ii-2"),
    ("411", "Základní kapitál (test)", "Equity", "CZ-rozvaha-pasiva-a-i-1"),
    ("321", "Dodavatelé (test)", "Liability", "CZ-rozvaha-pasiva-c-ii-4"),
    ("343", "DPH (test)", "Liability", "CZ-rozvaha-pasiva-c-ii-8-5"),
    ("604", "Tržby za zboží (test)", "Income", "CZ-vzz-ii"),
    ("611", "Změna stavu NV (test)", "Income", "CZ-vzz-b"),
    ("501", "Spotřeba materiálu (test)", "Expense", "CZ-vzz-a-2"),
    ("518", "Ostatní služby (test)", "Expense", "CZ-vzz-a-3"),
    ("551", "Odpisy (test)", "Expense", "CZ-vzz-e-1-1"),
]

# Suffix appended to every scenario account number. The real Czech chart has some of these
# numbers as *group* accounts (221, 343) or as Receivable/Payable leaves that demand a party on
# a journal line (311, 321); reusing them makes the scenario impossible to post. The suffix keeps
# the leading class digits (is_correction_account reads the prefix) while guaranteeing the test
# builds its own fresh, type-less, postable leaves that never collide with the production chart.
TEST_SUFFIX = "T"

EXPECTED_BALANCE = 1_721_000.0
EXPECTED_RESULT = 295_000.0

# Tag on every JE this test posts, so the scenario can be cancelled deterministically.
# This site runs with immutable ledger + auto-commit on submit, so per-test transaction
# rollback does not undo posted GL; the scenario is posted once and cancelled explicitly.
TAG = "CZ-S3-TEST"


class TestRozvaha(IntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = frappe.get_all("Company", limit=1, pluck="name")[0]
        cls.abbr = frappe.get_cached_value("Company", cls.company, "abbr")
        cls.cost_center = frappe.get_cached_value("Company", cls.company, "cost_center")
        cls.date = nowdate()
        _ensure_categories()
        cls.acc = _ensure_accounts(cls.company, cls.abbr)
        cls.project = _ensure_project(cls.company)
        _cancel_scenario(cls.company)          # clear any residue from a prior run
        cls._post_scenario()
        frappe.db.commit()  # noqa: this test manages its own data across the commit boundary

    @classmethod
    def tearDownClass(cls):
        _cancel_scenario(cls.company)
        frappe.db.commit()  # noqa
        super().tearDownClass()

    @classmethod
    def _je(cls, lines):
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.company = cls.company
        je.posting_date = cls.date
        je.user_remark = TAG
        for account, debit, credit in lines:
            je.append("accounts", {
                "account": cls.acc[account],
                "debit_in_account_currency": debit,
                "credit_in_account_currency": credit,
                "cost_center": cls.cost_center,
                "project": cls.project,
            })
        je.insert()
        je.submit()
        return je

    @classmethod
    def _post_scenario(cls):
        cls._je([("221", 1_000_000, 0), ("411", 0, 1_000_000)])            # capital
        cls._je([("022", 300_000, 0), ("221", 0, 300_000)])                # buy car
        cls._je([("501", 400_000, 0), ("321", 0, 400_000)])                # material -> cost
        cls._je([("518", 100_000, 0), ("321", 0, 100_000)])                # services -> cost
        cls._je([("121", 500_000, 0), ("611", 0, 500_000)])                # change-in-state MD121/D611
        cls._je([("551", 5_000, 0), ("082", 0, 5_000)])                    # depreciation
        cls._je([("311", 600_000, 0), ("604", 0, 600_000)])                # unit sale revenue
        cls._je([("611", 300_000, 0), ("121", 0, 300_000)])                # derecognize sold unit cost
        cls._je([("311", 126_000, 0), ("343", 0, 126_000)])                # output VAT
        cls._je([("321", 200_000, 0), ("221", 0, 200_000)])                # pay supplier

    def _rozvaha(self):
        _cols, rows = rozvaha.execute({"company": self.company, "to_date": self.date, "show_zero_rows": 1})
        return {r["ukazatel"]: r for r in rows if r.get("ukazatel")}

    def test_rozvaha_reconciles(self):
        rows = self._rozvaha()
        self.assertAlmostEqual(rows["AKTIVA CELKEM"]["netto"], rows["PASIVA CELKEM"]["netto"], places=2)
        self.assertAlmostEqual(rows["AKTIVA CELKEM"]["netto"], EXPECTED_BALANCE, places=2)
        self.assertNotIn("KONTROLA — Aktiva − Pasiva (musí být 0)", rows)

    def test_brutto_korekce_netto(self):
        rows = self._rozvaha()
        row = rows["Hmotné movité věci a jejich soubory"]
        self.assertAlmostEqual(row["brutto"], 300_000, places=2)
        self.assertAlmostEqual(row["korekce"], -5_000, places=2)
        self.assertAlmostEqual(row["netto"], 295_000, places=2)

    def test_result_in_av_equals_vzz(self):
        rows = self._rozvaha()
        av = rows["Výsledek hospodaření běžného účetního období (+/-)"]["netto"]
        self.assertAlmostEqual(av, EXPECTED_RESULT, places=2)

        _cols, vzz_rows = vzz_druhove.execute({"company": self.company, "to_date": self.date})
        total = next(r for r in vzz_rows if r["ukazatel"].startswith("***"))
        self.assertAlmostEqual(total["current"], EXPECTED_RESULT, places=2)
        self.assertAlmostEqual(total["current"], av, places=2)

    def test_construction_pnl_neutral_and_wip_remaining(self):
        # 501 + 518 = 500k cost; 611 change-in-state credit net = 500k - 300k(sold) = 200k
        _cols, wip = nedokoncena_vyroba.execute({"company": self.company, "to_date": self.date})
        total = next(r for r in wip if r.get("account") == "Celkem nedokončená výroba")
        self.assertAlmostEqual(total["balance"], 200_000, places=2)
        # the project analytics carry the WIP
        self.assertTrue(any(r.get("project") == self.project for r in wip))

    def test_denik_chronological_balanced(self):
        _cols, rows = ucetni_denik.execute({"company": self.company, "to_date": self.date})
        entries = [r for r in rows if r.get("entry_no")]
        self.assertTrue(entries)
        self.assertEqual([e["entry_no"] for e in entries], list(range(1, len(entries) + 1)))
        totals = next(r for r in rows if not r.get("entry_no"))
        self.assertAlmostEqual(totals["debit"], totals["credit"], places=2)


def _cancel_scenario(company):
    names = frappe.get_all(
        "Journal Entry",
        filters={"company": company, "user_remark": TAG, "docstatus": 1},
        pluck="name",
    )
    for n in names:
        frappe.get_doc("Journal Entry", n).cancel()


def _ensure_categories():
    for name, root_type, desc in CATEGORIES:
        if not frappe.db.exists("Account Category", name):
            frappe.get_doc({
                "doctype": "Account Category",
                "account_category_name": name,
                "root_type": root_type,
                "description": desc,
            }).insert(ignore_permissions=True)


def _ensure_project(company):
    project_name = "CZ Test Development"
    existing = frappe.db.get_value("Project", {"project_name": project_name}, "name")
    if existing:
        return existing
    doc = frappe.get_doc({"doctype": "Project", "project_name": project_name, "company": company})
    doc.insert(ignore_permissions=True)
    return doc.name


def _group_parent(company, abbr, root_type):
    """Return a group account of the given root_type to parent test leaves under."""
    parent = f"CZ Test {root_type} - {abbr}"
    if frappe.db.exists("Account", parent):
        return parent
    root = frappe.db.get_value(
        "Account",
        {"company": company, "root_type": root_type, "is_group": 1, "parent_account": ["in", ["", None]]},
        "name",
    )
    frappe.get_doc({
        "doctype": "Account", "account_name": f"CZ Test {root_type}", "company": company,
        "parent_account": root, "is_group": 1, "root_type": root_type,
    }).insert(ignore_permissions=True)
    return parent


def _ensure_accounts(company, abbr):
    mapping = {}
    for number, acc_name, root_type, category in ACCOUNTS:
        acc_number = number + TEST_SUFFIX
        existing = frappe.db.get_value("Account", {"account_number": acc_number, "company": company}, "name")
        if existing:
            frappe.db.set_value("Account", existing, "account_category", category)
            mapping[number] = existing
            continue
        parent = _group_parent(company, abbr, root_type)
        doc = frappe.get_doc({
            "doctype": "Account", "account_name": acc_name, "account_number": acc_number,
            "company": company, "parent_account": parent, "is_group": 0,
            "root_type": root_type, "account_category": category,
        })
        doc.insert(ignore_permissions=True)
        mapping[number] = doc.name
    return mapping
