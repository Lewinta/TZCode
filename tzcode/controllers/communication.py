# Copyright (c) 2026, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe


def after_insert(doc, method=None):
	if doc.reference_doctype == "Issue" \
		and doc.sent_or_received == "Received":
		queue_set_description_on_reference_document(doc.name)

def queue_set_description_on_reference_document(docname):
	frappe.enqueue(
		method=set_description_on_reference_document,
		queue="short",
		enqueue_after_commit=True,
		docname=docname
	)

def set_description_on_reference_document(docname):
	import time
	time.sleep(10)

	doc = _get_communication_doc(docname)
	if doc.reference_doctype == "Issue" \
		and doc.sent_or_received == "Received":
		issue = _get_issue_doc(doc.reference_name)

		if not doc.content:
			frappe.log_error(
				f"Communication {docname} has no content",
				exc=Exception("Communication has no content")
			)
			queue_set_description_on_reference_document(docname)
			return
		issue.description = doc.content

		issue.flags.ignore_permissions = True
		issue.flags.ignore_mandatory = True
		issue.save()


def _get_communication_doc(name):
	doctype = "Communication"
	return frappe.get_doc(doctype, name)


def _get_issue_doc(name):
	doctype = "Issue"
	return frappe.get_doc(doctype, name)
