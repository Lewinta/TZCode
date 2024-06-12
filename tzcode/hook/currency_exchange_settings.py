import frappe

def validate(doc, method):
    if not doc.disabled:
        frappe.throw("You can not disable this document, is intended to be like this to prevent incurring on charges")