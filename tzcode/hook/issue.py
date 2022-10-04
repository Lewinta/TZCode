import frappe
import requests
import json
from frappe import enqueue


@frappe.whitelist()
def create_issue(subject, status, customer, raised_by, remote_reference, priority=None, description="No Description"):
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
        "due_date": doc.due_date,
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
