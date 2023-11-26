import frappe
from frappe.utils import nowdate

def validate(doc, method):
    if doc.workflow_state == "Assigned" and not doc.date:
        frappe.throw("""Please complete the following actions:
        <ol>
            <li> Read the description carefully.</li>
            <li> Estimate how long will take you to solve this issue.</li>
            <li> Enter a due date.</li>
            <li> Save this Document.</li>
    """)

def on_update(doc, method):
    return
    if doc.reference_type == "Issue" and doc.reference_name:
        issue = frappe.get_doc("Issue", doc.reference_name)
        issue.status = doc.status
        issue.due_date = doc.date
        issue.workflow_state = doc.workflow_state
        issue.assigned_to = frappe.get_value("User", frappe.session.user, "full_name")
        if issue.status == "Closed":
            issue.resolution_date = nowdate()
        issue.save()
    
def after_insert(doc, method):
    pass
