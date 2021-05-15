// Copyright (c) 2021, Lewin Villar and contributors
// For license information, please see license.txt

frappe.ui.form.on('PM Visit', {
	validate(frm) {
		frm.trigger("validate_time");
		frm.trigger("calculate_time");
	},
	validate_time(frm) {
		if (frm.doc.arrival > frm.doc.leave)
			frappe.throw(__("Arrival must be before Leave"))
	},
	calculate_time(frm) {
		let dt1 = new Date(`${frm.doc.date} ${frm.doc.arrival}`); 
		let dt2 = new Date(`${frm.doc.date} ${frm.doc.leave}`); 
		var diff = (dt1.getTime() - dt2.getTime()) / 1000;
		frm.set_value("total_time", Math.abs(Math.round(diff)));
	}
});
