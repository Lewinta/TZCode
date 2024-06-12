# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_employee_list(doctype, txt, searchfield, start, page_len, filters=None):
    if filters is None:
        filters = dict()

    if isinstance(filters, dict):
        # if not has_management_role():
        filters.update({
            "status": "Active",
        })
    elif isinstance(filters, list):
        # if not has_management_role():
        if "status" not in {d[0] for d in filters}:  # noqa
            filters.append(["status", "=", "Active"])

    fields = ["name", "employee_name", "status"]

    text_in = {
        "name": ("like", "%%%s%%" % txt),
        "employee_name": ("like", "%%%s%%" % txt)
    }

    return frappe.get_list(
        doctype,
        fields=fields,
        filters=filters,
        or_filters=text_in,
        start=start,
        page_length=page_len,
        order_by="status",
        as_list=True
    )
