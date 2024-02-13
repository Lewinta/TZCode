// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

{
	// form events
	function refresh(frm) {
		add_custom_buttons(frm);
	}


	// utils
	function add_custom_buttons(frm) {
	}

	frappe.ui.form.on("Additional Salary", {
		refresh,
	});
}