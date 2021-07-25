import frappe
from frappe.utils import flt

def get_employee_salary(emp):
    # Return monthly base salary for an employee
    result = frappe.db.sql("""
        SELECT 
            ssa.base,
            sa.payroll_frequency
        FROM 
            `tabSalary Structure Assignment` ssa
        JOIN
            `tabSalary Structure` sa
        ON
            ssa.salary_structure = sa.name
        WHERE
            ssa.employee = %s
        Order by 
            ssa.creation desc
        LIMIT 1
    """, emp, as_dict=True)
    if not result:
        return 0
    
    salary = result[0]

    factor_obj = {
        "Monthly": 1.0,
        "Bimonthly": 2.0,
        "Fortnightly": 13.0 / 6.0, #26/12
        "Weekly": 52.0,
        "Daily": 365.25,
    }

    return flt(salary.base) *  factor_obj[salary.payroll_frequency]