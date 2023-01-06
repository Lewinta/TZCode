import frappe

@frappe.whitelist()
def get_suppliers(doctype, txt, searchfield, start, page_len, filters):
    Supplier = frappe.qb.DocType("Supplier")
    return frappe.qb.from_(Supplier).select(
        Supplier.name,
        Supplier.commercial_name,
        Supplier.tax_id
    ).where(
        (Supplier.disabled == 0)&
        (Supplier.name.like(f"%{txt}%"))|
        (Supplier.commercial_name.like(f"%{txt}%"))|
        (Supplier.tax_id.like(f"%{txt}%"))
    ).run()