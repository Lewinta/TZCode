# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe

class InvalidUserError(Exception):
    pass


def get_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user

    if not user:
        raise InvalidUserError("User not provided")

    if user == "Administrator":
        return ""


    # only last 3 months
    conditions = [
        f"tabTimesheet.start_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
    ]

    if employee_id := get_employee_id(frappe.session.user) \
        and "System Manager" not in frappe.get_roles():
        conditions.append(f"""
            tabTimesheet.employee = {employee_id!r}
        """)

    return f"({' AND '.join(conditions)})"


def get_employee_id(user):
    doctype = "Employee"
    filters = {
        "user_id": user,
        "status": "Active",
    }

    fieldname = "name"

    return frappe.get_value(doctype, filters, fieldname) 