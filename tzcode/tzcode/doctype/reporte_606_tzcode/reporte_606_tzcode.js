// Copyright (c) 2023, Lewin Villar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Reporte 606 Tzcode', {
	onload: function (frm) {
		frm.set_value("from_date", frappe.datetime.month_start());
		frm.set_value("to_date", frappe.datetime.month_end());
		frm.disable_save();
	},
	run_report: function (frm) {
		var file_url = __("/api/method/tzcode.tzcode.doctype.reporte_606_tzcode.reporte_606_tzcode.get_file_address?from_date={0}&to_date={1}",
			[frm.doc.from_date, frm.doc.to_date]);

		window.open(file_url);
	}
});
