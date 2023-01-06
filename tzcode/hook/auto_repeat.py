import frappe

def validate(doc, method):
    obj = {
        "Sales Order": "customer_name",
        "Sales Invoice": "customer_name",
        "Purchase Order": "supplier_name",
        "Purchase Invoice": "supplier_name",
        "ToDo": "description",
    }

    doc.custom_title = frappe.get_value(
        doc.reference_doctype,
        doc.reference_document,
        obj[doc.reference_doctype],
    ) or "-"