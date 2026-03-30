// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Interview', {

	refresh(frm) {
        console.log("Local Loaded")
        frm.trigger("add_custom_buttons");
    },

    add_custom_buttons(frm){
        frm.trigger("add_feedback_button");
    },

    add_feedback_button(frm){
		if (frm.doc.docstatus != 2 && !frm.doc.__islocal) {
			let allowed_interviewers = [];
			frm.doc.interview_details.forEach(values => {
				allowed_interviewers.push(values.interviewer);
			});

			if ((allowed_interviewers.includes(frappe.session.user))) {
				frappe.db.get_value('Interview Feedback', {'interviewer': frappe.session.user, 'interview': frm.doc.name, 'docstatus': 1}, 'name', (r) => {
					if (Object.keys(r).length === 0) {
                        frm.remove_custom_button(__('Submit Feedback'));
                        frm.add_custom_button(__('Submit Feedback'), function () {
							frappe.call({
								method: 'hrms.hr.doctype.interview.interview.get_expected_skill_set',
								args: {
									interview_round: frm.doc.interview_round
								},
								callback: function (r) {
									frm.events.show_feedback_dialog(frm, r.message);
									frm.refresh();
								}
							});
						}).addClass('btn-primary');
					}
				});
			}
		}
	},

	show_feedback_dialog: function (frm, data) {
		let fields = frm.events.get_fields_for_feedback();

		let d = new frappe.ui.Dialog({
			title: __('Submit Feedback'),
			fields: [
				{
					fieldname: 'skill_set',
					fieldtype: 'Table',
					label: __('Skill Assessment'),
					cannot_add_rows: false,
					in_editable_grid: true,
					reqd: 1,
					fields: fields,
					data: data
				},
				{
					fieldname: 'result',
					fieldtype: 'Select',
					options: ['', 'Cleared', 'Rejected'],
					label: __('Result'),
					reqd: 1,
				},
				{
					fieldname: 'feedback',
					fieldtype: 'Small Text',
					label: __('Feedback')
				}
			],
			size: 'extra-large',
			minimizable: true,
			static: true,
			primary_action: function(values) {
				frappe.call({
					method: 'hrms.hr.doctype.interview.interview.create_interview_feedback',
					args: {
						data: values,
						interview_name: frm.doc.name,
						interviewer: frappe.session.user,
						job_applicant: frm.doc.job_applicant
					}
				}).then(() => {
					frm.refresh();
				});
				d.hide();
			},
		});
		d.show();
		d.get_close_btn().show();
	},

	get_fields_for_feedback: function () {
		return [{
			fieldtype: 'Link',
			fieldname: 'skill',
			options: 'Skill',
			in_list_view: 1,
			columns: 3,
			label: __('Skill')
		}, {
            fieldtype: 'Rating',
			fieldname: 'rating',
			label: __('Rating'),
			in_list_view: 1,
			columns: 2,
			reqd: 1,
		},{
            fieldtype: 'Description',
			fieldname: 'description',
			label: __('Description'),
			in_list_view: 1,
			columns: 5,
			reqd: 1,
        }];
	},
});
