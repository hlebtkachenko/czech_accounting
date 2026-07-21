// Copyright (c) 2026, Hleb Tkachenko and contributors
// For license information, see license.txt
frappe.query_reports["Nezarazene ucty"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
	],
};
