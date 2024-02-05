# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe

from hrms.hr.doctype.appraisal import appraisal

class Appraisal(appraisal.Appraisal):
    def before_insert(self):
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
