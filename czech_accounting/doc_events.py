"""Boundary validation for the Czech document agendas (Sales / Purchase Invoice).

Input-boundary checks only (run on `validate`, so also fine on repost, which does
not re-run document validation). Stream 1 wires these in hooks.py::

    doc_events = {
        "Sales Invoice": {"validate": "czech_accounting.doc_events.validate_sales_invoice"},
        "Purchase Invoice": {"validate": "czech_accounting.doc_events.validate_purchase_invoice"},
    }
"""

import frappe
from frappe import _

# Must match the option string in fixtures/custom_field_document.json.
REVERSE_CHARGE_SUPPLY_TYPE = "Reverse charge (§ 92)"


# --- Pure decisions (unit-tested) -------------------------------------------

def duzp_required_and_missing(doc):
	"""A VAT document (carries tax rows) must state its tax point (DUZP)."""
	return bool(doc.get("taxes")) and not doc.get("cz_duzp")


def reverse_charge_mismatch(doc):
	"""Reverse charge checked but supply type is not PDP — likely the wrong template."""
	return bool(doc.get("cz_is_reverse_charge")) and doc.get("cz_vat_supply_type") != REVERSE_CHARGE_SUPPLY_TYPE


# --- doc_events entry points ------------------------------------------------

def validate_sales_invoice(doc, method=None):
	_apply(doc)


def validate_purchase_invoice(doc, method=None):
	_apply(doc)


def _apply(doc):
	if duzp_required_and_missing(doc):
		frappe.throw(_("Date of Taxable Supply (DUZP) is required on a VAT document."))
	if reverse_charge_mismatch(doc):
		frappe.msgprint(
			_("Reverse charge is checked but VAT Supply Type is not '{0}'. Use a PDP tax template so account 343 nets to zero.").format(
				REVERSE_CHARGE_SUPPLY_TYPE
			),
			indicator="orange",
			alert=True,
		)
