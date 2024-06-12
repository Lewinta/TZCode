// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt
{
	function refresh(frm) {
		set_intro(frm);
	}

	function set_intro(frm) {
		if (
			frm.is_new()
		) {
			frm.set_intro();
			frm.set_intro(__("The template will be rendered only once... so, make sure you include all your variables prior saving the document"));
		}
	}

	function notification_template(frm) {
		frappe.show_alert({
			indicator: "blue",
			message: __("Please save the document to render the template!"),
		});
	}

	function re_render_template(frm) {
		frm.call("render_template", {
			from_template: 1,
		}).then(response => {
			frappe.show_alert({
				indicator: "green",
				message: __("Template rendered successfully!"),
			});

			frm.dirty();
		}).catch(error => {
			frappe.show_alert({
				indicator: "red",
				message: __("An error occurred while rendering the template!"),
			});
		});
	}

	frappe.ui.form.on("Employee Notification", {
		refresh,
		re_render_template, // in-form button
		notification_template,
	});
}