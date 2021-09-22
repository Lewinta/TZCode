frappe.ui.form.on("Issue", {
    refresh(frm){
        frm.remove_custom_button("Close")
    }
})