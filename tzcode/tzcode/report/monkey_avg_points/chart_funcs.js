// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

function get_labels(result) {
	const periods = [];
	for (const row of result) {
		if (periods.includes(row.month)) {
			continue
		}
		periods.push(row.month);
	}

	return periods;
}

function get_total_points_by_period(result, periods) {
	const total_points = new Array();

	for (const period of periods) {
		let total = 0;
		for (const row of result) {
			if (row.month === period) {
				total += row.avg_points;
			}
		}
		total_points.push(total);
	}

	return total_points;
}

function get_issue_count_by_period(result, periods) {
	const issue_count = new Array();

	for (const period of periods) {
		let total = 0;
		for (const row of result) {
			if (row.month === period) {
				total += row.issue_count;
			}
		}
		issue_count.push(total);
	}

	return issue_count;
}

function get_avg_points_by_period(result, periods) {
	const avg_points = new Array();

	for (const period of periods) {
		let total = 0;
		for (const row of result) {
			if (row.month === period) {
				total += row.avg_points;
			}
		}
		avg_points.push(total);
	}

	return avg_points;
}

function after_datatable_render({ datamanager }) {
	const  { data } = datamanager;

	const wrapper = jQuery(`div[id="page-query-report"] div.chart-wrapper`)
		.show()
		.get(0)
		;

	return new frappe.Chart(wrapper, {
		// or DOM element
		data: {
		  labels: get_labels(data),
		  datasets: [
			{
			  name: "Monthly Total Pts",
			  chartType: "bar",
			  values: [25, 40, 30, 35]
			},
			{
			  name: "Issue Count",
			  chartType: "bar",
			  values: [25, 50, 10, 15]
			},
			{
			  name: "Avg Points",
			  chartType: "line",
			  values: [15, 20, 3, 15]
			}
		  ],
	  
		  yMarkers: [{ label: "Marker", value: 70, options: { labelPos: "left" } }],
		  yRegions: [
			{ label: "Region", start: 0, end: 50, options: { labelPos: "right" } }
		  ]
		},
	  
		title: "Monkey AVG Dashboard",
		type: "axis-mixed", // or 'bar', 'line', 'pie', 'percentage'
		height: 300,
		colors: ["purple", "#ffa3ef", "light-blue"],
		axisOptions: {
		  xAxisMode: "tick",
		  xIsSeries: true
		},
		barOptions: {
		  stacked: true,
		  spaceRatio: 0.5
		},
		tooltipOptions: {
		  formatTooltipX: (d) => (d + "").toUpperCase(),
		  formatTooltipY: (d) => d + " pts"
		}
	});
	
}

function get_chart_data(_, result) {
	const periods = get_labels(result);
	const datasets = new Array();

	datasets.push({
		"name": "Monthly Total Pts",
		"charType": "bar",
		"values": [get_total_points_by_period(result, periods)],
	})
	datasets.push({
		"name": "Issue Count",
		"charType": "bar",
		"values": [get_issue_count_by_period(result, periods)],
	})
	datasets.push({
		"name": "Avg Points",
		"charType": "line",
		"values": [get_avg_points_by_period(result, periods)],
	})

	return {
		"data": {"labels": periods, "datasets": datasets},
		// "type": "pie",
		"type": "axis-mixed",
		// "type": "percentage",
		axisOptions: {
			xAxisMode: "tick",
			xIsSeries: true
		  },
		  barOptions: {
			stacked: true,
			spaceRatio: 0.5
		  },
		  tooltipOptions: {
			formatTooltipX: (d) => (d + "").toUpperCase(),
			formatTooltipY: (d) => d + " pts"
		  }
	}
}