// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

function get_starting_date() {
	return frappe.datetime.month_start();
}

function get_ending_date() {
	return frappe.datetime.month_end();
}

const filters = [
	{
		fieldtype: "Date",
		label: __("Starting Date"),
		fieldname: "starting_date",
		default: get_starting_date(),
		reqd: 1,
	},
	{
		fieldtype: "Date",
		label: __("Ending Date"),
		fieldname: "ending_date",
		default: get_ending_date(),
		reqd: 1,
	},
	{
		fieldtype: "Link",
		fieldname: "resolver",
		label: "Resolver",
		options: "User",
		get_query: {
			name: [
				"in", [
					"rainierpolanco@tzcode.tech",
					"miguel.higuera@tzcode.tech",
					"reyferreras@tzcode.tech",
				]
			],
		},
		reqd: 0,
	},
	{
		fieldtype: "Select",
		fieldname: "status",
		label: "Status",
		options: [
			"",
			"Open",
			"Assigned",
			"Working",
			"Replied",
			"Hold",
			"Resolved",
			"Closed",
			"Ready for Development",
		],
	},
	{
		fieldtype: "Select",
		fieldname: "date_based_on",
		label: "Based On",
		options: [
			{"label": "Creation", "value": "creation"},
			{"label": "Delivered for QA", "value": "delivered_for_qa"},
		],
		default: "delivered_for_qa",
		reqd: 1,
	},
/* 	{
		fieldtype: "MultiSelect",
		fieldname: "workflow_states",
		label: "States",
		options: [
			{ label: "Open", value: "Opened" },
			{ label: "Close", value: "Closed" },
		],
	}, */
];