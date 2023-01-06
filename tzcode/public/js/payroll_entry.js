frappe.ui.form.on("Payroll Entry", {
    refresh(frm){
        frm.trigger("set_queries");
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
    }
})