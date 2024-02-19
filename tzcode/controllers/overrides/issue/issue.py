# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import json
import frappe

from frappe.model.document import Document
from frappe.desk.form.assign_to import add as do_assignation
from frappe.utils import now_datetime, nowdate
from datetime import datetime
from .discord import trigger_discord_notifications


class Issue(Document):
    def onload(self):
        self.set_onload()

    def set_onload(self):
        parent = super()
        parent.set_onload(
            "duplicates",
            self.get_duplicates(),
        )

    # def after_insert(self):
    #     trigger_discord_notifications({
    #         "doc": self,
    #         "is_new": True,
    #     })

    def validate(self):
        self.auto_set_resolver_if_not_set()
        if not self.is_new():
            trigger_discord_notifications({"doc": self})
        
        self.set_resolution_date()

    def on_update(self):
        self.update_delivered_for_qa_if_reqd()
        self.update_assignation_date_if_reqd()
        self.assign_to_resolver_if_not_assigned()
        self.assign_to_approver_if_not_assigned()
        self.close_timesheet_if_open()

    def get_duplicates(self):
        # based off the customer and remote_reference
        # key = (
        #     "customer", "remote_reference"
        # )

        if not self.remote_reference:
            return []

        return frappe.get_all(
            "Issue",
            filters={
                "customer": self.customer,
                "remote_reference": self.remote_reference,
                "name": ["!=", self.name],
            },
            fields=["name", "subject", "status"],
        )

    def auto_set_resolver_if_not_set(self):
        if self.is_new():
            return # don't do anything if this is a new record

        if self.resolver:
            return

        db_doc = self.get_doc_before_save()
        if not db_doc:
            return

        if self.workflow_state == "Working" \
            and db_doc.workflow_state != self.workflow_state:
            self.resolver = frappe.session.user

    def update_delivered_for_qa_if_reqd(self):
        # expected_state is the value that we are looking for
        # to know exactly when the Resolver has delivered the ticket
        expected_state = "Ready for QA"

        db_doc = self.get_doc_before_save()

        if not db_doc:
            return "No doc before save... this is a new record."

        # if the ticket was transitioned to a higher state in the workflow
        # and the delivered_for_qa field is empty, because this step was skipped
        # then we need to update the delivered_for_qa field
        higher_states = {
            "Code Quality Passed",
            "Completed",
        }

        # to prevent a refactor of the code, which would take more time
        # and also to prevent from writting the same code twice,
        # I will use this variable instead to know if I should update the
        # delivered_for_qa field

        shall_update_delivered_for_qa = False

        # if the ticket was transitioned to the expected state in the workflow
        # and the workflow state before was not the expected state
        # then we need to update the delivered_for_qa field
        if self.workflow_state == expected_state \
            and db_doc.workflow_state != expected_state:
            shall_update_delivered_for_qa = True

        if self.workflow_state in higher_states \
            and not self.delivered_for_qa:
            shall_update_delivered_for_qa = True

        if shall_update_delivered_for_qa:
            self.db_set("delivered_for_qa", frappe.utils.now())

    def update_assignation_date_if_reqd(self):
        # the main idea of this method is to keep updated the assignation_date.
        # it's going to gather some system information to do the lifting for two
        # other utility methods.
        db_doc = self.get_doc_before_save()

        if not db_doc:
            return "No doc before save... this is a new record."

        if self.resolver or db_doc.resolver:
            # let's do it the resolver's way

            # and we simply need to update the assignation_date
            if self.resolver == db_doc.resolver:
                return # not much should happen if resolver didn't change
            
            # if the resolver changed, then we need to update the assignation_date
            if self.resolver and not db_doc.resolver:
                self.db_set("assignation_date", frappe.utils.now())
                return
            
            # if the resolver was removed, then we need to update the assignation_date
            if not self.resolver and db_doc.resolver:
                self.db_set("assignation_date", None)
                return
        else:
            # now, this is a bit more complicated.
            # we are going to use the _assign field to know if the ticket
            # was assigned to someone or not. the _assign field is a json
            # array that contains the list of assignees. and we need to know
            # if the assignees are developers or just implementers.

            # there is a catch in here.
            # usually developers self assign tickets to themselves with the intention
            # to be the resolvers. rarely, they assign tickets to other developers (for not saying never).
            #
            # in the other hand, sometimes superiors assign a ticket to a developer which
            # might not be the resolver, just to the mere purpose of researching or gathering information.
            # in this case, the superior obviously is different then the assignee.
            # later
            
            old_assignees = json.loads(
                db_doc.get("_assign") or "[]",
            )

            new_assignees = json.loads(
                self.get("_assign") or "[]",
            )

            # if the assignees are the same, then we don't need to do anything
            if old_assignees == new_assignees:
                return

            # if the assignees are different, then we need to update the assignation_date
            if old_assignees and not new_assignees:
                self.db_set("assignation_date", None)
                return

            # if the assignees are different, then we need to update the assignation_date
            if not old_assignees and new_assignees:
                self.db_set("assignation_date", frappe.utils.now())
                return

            # # if the assignees are different, then we need to update the assignation_date
            # if old_assignees != new_assignees:
            #     self.db_set("assignation_date", frappe.utils.now())
            #     return

    def set_resolution_date(self):
        if self.status not in ("Resolved", "Closed"):
            self.resolution_date = None
            return
        if not self.resolution_date:
            self.resolution_date = frappe.utils.now()
        
    def assign_to_resolver_if_not_assigned(self):
        if not self.resolver:
            return "No resolver, no assign"

        db_doc = self.get_doc_before_save()

        if not db_doc:
            return "No doc before save... this is a new record."

        if db_doc.resolver == self.resolver:
            return "Resolver is the same, no assign"

        self.assign_to_resolver(re_assign=not db_doc.resolver)

    def assign_to_approver_if_not_assigned(self):
        if not self.approver:
            return "No approver, no assign"

        db_doc = self.get_doc_before_save()

        if not db_doc:
            return "No doc before save... this is a new record."

        if db_doc.approver == self.approver:
            return "Approver is the same, no assign"

        self.assign_to_approver(re_assign=not db_doc.approver)

    def close_timesheet_if_open(self):
        """Checks whether the related timesheet is still open and closes it if it is.
        This will be true as long as the new state is "Ready for QA"
        """

        if self.has_state_changed_to("Ready for QA"):
            # get any open timer for this issue
            doctype = "Timesheet"
            for detail, name in self.get_open_timelogs(
                self.name, self.resolver or frappe.session.user
            ):
                doc = frappe.get_doc(doctype, name)

                # find the time log and close it
                for time_log in doc.time_logs:
                    if time_log.name != detail:
                        continue

                    time_log.to_time = now_datetime()
                    time_log.completed = 1
                    time_log.hours = (
                        time_log.to_time - time_log.from_time
                    ).total_seconds() / 3600

                    break # look no further

                doc.save()

                frappe.msgprint(
                    f"""
                        Timesheet {doc.name} has been closed for Issue {self.name} as it has been moved to "Ready for QA"
                    """
                )

                break # don't overdo it
            else:
                frappe.msgprint(
                    f"""
                        <h4>
                            Be Careful: No open timers found for Issue {self.name}
                        </h4>

                        <p class="muted">
                            In the best interest of us all and for the next one,
                            please make sure you log your time properly.
                        </p>
                    """, indicator="red", title="Warning"
                )
        else:
            return "State is not Ready for QA"

    def has_state_changed_to(self, state, true_for_new=False):
        before_save = self.get_doc_before_save()

        if not before_save:
            return true_for_new

        return self.workflow_state == state \
            and before_save.workflow_state != state

    def get_open_timelogs(self, issue, user):
        return frappe.db.sql(
            """
            Select
                detail.name, detail.parent
            From
                `tabTimesheet` As parent
            Inner Join
                `tabTimesheet Detail` As detail
            On
                parent.name = detail.parent
                And detail.parenttype = "Timesheet"
                And detail.parentfield = "time_logs"
            Inner Join
                `tabEmployee` As employee
            On
                parent.employee = employee.name
            Where
                IfNull(detail.to_time, "") = ""
                And detail.issue = %s
                And parent.docstatus = 0
                And employee.user_id = %s
            """, (issue, user)
        )


    def assign_to_resolver(self, re_assign=False):
        # verify if the resolver is already assigned
        assignees = self.get_assignees()

        if self.resolver in assignees:
            return "Resolver is already assigned"

        role = "Resolver"
        self.assign_one(self.resolver, role, re_assign=re_assign)

    def assign_to_approver(self, re_assign=False):
        # verify if the approver is already assigned
        assignees = self.get_assignees()

        if self.approver in assignees:
            return "Approver is already assigned"

        role = "Approver"
        self.assign_one(self.approver, role, re_assign=re_assign)

    def assign_one(self, user, role, re_assign=False):
        do_assignation({
            "assign_to_me": 0,
            "assign_to": [user],
            "date": self.get_due_date(),
            "description": self.get_description(role=role),
            "doctype": self.doctype,
            "name": self.name,
            "bulk_assign": False,
            "re_assign": re_assign,
        })

    def get_description(self, role):
        # return the subject, a brief description and message based on the role.
        # possible roles are: Approver and Resolver

        if role == "Approver":
            return f"""
                <h3>You've been assign a new Ticket as Approver</h3>
                <p>{self.subject}</p>
                <p>{self.description}</p>
            """

        return f"""
            <h3>You've been assign a new Ticket as Resolver</h3>
            <p>{self.subject}</p>
            <p>{self.description}</p>
        """

    def get_due_date(self):
        # add five working days to the current date
        # Saturday and Sunday are not considered as working days
        suggested_working_days = 5

        today = frappe.utils.getdate(
            frappe.utils.nowdate()
        )

        exact_date = frappe.utils.add_days(today, suggested_working_days)

        # if the exact date is on a saturday, add two days
        if frappe.utils.get_weekday(exact_date) == "Sarturday":
            return frappe.utils.add_days(exact_date, 2)

        # if the exact date is on a sunday, add one day
        if frappe.utils.get_weekday(exact_date) == "Sunday":
            return frappe.utils.add_days(exact_date, 1)

        return exact_date


    def get_assignees(self):
        return set(
            json.loads(
                self.get("_assign", default="[]"),
            ),
        )


@frappe.whitelist()
def get_open_timers(issue_name, user):
    TS = frappe.qb.DocType("Timesheet")
    TSD = frappe.qb.DocType("Timesheet Detail")
    EMP = frappe.qb.DocType("Employee")

    return frappe.qb.from_(TS).join(TSD).on(
        TS.name == TSD.parent,
    ).join(EMP).on(
        TS.employee == EMP.name
    ).select(
        TS.name.as_("timesheet"),
        TSD.name.as_("log_name"),
        TSD.activity_type,
        TSD.expected_hours,
        TSD.issue,
        TSD.from_time
    ).where(
        (TSD.issue == issue_name)&
        (EMP.user_id == user)&
        (EMP.status == 'Active')&
        (TSD.completed == 0)
    ).run(as_dict=True)


@frappe.whitelist()
def create_timelogs(activity_type, expected_hours, issue):
    EMP = frappe.qb.DocType("Employee")
    TS = frappe.qb.DocType("Timesheet")
    today = frappe.utils.nowdate()
    ts = None

    timesheets = frappe.qb.from_(TS).join(EMP).on(
        TS.employee == EMP.name
    ).select(
        TS.name
    ).where(
        (EMP.user_id == frappe.session.user)&
        (EMP.status == 'Active')&
        (TS.start_date == today)&
        (TS.docstatus == 0)
    ).run(as_dict=True)
    
    if timesheets:
        ts = frappe.get_doc("Timesheet", timesheets[0].name)
    else:
        ts = frappe.new_doc("Timesheet")
        ts.employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user})
        ts.start_date = today
        ts.en_date = today
    
    ts.append("time_logs", {
        "activity_type": activity_type,
        "from_time": now_datetime(),
        "issue": issue,
        "is_billable": 0
    })
    ts.save()


@frappe.whitelist()
def complete_timelogs(timesheet, log_name):
    doc = frappe.get_doc("Timesheet", timesheet)
    log = doc.get("time_logs", {"name": log_name})[0]
    from_time = log.get("from_time")
    to_time = now_datetime()
    log.update({
        "to_time": now_datetime(),
        "completed": 1,
        "hours": (to_time - from_time).total_seconds() / 3600
    })
    doc.save()
    

def get_permission_query_conditions(user=None):
    if user is None:
        user = frappe.session.user

    # skip those that are completed and have more than 30 days without any modifications
    return """
        `tabIssue`.workflow_state != "Completed"
        Or `tabIssue`.modified >= DATE_SUB(CURDATE(), INTERVAL 45 DAY)
    """
    

def has_permission():
    pass
