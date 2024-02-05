# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import json
import frappe

from frappe.model.document import Document
from frappe.desk.form.assign_to import add as do_assignation

from .discord import trigger_discord_notifications


class Issue(Document):
    # def after_insert(self):
    #     trigger_discord_notifications({
    #         "doc": self,
    #         "is_new": True,
    #     })

    def validate(self):
        self.auto_set_resolver_if_not_set()
        if not self.is_new():
            trigger_discord_notifications({"doc": self})

    def on_update(self):
        self.update_delivered_for_qa_if_reqd()
        self.update_assignation_date_if_reqd()
        self.assign_to_resolver_if_not_assigned()
        self.assign_to_approver_if_not_assigned()

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
                db_doc.get("_assign", default="[]"),
            )

            new_assignees = json.loads(
                self.get("_assign", default="[]"),
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
