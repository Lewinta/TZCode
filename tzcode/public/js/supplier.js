frappe.ui.form.on("Supplier", {
    validate(frm){
        if(!frm.doc.commercial_name)
            frm.set_value("commercial_name", frm.doc.supplier_name);
    },
    tax_id(frm){
        if(!frm.doc.tax_id)
            return
        frm.set_value(
            "tax_id",
            frm.doc.tax_id.replace("-", "")
        )
    },

});