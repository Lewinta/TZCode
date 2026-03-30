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
    @property
    def is_properly_completed(self):
        return all(
            [
                timesheet_detail.to_time
                for timesheet_detail in self.time_logs
            ]
        )

    @overrides
    def validate(self):
        super().validate()
        self.validate_if_against_valid_issue()
        self.auto_submit_if_completed()

    def on_update(self):
        self.ensure_only_timelog_opened()

    def validate_if_against_valid_issue(self):
        def get_timesheet_detail():
            for time_log in self.time_logs:
                if time_log.name not in [log.name for log in db_doc.time_logs]:
                    return time_log
            return None

        def get_issue_state(issue_id):
            doctype = "Issue"
            name = issue_id
            fieldname = "workflow_state"

            return frappe.get_value(doctype, name, fieldname)

        if db_doc := self.get_doc_before_save():
            if not len(self.time_logs) > len(db_doc.time_logs):
                return

            # let's get the one that was just added
            timesheet_detail = get_timesheet_detail()

            if not timesheet_detail:
                return

            if not timesheet_detail.issue:
                return

            issue_state = get_issue_state(timesheet_detail.issue)

            if issue_state not in self.get_valid_issue_states() \
                and "Support Manager" not in frappe.get_roles():
                frappe.throw(
                    f"""
                        The Issue {timesheet_detail.issue} is in a state that doesn't allow you to log time against it.
                        Please check the Issue's state and try again.
                    """
                )
        else:
            if self.is_new():
                for time_log in self.time_logs:
                    if time_log.issue:
                        issue_state = get_issue_state(time_log.issue)

                        if issue_state not in self.get_valid_issue_states() \
                            and "Support Manager" not in frappe.get_roles():
                            frappe.throw(
                                f"""
                                    The Issue {time_log.issue} is in a state that doesn't allow you to log time against it.
                                    Please change the Issue's state and try again. Allowed states are:
                                    {frappe.utils.comma_and([d for d in self.get_valid_issue_states()])}
                                """
                            )
            else:
                frappe.throw("Couldn't find the previous version of the document")

        # hook to this event for further integrations
        self.run_method("timer_validated")

    @staticmethod
    def get_valid_issue_states():
        tz_settings = frappe.get_single("Tz Settings")

        if tz_settings.disable_validation_for_issue_states:
            return tz_settings.get_issue_workflow_states()

        return tz_settings.get_valid_issue_states()

    def auto_submit_if_completed(self):
        """If the Timesheet started yesterday and was completed today, let's submit it"""
        today = frappe.utils.today()

        if today == utils.cstr(
            self.start_date
        ):
            return # We don't want to submit today's timesheet

        if getattr(self, "dont_auto_submit", False):
            return

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

    def ensure_only_timelog_opened(self):
        """Ensure that only one timelog is open at a time"""
        
        counter = 0

        for name in frappe.db.sql_list(
            f"""
                Select
                    timesheet.name
                From
                    `tabTimesheet` As timesheet
                Where
                    timesheet.employee = {self.employee!r}
                    And timesheet.docstatus = 0
            """
        ):
            doc = self.load_timesheet(name)

            out = [
                timesheet_detail.to_time
                for timesheet_detail in doc.time_logs
                if not timesheet_detail.to_time
            ]

            counter += len(out)

        if counter > 1:
            frappe.throw(
                f"""
                    You can only have one timelog open at a time. We found {counter} open timelogs.
                    Please close the other timelogs before opening a new one.
                """
            )

    def load_timesheet(self, name):
        doctype = "Timesheet"
        return frappe.get_doc(doctype, name)

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