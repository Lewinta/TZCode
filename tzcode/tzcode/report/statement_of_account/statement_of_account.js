// Copyright (c) 2016, Lewin Villar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Statement of Account"] = {
	"filters": [
		{
			"label": __("From Date"),
			"fieldname": "from_date",
			"fieldtype": "Date",
			"bold": "1",
		},
		{
			"label": __("To Date"),
			"fieldname": "to_date",
			"fieldtype": "Date",
			"bold": "1",
		},
		{
			"label": __("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"bold": "1",
		},
		{
			"label": __("Currency"),
			"fieldname": "currency",
			"fieldtype": "Select",
			"options": "Invoice Currency\nCompany Currency",
			"default": "Company Currency",
		},
		{
			"label": __("Mostrar solo Pendientes?"),
			"fieldname": "unpaid",
			"fieldtype": "Check",
			"default": "1",
		},
	]
};
