frappe.ui.form.on("Appraisal", {
    refresh(frm) {
        frm.trigger("set_custom_buttons");
    },
    set_custom_buttons(frm) {
        // if (frm.doc.docstatus != 1)
        //     return;
        
        // Los incentivos se pagaran el dia 15 del mes siguiente
        const next_month = frappe.datetime.add_months(frm.doc.start_date, 1);
        const payroll_date = frappe.datetime.add_days(next_month, 14);
        const title = __("Create Additional Salary");
        const fields = [
            {
                fieldtype: "Link",
                fieldname: "employee",
                label: __("Employee"),
                options: "Employee",
                reqd: 1,
                read_only: 1,
                default: frm.doc.employee
            },
            {
                fieldtype: "Currency",
                fieldname: "amount",
                label: __("Amount"),
                reqd: 1,
                read_only: 1,
            },
            {
                fieldtype: "Column Break",
            },
            {
                fieldtype: "Date",
                fieldname: "payroll_date",
                label: __("Payroll Date"),
                reqd: 1,
                default: payroll_date
            },
            {
                fieldtype: "Link",
                fieldname: "salary_component",
                label: __("Salary Component"),
                options: "Salary Component",
                reqd: 1,
                default: "Incentivos"
            },
        ];

        if (frm.doc.__onload && frm.doc.__onload.additional_salary) {
            frm.add_custom_button(__("View Additional Salary"), function() {
                frappe.set_route("Form", "Additional Salary", frm.doc.__onload.additional_salary);
            });
        } else {
            let btn = frm.add_custom_button(__("Create Additional Salary"), function() {
                // frappe.db.get_value(
                //     "Salary Structure Assignment",
                //     {"employee": frm.doc.employee, "docstatus": 1},
                //     "variable"
                // ).then(({message}) => {
                //     let dialog = new frappe.ui.Dialog({
                //         title,
                //         fields,
                //         primary_action_label: __("Create"),
                //         primary_action(values) {
                //             const method = "create_additional_salary";
                //             frm.call(method, values)
                //                 .then(({ message: name }) => {
                //                     // get name of newly created doc and redirect to it
                //                     frappe.set_route("Form", "Additional Salary", name);
                //                 });
                //         }
                //     })

                //     const amount = flt(frm.doc.total_score) / 5.0 * flt(message.variable);
                //     dialog.set_value("amount", amount);  
                //     dialog.show();
                // })

                const method = "tzcode.controllers.overrides.appraisal.get_amount_from_additional_salaries";
                const args = { "appraisal": frm.doc.name };
                frappe.call(method, args)
                    .then(({ message: amount }) => {
                        const dialog = new frappe.ui.Dialog({
                            title,
                            fields,
                            primary_action_label: __("Create"),
                            primary_action(values) {
                                const method = "create_additional_salary";
                                frm.call(method, values)
                                    .then(({ message: name }) => {
                                        // get name of newly created doc and redirect to it
                                        frappe.set_route("Form", "Additional Salary", name);
                                    });
                            }
                        });

                        dialog.set_value("amount", amount);  
                        dialog.show();
                    });
            });

            btn.addClass("btn-primary");
        }
    }
});

frappe.ui.form.on("Appraisal Goal", {
    earned(frm, doctype, name) {
        const doc = frappe.get_doc(doctype, name);

        // score goes from 0-5
        // TzCode Policy says it should be all or nothing
        // 5 or 0, hence the checkbox to automate this
        let score = 0;
        if (doc.earned) {
            score = 5;
        }

        const fieldname = "score";
        frappe.model
            .set_value(doctype, name, fieldname, score);
    }
});