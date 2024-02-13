frappe.ui.form.on("Payroll Entry", {
    refresh(frm){
        $.map(
            ["set_queries", "add_custom_buttons"],
            event => frm.trigger(event)
        )
    },
    validate(frm){
        if(!frm.is_new())
            return
        if (!!frm.doc.employee && frm.doc.employee.length > 1)
            return
        // frm.events.get_employee_details(frm);
    },
    set_queries(frm){
        frm.set_query("bank_account", function() {
            return {
                filters: {
                    "is_company_account": 1,
                    "account": frm.doc.payment_account
                }
            }
        });
    },
    add_custom_buttons(frm){
        frm.trigger('salary_register_btn');
        frm.trigger('update_salary_slips');
    },
    salary_register_btn(frm){
        if(frm.doc.docstatus != 1)
            return 
        
        frm.add_custom_button("Salary Register", () => {
            frappe.set_route('query-report', 'Salary Register', {
                'from_date': frm.doc.start_date,
                'to_date': frm.doc.end_date,
                'docstatus': frm.doc.salary_slips_submitted ? 'Submitted' : 'Draft' 
            });
        })
    },
    update_salary_slips(frm){
        if(!!frm.doc.salary_slips_submitted)
            return 
        frm.add_custom_button("Update Slips", () => {
            let freeze_message = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden"></span>
                </div>`;
            let opts = {
                method: "tzcode.controllers.overrides.payroll_entry.update_salary_slips",
                args: {name: frm.docname},
                freeze: true,
                freeze_message: freeze_message
            }
            frappe.call(opts).then( () => {
                frappe.utils.play_sound('submit');
                frappe.show_alert({
                    "message": "Salary Slips Updated Successfully",
                    "indicator": "green"
                })
            });
        });
    }
})