// Copyright (c) 2023, Lewin Villar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Tickets By Developer"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.week_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.week_end()
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "User",
		},
		{
			"fieldname": "workflow_state",
			"label": __("Workflow State"),
			"fieldtype": "Link",
			"options": "Workflow State",
		},
		{
			"fieldname": "type",
			"label": __("Type"),
			"fieldtype": "Select",
			"options": "Historical\nDevelopment\nImplementation",
			"reqd": 1,
			"default": "Historical",
			"hidden":0
		},
		{
			"fieldname": "summary",
			"label": __("Summary"),
			"fieldtype": "Check",
			"default": 1,
			on_change: function() {
				const summary = frappe.query_report.get_filter_value('summary');
				// If checked, set
				frappe.query_report.toggle_filter_display('developer', !!summary);
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "dashboard",
			"label": __("Dashboard"),
			"fieldtype": "Check",
			"hidden": 1,
			"default": 0,
		}
		// {
		// 	"fieldname": "old_issues",
		// 	"label": __("Include Old Tickets"),
		// 	"fieldtype": "Check",
		// 	"default": 0,
		// },
	],
};
