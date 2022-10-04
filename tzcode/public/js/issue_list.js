frappe.listview_settings['Issue'] = {
	onload: function (listview) {
		const { page } = listview;

		const { workflow_state } = page.fields_dict;

		if (!workflow_state) {
			return "Not a workflow state";
		}

		workflow_state.get_query = function () {
			// valid states
			const states = [
				"Open",
				"On Hold",
				"Working",
				"Closed",
				"Overdue",
			];

			if (frappe.user.has_role("Support Manager")) {
				// states.push("Pending");
				states.push("Assigned");
			}

			const filters = {
				name: ["in", states],
			};

			return { filters };
		};
	},
	filters: [
		["Issue", "_assign", "like", `%${frappe.session.user}%`],
		["Issue", "workflow_state", "in", ["Open", "Working"]],
	],
}