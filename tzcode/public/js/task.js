frappe.ui.form.on("Task", {
    is_group(frm) {
        frm.trigger("req_color");
    },
    color(frm) {
        frm.trigger("req_color");
    },
    req_color(frm) {
        frm.set_df_property("color", "reqd", !!frm.doc.is_group)
    }

})