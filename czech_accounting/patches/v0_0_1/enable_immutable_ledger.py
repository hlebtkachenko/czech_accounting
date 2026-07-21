"""Enable the immutable ledger (locked project decision).

Submitted GL entries become uneditable and cancellations post reversal entries instead of
deleting rows, which is what Czech statutory bookkeeping expects. Idempotent.
"""
import frappe


def execute():
    frappe.db.set_single_value("Accounts Settings", "enable_immutable_ledger", 1)
