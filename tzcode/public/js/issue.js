frappe.ui.form.on("Issue", {
    setup(frm) {
        const style = document.createElement("style")
        style.innerHTML = `
            #page-Issue div[data-label=${__("Create")}],
            #page-Issue button[data-label=${__("Close")}],
            #page-Issue button[data-label=${__("Reopen")}]
            { display: none; }
        `
        document.head.appendChild(style)
    },
    refresh(frm) {
        frm.trigger("render_go_to_client_system_btn");
    },
    render_go_to_client_system_btn(frm) {
        const { doc, fields_dict } = frm;

        if (doc.remote_reference) {
            const { wrapper } = fields_dict.remote_reference;
            jQuery(wrapper).find("button.btn-default").remove();
            jQuery("<button class='btn btn-default btn-xs'>Go to Client System</button>")
                .click(() => {
                    window.open(`${doc.remote_reference}/login`, "_blank");
                })
                .appendTo(wrapper);
        }
    },
})