// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

{
	function refresh(frm) {
		add_custom_buttons(frm);
	}

	function add_custom_buttons(frm) {
		if (frm.is_new()) {
			// todo:
			// add buttons for new documents
		} else {
			add_create_issue(frm);
			add_update_issue(frm);

			// not a custom button, but this logic
			// fits better here
			mark_group_as_primary(frm);
		}
	}

	function add_create_issue(frm) {
		const label = __("Create Issue");
		const group = __("Actions");

		function callback(_) {
			do_call_to_create_issue(frm);
		}

		frm.add_custom_button(label, callback, group);
	}

	function add_update_issue(frm) {
		const label = __("Update Issue");
		const group = __("Actions");

		function callback(_) {
			do_call_to_update_issue(frm);
		}

		frm.add_custom_button(label, callback, group);
	}


	function mark_group_as_primary(frm) {
		const group = __("Actions");
		frm.page.set_inner_btn_group_as_primary(group);
	}

	function do_call_to_create_issue(frm) {
		frm.call("create_issue", {
			auto_commit: true,
		})
			.then((response) => {
				frappe.show_alert({
					message: __("Issue created successfully"),
					indicator: "green",
				});
			})
			.catch((error) => {
				frappe.show_alert({
					message: __("Error creating issue"),
					indicator: "red",
				});
			});
	}

	function do_call_to_update_issue(frm) {
		frm.call("update_issue", {
			auto_commit: true,
		})
			.then((response) => {
				frappe.show_alert({
					message: __("Issue updated successfully"),
					indicator: "green",
				});
			})
			.catch((error) => {
				frappe.show_alert({
					message: __("Error updating issue"),
					indicator: "red",
				});
			});
	}

	frappe.ui.form.on("Bulk Issue", {
		refresh,
	});
}
