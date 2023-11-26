frappe.ui.form.on("Payment Entry", {
    refresh(frm) {

    },
});

frappe.ui.form.on("Payment Entry Reference", {
    isr(frm, doctype, name) {
        const { deductions, references } = frm.doc;

        const doc = frappe.get_doc(doctype, name);

        if (!doc.isr) {
            return "Skip for empty isr_rate";
        }

        frm.call("get_retention_details", {
            reference_doctype: doc.reference_doctype,
            reference_name: doc.reference_name,
            retention_id: doc.isr,
        }).then(({ message }) => {


            const {
                account,
                amount,
                cost_center,
                retention_category,
                retention_description,
                retention_rate,
                retention_type,
            } = message;

            frappe.model.set_value(doctype, name, "isr_amount", amount);

            const deductions = frm.doc.deductions;
            const existing_deduction = deductions
                .find(deduction => deduction.account === account);

            if (existing_deduction) {
                // check to see if the is another row with the same retention_type
            }

            const deduction = {
                cost_center: cost_center,
                amount: amount,
                description: retention_description,
            };
            const exists = deductions.some(item =>
                item.cost_center === deduction.cost_center &&
                item.description === deduction.description
            );
            if (exists) {
                deductions.filter(item =>
                    item.cost_center === deduction.cost_center &&
                    item.description === deduction.description

                ).map((item) => {
                    const doc = frappe.get_doc(item.doctype, item.name)
                    const index = deductions.indexOf(doc)
                    deductions.splice(index, 1)
                })

                deductions.map((item, index) => {
                    item.idx = index + 1
                })
            }
            frm.add_child("deductions", {
                "account": account,
                "cost_center": cost_center,
                "amount": -1 * amount,
                "description": retention_description,
            });
            frm.refresh_field("deductions");
        });


    },
});