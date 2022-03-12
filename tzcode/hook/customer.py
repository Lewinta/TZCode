import frappe
def on_update(doc, method):
    frappe.db.sql("""
        UPDATE
            `tabCloud Server Host`
        JOIN
            `tabCustomer`
        ON
            `tabCloud Server Host`.customer = `tabCustomer`.name
        SET 
            `tabCloud Server Host`.monthly_bill = `tabCustomer`.monthly_bill,
            `tabCloud Server Host`.base_monthly_bill = `tabCustomer`.base_monthly_bill,
            `tabCloud Server Host`.disabled = `tabCustomer`.disabled
        WHERE
            `tabCloud Server Host`.customer = %s
    """, doc.name)
    
    filters = {"customer": doc.name}
    servers = frappe.get_list("Cloud Server Host", filters, "parent", as_list=True)
    for name, in servers:
        srv = frappe.get_doc("Cloud Server", name)
        srv.save(ignore_permissions=True)

        