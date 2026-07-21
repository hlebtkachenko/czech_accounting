"""Unit tests for the Czech invoice boundary validators (pure decisions)."""

import sys
import types
import unittest

# Let the module import without a bench when run standalone.
if "frappe" not in sys.modules:
	fake = types.ModuleType("frappe")

	class ValidationError(Exception):
		pass

	def throw(msg, *args, **kwargs):
		raise ValidationError(msg)

	fake.ValidationError = ValidationError
	fake.throw = throw
	fake.msgprint = lambda *a, **k: None
	fake._ = lambda s: s
	sys.modules["frappe"] = fake

from czech_accounting.doc_events import (  # noqa: E402
	REVERSE_CHARGE_SUPPLY_TYPE,
	duzp_required_and_missing,
	reverse_charge_mismatch,
	validate_sales_invoice,
)


class TestDUZPRequired(unittest.TestCase):
	def test_taxed_without_duzp_is_flagged(self):
		self.assertTrue(duzp_required_and_missing({"taxes": [{}]}))

	def test_taxed_with_duzp_is_ok(self):
		self.assertFalse(duzp_required_and_missing({"taxes": [{}], "cz_duzp": "2026-01-01"}))

	def test_no_tax_rows_is_ok(self):
		# neplátce / exempt: no tax rows, DUZP not forced
		self.assertFalse(duzp_required_and_missing({}))

	def test_validate_throws_when_taxed_without_duzp(self):
		with self.assertRaises(Exception):
			validate_sales_invoice({"taxes": [{}]})


class TestReverseChargeMismatch(unittest.TestCase):
	def test_checked_without_supply_type_is_flagged(self):
		self.assertTrue(reverse_charge_mismatch({"cz_is_reverse_charge": 1}))

	def test_checked_with_pdp_supply_type_is_ok(self):
		self.assertFalse(
			reverse_charge_mismatch(
				{"cz_is_reverse_charge": 1, "cz_vat_supply_type": REVERSE_CHARGE_SUPPLY_TYPE}
			)
		)

	def test_unchecked_is_ok(self):
		self.assertFalse(reverse_charge_mismatch({"cz_is_reverse_charge": 0}))


if __name__ == "__main__":
	unittest.main()
