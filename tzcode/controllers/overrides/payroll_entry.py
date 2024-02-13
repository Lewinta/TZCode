import frappe

@frappe.whitelist()
def update_salary_slips(name):
    SS = frappe.qb.DocType("Salary Slip")

    slips = frappe.qb.from_(SS).select(SS.name).where(
        SS.payroll_entry == name
    ).run()

    for name, in slips:
        salary_slip = frappe.get_doc("Salary Slip", name)
        if salary_slip.docstatus == 0:
            salary_slip.save()
    
    return True