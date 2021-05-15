import frappe

def on_cancel(doc, method):
    cancel_gl_entries(doc)

def on_trash(doc, method):
    delete_gl_entries(doc)

def cancel_gl_entries(doc):
    filters = {
        "voucher_type": doc.doctype,
        "voucher_no": doc.name,
    }
    for name, in frappe.get_list("GL Entry", filters, as_list=True):
        gl = frappe.get_doc("GL Entry", name)  
        if gl.docstatus == 1:
            gl.cancel = 2
            gl.save(ignore_permissions=True)

def delete_gl_entries(doc):
    filters = {
        "voucher_type": doc.doctype,
        "voucher_no": doc.name,
    }
    for name, in frappe.get_list("GL Entry", filters, as_list=True):
        gl = frappe.get_doc("GL Entry", name)
        if gl.docstatus == 1:
            gl.cancel()
        gl.delete(ignore_permissions=True)