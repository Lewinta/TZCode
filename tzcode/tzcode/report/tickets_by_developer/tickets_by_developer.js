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
			"options": "Historical\nDevelopment\nTimesheet",
			"reqd": 1,
			"default": "Historical",
			"hidden":0,
			on_change: function() {
				const type = frappe.query_report.get_filter_value('type') == "Timesheet";
				// If checked, set
				frappe.query_report.toggle_filter_display('group_by', !type);
				frappe.query_report.toggle_filter_display('employee', !!type);
				frappe.query_report.toggle_filter_display('workflow_state', !!type);
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": "Developer\nIssue",
			"default": "Developer",
			"hidden": 1,
		},
		{
			"fieldname": "summary",
			"label": __("Summary"),
			"fieldtype": "Check",
			"default": 1,
			on_change: function() {
				const summary = frappe.query_report.get_filter_value('summary');
				const type = frappe.query_report.get_filter_value('type');
				// If checked, set
				frappe.query_report.toggle_filter_display('developer', !!summary);
				frappe.query_report.toggle_filter_display('group_by', !summary && type == "Timesheet");
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
