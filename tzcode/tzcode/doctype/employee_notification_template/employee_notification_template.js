// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt

{
	function refresh(frm) {
		add_fetches(frm);
	}
	function add_fetches(frm) {
		add_notification_type_fetch(frm);
	}

	function add_notification_type_fetch(frm) {
		const link = "notification_type";
		const source = "requires_acknowledgment";
		const target = "requires_acknowledgment";
		frm.add_fetch(link, source, target);
	}

	frappe.ui.form.on("Employee Notification Template", {
		refresh,
	});
}
