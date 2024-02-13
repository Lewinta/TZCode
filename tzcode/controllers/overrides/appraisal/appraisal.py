# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe

from hrms.hr.doctype.appraisal import appraisal

class Appraisal(appraisal.Appraisal):
    def before_insert(self):
        self.validate_is_created_from_cycle()

    def validate_is_created_from_cycle(self):
        if self.amended_from:
            return # skip validation if this document is an amendment

        if not self.from_appraisal_cycle:
            frappe.throw(
                "<p>I don't think you should create this document manually.</p>"
                "<p>Please use the Appraisal Cycle document to create this document.</p>"
            )

    def onload(self):
        self.load_additional_salary_if_exists()

    @frappe.whitelist()
    def create_additional_salary(self, amount, payroll_date, salary_component, employee=None):
        """Creates a new Additional Salary document"""
        doc = frappe.new_doc("Additional Salary")

        doc.update({
            "employee": self.employee,
            "employee_name": self.employee_name,
            "salary_component": salary_component,
            "amount": amount,
            "payroll_date": payroll_date,
            "company": self.company,
            "ref_doctype": self.doctype,
            "ref_docname": self.name,
        })

        self.validate_salary_component_type(salary_component)

        doc.type = "Earning"
        doc.currency = "DOP"
        doc.is_recurring = False

        # doc.deduct_full_tax_on_selected_payroll_date = False
        doc.overwrite_salary_structure_amount = True
        doc.save(ignore_permissions=True)

        return doc.name

    def validate_salary_component_type(self, salary_component):
        doc = self.get_salary_component(salary_component)

        if doc.type != "Earning":
            frappe.throw("Salary Component must be of type Earning")

    def get_salary_component(self, name):
        doctype = "Salary Component"
        return frappe.get_doc(doctype, name)

    def load_additional_salary_if_exists(self):
        doctype = "Additional Salary"
        filters = {
            "ref_doctype": self.doctype,
            "ref_docname": self.name,
            "docstatus": ["!=", "2"],
        }

        db_exists = frappe.db.exists(doctype, filters)
        if db_exists:
            self.set_onload("additional_salary", db_exists)


@frappe.whitelist()
def get_amount_from_additional_salaries(appraisal):
    # get other additional salaries within the same period (month)
    employee_details = get_appraisal_reference_details(appraisal)
    variable = get_variable_for_employee(employee_details.employee)

    if not variable:
        print(f"Employee {employee_details.employee} has no variable")
        return 0

    avg_total_score = get_avg_total_score_for_employee(
        employee_details.employee, employee_details.month
    )

    if not avg_total_score:
        print(f"Employee {employee_details.employee} has no avg_total_score")
        return 0

    return avg_total_score * variable


def get_avg_total_score_for_employee(employee, period):
    out = frappe.db.sql(
        """
            Select
                Avg(total_score / 5) As total_score
            From
                `tabAppraisal`
            Where
                employee = %(employee)s
                And Concat_Ws(
                    "-",
                    Year(start_date),
                    Month(start_date)
                ) = %(period)s
        """, {
            "employee": employee,
            "period": period,
        }
    )

    if not out:
        print(f"No appraisal found for employee {employee} in period {period}")
        return 0

    return out[0][0]


def get_appraisal_reference_details(name):
    """We need to return:
        - employee
        - employee_name
        - department
        - designation
        - month and year (based on the start_date)
    """

    out = frappe.db.sql(
        """
            Select
                employee,
                employee_name,
                department,
                designation,
                Concat_Ws(
                    "-",
                    Year(start_date),
                    Month(start_date)
                ) As month
            From
                `tabAppraisal`
            Where
                name = %(name)s
        """, {
            "name": name,
        }, as_dict=True
    )

    if not out:
        frappe.throw(f"No appraisal found with the given name {name!r}")

    return out[0]


def get_variable_for_employee(employee):
    doctype = "Salary Structure Assignment"

    filters = {
        "employee": employee,
        "docstatus": 1,
    }

    field = "variable"

    return frappe.db.get_value(doctype, filters, field)
