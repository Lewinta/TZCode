frappe.ui.form.on("ToDo", {
    refresh(frm) {
        frm.remove_custom_button("Close");
        frm.remove_custom_button("New");
    }
})