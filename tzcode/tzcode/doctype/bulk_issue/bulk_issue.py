# Copyright (c) 2022, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe.realtime import publish_realtime
from frappe.utils.background_jobs import enqueue_doc

from tzcode.controllers.overrides.issue.discord import (
    trigger_discord_notifications,
)

from . import locker


class BulkIssue(Document):
    def validate(self):
        if self.is_new():
            return "Only for existing documents"

        if self.modified_by == "ticket@tzcode.tech" \
            and frappe.session.user == "ticket@tzcode.tech" \
            and not self.elapsed_time(seconds=60):
            frappe.throw("You can't update this document yet")

    def after_insert(self):
        self.hsh = frappe.generate_hash()

        # frappe.msgprint("Bulk Issue created")
        if locker.is_locked():
            locker.retry_after_5_secs(
                self.create_issue,
            )
        else:
            locker.acquire_lock(self.hsh)

            self.create_issue()


    def on_update(self):
        if self.is_new():
            return "Only for existing documents"

        doctype = self.doctype
        name = self.name
        method = "update_issue"
        queue = 'default'
        timeout = 300
        now = False
        job_id = f"{doctype}-{name} update_issue"

        enqueue_doc(
            doctype=doctype,
            name=name,
            method=method,
            queue=queue,
            timeout=timeout,
            now=now,
            enqueue_after_commit=True,
            job_id=job_id,
        )

        frappe.msgprint("Bulk Issue updated")

    def elapsed_time(self, seconds=60):
        # verifies if the elapsed time is greater than the specified seconds
        # if it is, then it returns True, otherwise it returns False
        now = frappe.utils.now_datetime()

        modified = frappe.utils.get_datetime(self.modified)
        
        elapsed = now - modified

        return elapsed.total_seconds() > seconds

    def check_if_exists(self):
        # lock the table
        # this is just to prevent the creation of the same issue
        # frappe.db.sql("Select Max(name) from `tabIssue` For Update")

        doctype = "Issue"

        filters = {
            "remote_reference": self.remote_reference,
            "customer": self.customer,
        }

        return frappe.db.exists(doctype, filters)

    @frappe.whitelist()
    def create_issue(self, auto_commit=True):
        if self.check_if_exists():
            return self.update_issue(auto_commit=auto_commit)


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
        doc.flags.dont_notify_client = True

        try:
            doc.db_insert()
        except Exception as e:
            frappe.log_error()


        trigger_discord_notifications({
            "doc": doc,
            "is_new": True,
        })

        if auto_commit:
            frappe.db.commit()

            # todo: trigger method to send email to admin

        # publish_realtime(
        #     "version_update",
        #     message="Issue created",
        #     user=frappe.session.user
        # )

        locker.release_lock(self.hsh)

    @frappe.whitelist()
    def update_issue(self, auto_commit=True):
        if not self.check_if_exists():
            return self.create_issue(auto_commit=auto_commit)
        else:
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
            except Exception as e:
                frappe.log_error()

                # todo: trigger method to send email to admin

            if auto_commit:
                frappe.db.commit()

            # publish_realtime(
            #     "version_update",
            #     message="Issue updated",
            #     user=frappe.session.user
            # )

    subject = None
    status = None
    customer = None
    raised_by = None
    remote_reference = None
    priority = None
    description = None
    hsh = None
