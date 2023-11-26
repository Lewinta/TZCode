# Copyright (c) 2022, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe.realtime import publish_realtime
from frappe.utils.background_jobs import enqueue_doc

from tzcode.controllers.overrides.issue.discord import (
    trigger_discord_notifications,
)


class BulkIssue(Document):
    def after_insert(self):
        doctype = self.doctype
        name = self.name
        method = "create_issue"
        queue = 'default'
        timeout = 300
        now = False

        enqueue_doc(
            doctype,
            name,
            method,
            queue,
            timeout,
            now,
        )

        frappe.msgprint("Bulk Issue created")

    def on_update(self):
        if self.is_new():
            return "Only for existing documents"

        doctype = self.doctype
        name = self.name
        method = "update_issue"
        queue = 'default'
        timeout = 300
        now = False

        enqueue_doc(
            doctype,
            name,
            method,
            queue,
            timeout,
            now,
        )

        frappe.msgprint("Bulk Issue updated")

    def create_issue(self, auto_commit=True):
        doctype = "Issue"

        doc = frappe.new_doc(doctype)

        doc.update({
            "subject": self.subject,
            "status": self.status,
            "customer": self.customer,
            "raised_by": self.raised_by,
            "remote_reference": self.remote_reference,
            "priority": self.priority,
            "description": self.description,
        })

        doc.flags.ignore_permissions = True
        doc.flags.ignore_mandatory = True

        try:
            doc.db_insert()
        except:
            frappe.log_error(frappe.get_traceback())


        trigger_discord_notifications({
            "doc": doc,
            "is_new": True,
        })

        if auto_commit:
            frappe.db.commit()

            # todo: trigger method to send email to admin

        publish_realtime(
            "version_update",
            message="Issue created",
            user=frappe.session.user
        )

    def update_issue(self):
        doctype = "Issue"

        filters = {
            "remote_reference": self.remote_reference,
            "customer": self.customer,
        }

        doc = frappe.get_doc(doctype, filters)

        doc.update({
            "subject": self.subject,
            "status": self.status,
            "customer": self.customer,
            "raised_by": self.raised_by,
            "remote_reference": self.remote_reference,
            "priority": self.priority,
            "description": self.description,
        })

        doc.flags.ignore_permissions = True
        doc.flags.ignore_mandatory = True

        doc.modified = frappe.utils.now()
        doc.modified_by = frappe.session.user

        try:
            doc.db_update()
        except:
            frappe.log_error(frappe.get_traceback())

            # todo: trigger method to send email to admin

        frappe.db.commit()

        publish_realtime(
            "version_update",
            message="Issue updated",
            user=frappe.session.user
        )

    subject = None
    status = None
    customer = None
    raised_by = None
    remote_reference = None
    priority = None
    description = None
