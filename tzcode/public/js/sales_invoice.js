frappe.ui.form.on('Sales Invoice', {
    refresh(frm){
        frm.trigger('add_custom_buttons');
    },
    add_custom_buttons(frm){
        frm.add_custom_button(__("Email Invoice"), function(){
            const fields = [
                {
                    fieldname: "email",
                    fieldtype: "Data",
                    label: __("Email"),
                    reqd: true,
                    default: frm.doc.contact_email
                }
            ]
            const _callback = function(data){
                frappe.call({
                    method: "tzcode.hook.sales_invoice.email_invoice",
                    args: {
                        docname: frm.doc.name,
                        email: data.email
                    },
                    callback: function(r){
                        if(r.message){
                            frappe.show_alert({
                                message: __("Email sent successfully"),
                                indicator: "green",
                            });
                        }
                    }
                });
            }
            frappe.prompt(fields, _callback, "Send Email", "Send");
           
        });
    }
});