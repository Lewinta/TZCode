// Copyright (c) 2022, Lewin Villar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Upwork Payment Breakdown', {
	currency(frm){
		if(frm.doc.currency == "DOP")
			frm.set_value("exchange_rate", 1);
	},
	paid_amount(frm){
		frm.trigger("make_calculations");
	},
	exchange_rate(frm){
		frm.trigger("make_calculations");
	},
	upwork_rate(frm){
		const {paid_amount, upwork_rate, exchange_rate} = frm.doc;
		const rate = upwork_rate / 100.00;
		frm.set_value("upwork_fee", paid_amount * rate);
		frm.set_value("base_upwork_fee", paid_amount * rate * exchange_rate);
	},
	withdrawal_fee(frm){
		const {exchange_rate, withdrawal_fee} = frm.doc;
		frm.set_value("base_withdrawal_fee", withdrawal_fee * exchange_rate);
	},
	bank_fee(frm){
		const {exchange_rate, bank_fee} = frm.doc;
		frm.set_value("base_bank_fee", bank_fee * exchange_rate);
	},
	make_calculations(frm){
		frm.trigger("upwork_rate");
		frm.trigger("withdrawal_fee");
		frm.trigger("bank_fee");
		const {
			paid_amount,
			upwork_fee,
			withdrawal_fee,
			bank_fee,
			exchange_rate
		} = frm.doc;
		const received_amount = paid_amount - upwork_fee - withdrawal_fee - bank_fee;
		frm.set_value("base_paid_amount", paid_amount * exchange_rate);
		frm.set_value("received_amount", received_amount);
		frm.set_value("base_received_amount", received_amount * exchange_rate);
		

	},
	

});
