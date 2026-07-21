"""Per-company Czech VAT configuration: tax templates and cash/bank Mode of Payment.

This is company-scoped on purpose. ERPNext tax templates and Mode of Payment
account rows reference per-company ``Account`` records (created by Stream 1 from
the Czech chart of accounts). A single global fixture cannot express that on a
one-site / many-companies deployment, so we materialise the config by looking up
accounts by their frozen account number. Everything here is idempotent and safe
to re-run.

Posting accounts are the analytical leaves from Stream 1's chart: input VAT on
343.100, output VAT on 343.200, bank on 221001, cash on 211. The parents 343 and
221 are group accounts and cannot be posted to.

Rates are effective-dated. Since 2024-01-01 (Act 349/2023) the Czech rates are
21 % standard and 12 % reduced; the former 15 % rate is abolished. There is no
statutory 0 % rate, so the "0 %" template stands for osvobozeno s nárokem na
odpočet / export / mimo předmět (a zero DPH line, no tax posted).

Run after Stream 1 has built a company's chart of accounts::

    bench --site <site> execute czech_accounting.setup.vat_templates.setup_all_companies
"""

import frappe

# Effective-dated VAT rates (Act 349/2023, in force since 2024-01-01).
VAT_RATES_2024_01_01 = {"standard": 21.0, "reduced": 12.0, "zero": 0.0}

# Frozen posting-leaf account anchors from Stream 1's chart of accounts.
INPUT_VAT_ACCOUNT = "343.100"   # DPH na vstupu (input VAT)
OUTPUT_VAT_ACCOUNT = "343.200"  # DPH na výstupu (output VAT)
CASH_ACCOUNT = "211"            # Pokladna (cash)
BANK_ACCOUNT = "221001"         # Bankovní účet CZK


def get_account(company, account_number):
	name = frappe.db.get_value(
		"Account", {"company": company, "account_number": account_number}, "name"
	)
	if not name:
		frappe.throw(f"Account {account_number} not found for company {company}")
	return name


# --- Pure tax-row builders (no DB; unit-tested) -----------------------------

def sales_tax_rows(rate, output_account):
	"""Standard output-VAT row on 343.200."""
	return [
		{
			"charge_type": "On Net Total",
			"account_head": output_account,
			"rate": rate,
			"description": f"DPH {rate:g} % na výstupu",
		}
	]


def purchase_tax_rows(rate, input_account):
	"""Standard input-VAT (deductible) row on 343.100."""
	return [
		{
			"charge_type": "On Net Total",
			"account_head": input_account,
			"rate": rate,
			"description": f"DPH {rate:g} % na vstupu",
		}
	]


def reverse_charge_rows(rate, input_account, output_account):
	"""Přenesená daňová povinnost (§ 92) self-assessment — nets to zero.

	The buyer self-assesses output VAT (credit) and claims the matching input VAT
	(debit) at the same base and rate, on 343.200 (output) and 343.100 (input). The two rows
	cancel in the invoice grand total, so only the net is paid to the supplier,
	and the 343 group nets to zero. Covers §92e construction PDP.
	"""
	return [
		{
			"charge_type": "On Net Total",
			"account_head": output_account,
			"rate": rate,
			"add_deduct_tax": "Add",
			"description": f"PDP {rate:g} % — samovyměření DPH na výstupu",
		},
		{
			"charge_type": "On Net Total",
			"account_head": input_account,
			"rate": rate,
			"add_deduct_tax": "Deduct",
			"description": f"PDP {rate:g} % — nárok na odpočet DPH na vstupu",
		},
	]


# --- Per-company writers (idempotent) ---------------------------------------

def _upsert_template(doctype, company, title, rows):
	if frappe.db.exists(doctype, {"company": company, "title": title}):
		return
	doc = frappe.new_doc(doctype)
	doc.title = title
	doc.company = company
	for row in rows:
		doc.append("taxes", row)
	doc.insert(ignore_permissions=True)


def _ensure_mode_of_payment(name, mop_type, company, account_number):
	account = get_account(company, account_number)
	if frappe.db.exists("Mode of Payment", name):
		mop = frappe.get_doc("Mode of Payment", name)
	else:
		mop = frappe.new_doc("Mode of Payment")
		mop.mode_of_payment = name
		mop.type = mop_type
	for row in mop.accounts:
		if row.company == company:
			row.default_account = account
			break
	else:
		mop.append("accounts", {"company": company, "default_account": account})
	mop.save(ignore_permissions=True)


def setup_company_vat(company):
	"""Create the Czech tax templates and cash/bank modes for one company.

	Titles are bare (e.g. "DPH 21 %"). ERPNext's tax-template autoname appends
	" - {abbr}" to build the record name, so do NOT add the abbr here or the name
	ends up double-suffixed.
	"""
	input_vat = get_account(company, INPUT_VAT_ACCOUNT)
	output_vat = get_account(company, OUTPUT_VAT_ACCOUNT)
	rates = VAT_RATES_2024_01_01

	sales = "Sales Taxes and Charges Template"
	_upsert_template(sales, company, "DPH 21 %", sales_tax_rows(rates["standard"], output_vat))
	_upsert_template(sales, company, "DPH 12 %", sales_tax_rows(rates["reduced"], output_vat))
	_upsert_template(sales, company, "DPH 0 % (osvobozeno / vývoz)", sales_tax_rows(rates["zero"], output_vat))

	purchase = "Purchase Taxes and Charges Template"
	_upsert_template(purchase, company, "DPH 21 %", purchase_tax_rows(rates["standard"], input_vat))
	_upsert_template(purchase, company, "DPH 12 %", purchase_tax_rows(rates["reduced"], input_vat))
	_upsert_template(purchase, company, "DPH 0 % (osvobozeno / dovoz)", purchase_tax_rows(rates["zero"], input_vat))
	_upsert_template(purchase, company, "PDP 21 % (přenesená daňová povinnost)", reverse_charge_rows(rates["standard"], input_vat, output_vat))
	_upsert_template(purchase, company, "PDP 12 % (přenesená daňová povinnost)", reverse_charge_rows(rates["reduced"], input_vat, output_vat))

	_ensure_mode_of_payment("Cash", "Cash", company, CASH_ACCOUNT)
	_ensure_mode_of_payment("Bank", "Bank", company, BANK_ACCOUNT)

	frappe.db.commit()


def setup_all_companies():
	"""Run the VAT setup for every company that already has the 343 accounts."""
	for company in frappe.get_all("Company", pluck="name"):
		if frappe.db.exists("Account", {"company": company, "account_number": OUTPUT_VAT_ACCOUNT}):
			setup_company_vat(company)
