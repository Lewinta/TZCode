# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import json
from bs4 import BeautifulSoup

import frappe


import frappe.app
from frappe.model.workflow import apply_workflow


@frappe.whitelist()
def get_list_of_todos(filters=None, fields=None):
    if filters is None:
        filters = {}

    if isinstance(filters, str):
        import json
        filters = json.loads(filters)

    if fields is None:
        fields = ["name"]

    if isinstance(fields, str):
        fields = fields.split(",")

    table_fields = set(
        frappe.db.get_db_table_columns("tabIssue")
    )

    for fieldname in fields:
        if fieldname not in table_fields:
            return f"fieldname {fieldname} is not valid field"
    

    asking_for_description = False
    if "description" in fields:
        asking_for_description = True

    asking_for_comments = False
    if "_comments" in fields:
        asking_for_comments = True

    return _get_list_of_todos(
        filters=filters,
        fields=fields,
        has_description=asking_for_description,
        has_comments=asking_for_comments,
    )

def _get_list_of_todos(filters, fields, has_description=False, has_comments=False):
    doctype = "Issue"

    out = list()

    for issue in frappe.get_all(doctype, filters, fields):
        if has_description:
            soup = BeautifulSoup(issue.description, "html.parser")
            issue.description = soup.get_text("\n")
            

        if has_comments:
            comments = list()
            for comment in json.loads(issue._comments or "[]"):
                try:
                    soup = BeautifulSoup(comment["comment"], "html.parser")
                except TypeError:
                    continue
                else:
                    _comment = soup.get_text("\n")
                    comment["comment"] = _comment
                    comments.append(
                        comment
                    )

            del issue["_comments"]
            issue.comments = json.dumps(comments)

        out.append(issue)

    return out

@frappe.whitelist()
def apply_workflow_state(issue_id, action):
    doctype = "Issue"
    doc = frappe.get_doc(doctype, issue_id)

    apply_workflow(doc=doc, action=action)

    doc.reload()
    frappe.db.commit()
    return doc
