frappe.ui.form.on("Payroll Entry", {
    validate(frm){
        if(!frm.is_new())
            return
        if (frm.doc.employee)
            return
        // frm.events.get_employee_details(frm);
    }
})