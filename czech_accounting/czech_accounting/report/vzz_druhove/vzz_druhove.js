// Copyright (c) 2026, Hleb Tkachenko and contributors
// For license information, see license.txt
/* eslint-disable */

frappe.query_reports["VZZ druhove"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.year_start(),
			description: __("Defaults to the start of the fiscal year of To Date"),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "previous_to_date",
			label: __("Previous Period End"),
			fieldtype: "Date",
			description: __("Defaults to one year before To Date"),
		},
		{
			fieldname: "finance_book",
			label: __("Finance Book"),
			fieldtype: "Link",
			options: "Finance Book",
			description: __("Select the accounting book (CZ-Účetní odpisy) for the statutory statement"),
		},
	],
};
