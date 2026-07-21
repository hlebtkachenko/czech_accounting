// Copyright (c) 2026, Hleb Tkachenko and contributors
// For license information, see license.txt
/* eslint-disable */

frappe.query_reports["Rozvaha"] = {
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
			description: __("Defaults to the Company's accounting book (Účetní odpisy)"),
		},
		{
			fieldname: "show_zero_rows",
			label: __("Show Zero Rows"),
			fieldtype: "Check",
			default: 0,
			description: __("Show all statutory rows, including empty ones"),
		},
	],
};
