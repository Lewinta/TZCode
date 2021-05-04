import frappe

def validate(doc, method):
    sync_with_parent(doc)

def sync_with_parent(doc):
    if doc.is_group:
        filters = {"parent_task": doc.name}
        for name, in frappe.get_list("Task", filters, as_list=True):
            child = frappe.get_doc("Task", name)
            child.update({
                "color": doc.color,
                "project": doc.project,
            })
    else:
        if not doc.parent_task:
            return 
        color, project = frappe.get_value(
            "Task",
            doc.parent_task,
            ["color", "project"]
        )
        doc.update({
            "color": color,
            "project": project,
        })