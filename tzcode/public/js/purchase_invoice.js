frappe.ui.form.on("Purchase Invoice", {
    refresh(frm) {
        const events = [
            "set_defaults", "set_queries", "add_custom_buttons",
        ]
        events.forEach(event => {
            frm.trigger(event);
        });
    },
    posting_date(frm) {
        frm.set_value("bill_date", frm.doc.posting_date)
    },
    set_defaults(frm) {
        if (!frm.is_new())
            return
        
        frm.set_value("cost_center", "Principal - TZ");
    },
    set_queries(frm){
        frm.set_query("supplier", () => {
            return {
                "query": "tzcode.queries.get_suppliers"
            }
        })
    },
    cost_center(frm){
        // OJO: antes decia `frm.doc.items + frm.doc.items`, que concatena los
        // arrays como string y no actualizaba nada. Hay que recorrer items Y taxes
        // y refrescar las grids para que el usuario vea el valor copiado.
        if (!frm.doc.cost_center) return;
        ["items", "taxes"].forEach(table => {
            (frm.doc[table] || []).forEach(row => {
                frappe.model.set_value(row.doctype, row.name, "cost_center", frm.doc.cost_center);
            });
            frm.refresh_field(table);
        });
    },
    add_custom_buttons(frm) {
        if (frm.doc.docstatus !== 1) return;

        if (!frappe.user.has_role("System Manager")) return;

        frm.add_custom_button(__("Update Cost Center"), () => {
            const current_cc = frm.doc.cost_center;

            const dialog = new frappe.ui.Dialog({
                title: __("Update Cost Center"),
                fields: [
                    {
                        fieldname: "new_cost_center",
                        label: __("New Cost Center"),
                        fieldtype: "Link",
                        options: "Cost Center",
                        default: "Operations - TZ",
                        reqd: 1
                    }
                ],
                primary_action_label: __("Update"),
                primary_action(values) {
                    if (!values.new_cost_center) {
                        frappe.msgprint(__("Please select a Cost Center"));
                        return;
                    }

                    if (values.new_cost_center === current_cc) {
                        frappe.msgprint({
                            title: __("No Change"),
                            message: __("The selected Cost Center is the same as the current one."),
                            indicator: "orange"
                        });
                        dialog.hide();
                        return;
                    }

                    frappe.call({
                        method: "tzcode.hook.purchase_invoice.update_cost_center",
                        args: {
                            purchase_invoice: frm.doc.name,
                            cost_center: values.new_cost_center
                        },
                        freeze: true,
                        freeze_message: __("Updating Cost Center and GL Entries…"),
                        callback(r) {
                            if (!r.exc) {
                                frappe.msgprint({
                                    title: __("Success"),
                                    message: __("Cost Center updated successfully."),
                                    indicator: "green"
                                });
                                dialog.hide();
                                frm.reload_doc();
                            }
                        }
                    });
                }
            });

            dialog.show();
        });
    }
})