// Copyright (c) 2016, Lewin Villar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cuentas por Pagar Relacionadas"] = {
	"filters": [
		{
			"label": __("Related Entity"),
			"fieldname": "related_entity",
			"fieldtype": "Link",
			"options": "Related Entity",
		},
		{
			"label": __("Summarized?"),
			"fieldname": "summarized",
			"fieldtype": "Check",
		}
	]
};
