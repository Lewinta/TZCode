{
	const filters = [
		[
			"Issue",
			"workflow_state",
			"in", [
				"Pending",
				"Ack",
				"Working",
				"On Hold",
				"Ready for QA",
				"Ready for Development",
				"Code Quality Passed",
				"Code Quality Rejected",
				// "Completed",
			]
		],
	]

	if (!frappe.user.has_role("Support Manager")) {
		filters.push(["Issue", "_assign", "like", `%${frappe.session.user}%`])
	}

	function onload(listview) {
		const { page } = listview

		const { workflow_state } = page.fields_dict

		if (!workflow_state) {
			return "Not a workflow state"
		}

		workflow_state.get_query = function () {
			// valid states
			const states = [
				"Pending",
				"Ack",
				"Ready for Development",
				"Working",
				"On Hold",
				"Ready for QA",
				"Code Quality Passed",
				"Code Quality Rejected",
				"Duplicated",
				"Forgotten",
			]

			if (frappe.user.has_role("Support Manager")) {
				states.push("Completed")
			}

			const filters = {
				name: ["in", states],
			}

			return { filters }
		};

		listview.page.add_button("Reset", function(event) {
			listview.filter_area.clear()
			listview.filter_area.set(filters)
		}, {
			icon: "filter",
			btn_class: "btn-link",
		})
			.attr("title", "Resets all the filters") // add tooltip text
			.attr("data-toggle", "tooltip") // enable tooltip
			.attr("data-placement", "bottom") // place the tooltip on top of the item
			.tooltip()
		;
	}

	function on_update(listview) {
		console.log("Do something on update")
	}


	function get_indicator(doc) {
		const is_delayed = doc.due_date && doc.due_date < frappe.datetime.now_date();

		const indicator = {
			"Pending": "red",
			"Ack": "orange",
			"Ready for Development": is_delayed ? "red" : "orange",
			"Working": is_delayed ? "red" : "yellow",
			"Ready for QA": is_delayed ? "red" : "yellow",
			"On Hold": "red",
			"Code Quality Passed": "blue",
			"Code Quality Rejected": is_delayed ? "red" : "yellow",
			"Completed": "green",
			"Duplicated": "gray",
			"Forgotten": "gray",
		}[doc.workflow_state]

		let state = ": On Time"
		if (is_delayed) {
			state = ": Delayed"
		}

		const non_expirables = [
			"On Hold",
			"Forgotten",
			"Duplicated",
			"Code Quality Passed",
			"Completed",
		]

		let _state = doc.workflow_state;

		// let's get fancy here...
		// 💢💦💤💨💫🆘❇️🕢🈂️㊙️🍨
		if (doc.workflow_state === "Code Quality Passed") {
			_state = "👍 Code Quality Passed"
		} else if (doc.workflow_state === "Code Quality Rejected") {
			_state = "💫 Code Quality Rejected"
		} else if (doc.workflow_state === "Ready for QA") {
			_state = "🎉 Ready for QA"
		} else if (doc.workflow_state === "Ready for Development") {
			_state = "✨ Ready for Development"
		} else if (doc.workflow_state === "On Hold") {
			_state = "🚫 On Hold"
		} else if (doc.workflow_state === "Working") {
			_state = "🪄 Working"
		} else if (doc.workflow_state === "Ack") {
			_state = "📝 Ack"
		} else if (doc.workflow_state === "Pending") {
			_state = "🆕 Pending"
		} else if (doc.workflow_state === "Completed") {
			_state = "✅ Completed"
		} else if (doc.workflow_state === "Duplicated") {
			_state = "💢 Duplicated"
		} else if (doc.workflow_state === "Forgotten") {
			_state = "💤 Forgotten"
		}

		if (
			!doc.due_date
			|| non_expirables.includes(doc.workflow_state)
		) {
			state = ""
		} else {
			if (is_delayed) {
				_state = `🕢 ${_state}`
			}
		}

		return [`${_state}${state}`, indicator, "workflow_state,=," + doc.workflow_state]
	}

	frappe.listview_settings["Issue"] = {
		onload,
		on_update,
		filters,
		get_indicator,
		// hide_name_column: 1,
		colwidths: { "subject": 6 },
		add_fields: ["priority", "workflow_state", "due_date"],
	}
}