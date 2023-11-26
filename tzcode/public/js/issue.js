{
    function setup(_) {
        _hide_erpnext_buttons()
    }
    
    function refresh(frm) {
        _render_go_to_client_system_btn(frm)
        _add_privileged_custom_buttons(frm)
    }

    function _hide_erpnext_buttons() {
        const style = document.createElement("style")
        style.innerHTML = `
            #page-Issue div[data-label=${__("Create")}],
            #page-Issue button[data-label=${__("Close")}],
            #page-Issue button[data-label=${__("Reopen")}]
            { display: none; }
        `
        document.head.appendChild(style)
    }
    
    function _add_privileged_custom_buttons(frm) {
        // this is only for Support Manager... for now!
        const privileged_roles = [
            "Support Manager",
            "System Manager",
        ]

        if (!frappe.user.has_role(privileged_roles)) {
            return "Not a privileged user"
        }

        _add_remove_remote_reference_btn(frm)
    }
    
    function _render_go_to_client_system_btn(frm) {
        const { doc, fields_dict } = frm

        if (doc.host_url) {
            const { wrapper } = fields_dict.host_url
            jQuery(wrapper).find("button.btn-default").remove()
            jQuery("<button class='btn btn-default btn-xs'>Go to Client System</button>")
                .click(() => {
                    window.open(`${doc.host_url}/login`, "_blank")
                })
                .appendTo(wrapper)
        }
    }

    function _add_remove_remote_reference_btn(frm) {
        const { doc } = frm

        const allowed_states = [
            "Pending",
            "Ack",
            "Ready for Development",
        ]

        if (
            doc.remote_reference
            && allowed_states.includes(doc.workflow_state)
        ) {
            const label = "Remove Remote Reference"
            const action = _on_remove_remote_reference.bind(null, frm)
            frm.add_custom_button(label, action)
        }
    }

    function _on_remove_remote_reference(frm) {
        const { doc } = frm

        frappe.confirm(
            __("Are you sure you want to remove the remote reference?"),
            () => {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Issue",
                        name: doc.name,
                        fieldname: "remote_reference",
                        value: "",
                    },
                    callback: () => {
                        frm.reload_doc()
                    },
                })
            }
        )
    }

    frappe.ui.form.on("Issue", {
        setup,
        refresh, 
    })
}