import frappe
import requests
import json

from frappe import db
from frappe import enqueue

from frappe.utils import cstr

from . import locker


@frappe.whitelist()
def create_issue(subject, status, customer, raised_by, remote_reference, priority=None, description="No Description"):
    # unique hash for the function execution
    hsh = frappe.generate_hash()

    # allow only one of this function to run at a time
    if locker.lock_exists():
        # enqueue the function to run after 5 seconds
        locker.queue_after_5_secs(
            create_issue, subject, status, customer, raised_by,
            remote_reference, priority, description
        )
    else:
        locker.create_lock(hsh)

    doctype = "Bulk Issue"
    filters = {
        "remote_reference": remote_reference,
        "customer": customer,
    }

    if db.exists(doctype, filters):
        update_bulk_issue(subject, status, customer, raised_by,
                          remote_reference, priority, description)

    else:
        create_bulk_issue(subject, status, customer, raised_by,
                          remote_reference, priority, description)

    # remove the lock
    locker.remove_lock(hsh)


def create_bulk_issue(subject, status, customer, raised_by, remote_reference, priority=None, description="No Description"):
    doctype = "Bulk Issue"
    doc = frappe.new_doc(doctype)
    doc.update({
        "subject": subject,
        "status": status,
        "customer": customer,
        "raised_by": raised_by,
        "remote_reference": remote_reference,
        "priority": priority,
        "description": description,
    })

    doc.save(ignore_permissions=True)
    return doc.as_dict()


def update_bulk_issue(subject, status, customer, raised_by, remote_reference, priority=None, description="No Description"):
    doctype = "Bulk Issue"

    doc = frappe.get_doc(doctype, {
        "remote_reference": remote_reference,
    })

    doc.update({
        "subject": subject,
        "status": status,
        "customer": customer,
        "raised_by": raised_by,
        "remote_reference": remote_reference,
        "priority": priority,
        "description": description,
    })

    doc.save(ignore_permissions=True)
    return doc.as_dict()


def _create_issue():
    if not priority:
        priority = "Medio"

    if priority and not frappe.db.exists("Issue Priority", priority):
        priority = "Medio"

    exists = frappe.db.exists("Issue", {"remote_reference": remote_reference})
    issue = frappe.get_doc(
        "Issue", exists) if exists else frappe.new_doc("Issue")

    issue.update({
        "subject": subject,
        "status": status,
        "customer": customer,
        "raised_by": raised_by,
        "remote_reference": remote_reference,
        "priority": priority,
        "description": description,
    })
    issue.db_update() if exists else issue.save(ignore_permissions=True)
    return issue.as_dict()


def on_update(doc, method):
    enqueue(close_issue, doc=doc)
    set_closed_by(doc)


def close_issue(doc):
    try:
        _close_issue(doc)
    except Exception as e:
        pass

def _close_issue(doc):
    if not doc.customer:
        return

    remote_method = "/api/resource/Issue/{}".format(doc.remote_reference)
    customer = frappe.get_doc("Customer", doc.customer)
    if not customer.api_key or not customer.api_secret:
        frappe.throw("Please fill out integration section for customer {}".format(
            customer.customer_name))

    headers = {"Authorization": 'token {}:{}'.format(
        customer.api_key, customer.api_secret)}
    data = json.dumps({
        "status": doc.status,
        "resolution_details": doc.resolution_details,
        "due_date": cstr(doc.due_date),
        "assigned_to": doc.assigned_to,
    })
    endpoint = "{}{}".format(customer.host_url, remote_method)
    response = requests.put(
        url=endpoint,
        data=data,
        headers=headers
    )
    response.raise_for_status()
    # print(response.text)


def set_closed_by(doc):
    if doc.workflow_state == "Closed" \
            and not doc.closed_by:
        doc.closed_by = frappe.session.user
        doc.db_update()
