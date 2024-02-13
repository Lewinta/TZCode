// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

{
	{% include "tzcode/tzcode/report/monkey_avg_points/filters.js" %}
	{% include "tzcode/tzcode/report/monkey_avg_points/chart_funcs.js" %}
	// include "tzcode/tzcode/report/monkey_avg_points/get_chart.js" %}

	frappe.query_reports["Monkey Avg Points"] = {
		filters,
		after_datatable_render,
	};
}
