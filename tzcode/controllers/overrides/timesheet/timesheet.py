# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe


from frappe import utils

from erpnext.projects.doctype.timesheet import timesheet
from hrms.overrides import employee_timesheet

from tzcode.controllers.overrides import overrides

class InvalidUserError(Exception):
    pass

class Timesheet(
    employee_timesheet.EmployeeTimesheet, timesheet.Timesheet
):
    @overrides
    def validate(self):
        super().validate()
        self.auto_submit_if_completed()

    def auto_submit_if_completed(self):
        """If the Timesheet started yesterday and was completed today, let's submit it"""
        today = frappe.utils.today()

        if today == utils.cstr(
            self.start_date
        ):
            return # We don't want to submit today's timesheet

        for timesheet_detail in self.time_logs:
            if not timesheet_detail.to_time:
                return # We don't want to submit an incomplete timesheet

        if not self.flags.internal_submit:
            self.flags.internal_submit = True
            self.queue_action("submit")

            # submitting can cause a validation recursion error
            # so we need to do something to prevent it
            self.flags.internal_submit = False
        else:
            ...

    #     self.validate_employee()

    # def validate_employee(self):
    #     employee_id = get_employee_id(frappe.session.user)

    #     if not employee_id:
    #         frappe.throw("Employee not found for current user")

    #     if self.employee != employee_id:
    #         frappe.throw("You can only create timesheets for yourself")


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


    employee_id = get_employee_id(frappe.session.user)
    does_not_have_system_manager_role = (
        "System Manager" not in frappe.get_roles()
    )

    if employee_id and does_not_have_system_manager_role:
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