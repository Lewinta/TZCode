import frappe

@frappe.whitelist()
def update_salary_slips(name):
    SS = frappe.qb.DocType("Salary Slip")

    slips = frappe.qb.from_(SS).select(SS.name).where(
        SS.payroll_entry == name
    ).run()

    for name, in slips:
        salary_slip = frappe.get_doc("Salary Slip", name)
        remove_cancelled_components(salary_slip)
        if salary_slip.docstatus == 0:
            salary_slip.save()
    
    return True

def remove_cancelled_components(salary_slip):
    for d in salary_slip.earnings + salary_slip.deductions:
        if not d.additional_salary:
            continue
        if frappe.db.get_value("Additional Salary", d.additional_salary, "docstatus") == 2:
            print(f"Removing cancelled component {d.additional_salary} from {salary_slip.name}")
            salary_slip.remove(d)
    salary_slip.calculate_net_pay()
    return True