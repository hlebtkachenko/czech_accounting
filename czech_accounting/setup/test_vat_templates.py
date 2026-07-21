"""Unit tests for the Czech VAT tax-row builders.

These cover the row structure only (no DB): the failure mode that matters is a
reverse-charge template that does NOT net to zero on account 343, which would
leave a phantom VAT liability or deduction.
"""

import unittest

from czech_accounting.setup.vat_templates import (
	VAT_RATES_2024_01_01,
	purchase_tax_rows,
	reverse_charge_rows,
	sales_tax_rows,
)

INPUT = "343.100 - DPH na vstupu - TC"
OUTPUT = "343.200 - DPH na výstupu - TC"


def _signed_amount(row, base):
	amount = row["rate"] / 100.0 * base
	return -amount if row.get("add_deduct_tax") == "Deduct" else amount


class TestVATTaxRows(unittest.TestCase):
	def test_sales_row_posts_output_vat(self):
		rows = sales_tax_rows(21.0, OUTPUT)
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["account_head"], OUTPUT)
		self.assertEqual(rows[0]["rate"], 21.0)
		self.assertEqual(rows[0]["charge_type"], "On Net Total")

	def test_purchase_row_posts_input_vat(self):
		rows = purchase_tax_rows(12.0, INPUT)
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["account_head"], INPUT)
		self.assertEqual(rows[0]["rate"], 12.0)

	def test_reverse_charge_nets_to_zero(self):
		base = 100000.0
		for rate in (21.0, 12.0):
			rows = reverse_charge_rows(rate, INPUT, OUTPUT)
			self.assertEqual(len(rows), 2)
			total = sum(_signed_amount(r, base) for r in rows)
			self.assertAlmostEqual(total, 0.0, places=6)

	def test_reverse_charge_hits_both_343_subaccounts(self):
		rows = reverse_charge_rows(21.0, INPUT, OUTPUT)
		add = next(r for r in rows if r.get("add_deduct_tax") == "Add")
		deduct = next(r for r in rows if r.get("add_deduct_tax") == "Deduct")
		self.assertEqual(add["account_head"], OUTPUT)   # self-assessed output
		self.assertEqual(deduct["account_head"], INPUT)  # claimed input

	def test_rates_never_include_abolished_15_percent(self):
		self.assertNotIn(15.0, VAT_RATES_2024_01_01.values())
		self.assertEqual(VAT_RATES_2024_01_01["standard"], 21.0)
		self.assertEqual(VAT_RATES_2024_01_01["reduced"], 12.0)


if __name__ == "__main__":
	unittest.main()
