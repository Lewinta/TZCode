frappe.ui.form.on("Purchase Invoice", {
    refresh(frm) {
        frm.trigger("set_defaults");
    },
    posting_date(frm) {
        frm.set_value("bill_date", frm.doc.posting_date)
    },
    set_defaults(frm) {
        if (!frm.is_new())
            return
        
        frm.set_value("cost_center", "Principal - TZ");
    }
})