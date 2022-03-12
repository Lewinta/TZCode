frappe.ui.form.on("ToDo", {
    refresh(frm) {
        console.log("loaded")
        frm.remove_custom_button("Close");
        frm.remove_custom_button("New");
    }
})