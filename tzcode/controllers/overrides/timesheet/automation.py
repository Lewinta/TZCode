# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe


__all__ = ("submit_draft_timesheets",)


# called from tzcode/tzcode/tasks/daily.py
def submit_draft_timesheets():
    """This method submits smartly all draft timesheets
    Which have rounded time entries. That means
    all timesheets which have all entries with both values
    for from_time and to_time cols in their time_logs.
    """

    # get all draft timesheets
    doclist = frappe.get_all(
        "Timesheet",
        filters={
            "start_date": ("<", frappe.utils.today()),
            "docstatus": 0,
        },
        pluck="name",
    )

    # iterate over all draft timesheets
    for name in doclist:
        doc = get_timesheet(name)

        # check if all time_logs have both from_time and to_time
        # if so, submit the timesheet
        if all([doc.from_time and doc.to_time for doc in doc.time_logs]):
            doc.submit()


# called from tzcode/tzcode/tasks/daily.py
def submit_previous_draft_timesheets():
    """
    This method submits smartly all draft timesheets
    Which have being created on a date before today and which have
    rounded time entries. That means all timesheets which have all entries
    with both values for from_time and to_time cols in their time_logs.
    """
    
    # get all draft timesheets
    doclist = frappe.get_all(
        "Timesheet",
        filters={
            "start_date": ("<", frappe.utils.today()),
            "docstatus": 0,
        },
        pluck="name",
    )

    # iterate over all draft timesheets
    for name in doclist:
        doc = get_timesheet(name)

        # check if all time_logs have both from_time and to_time
        # if so, submit the timesheet
        if all([doc.from_time and doc.to_time for doc in doc.time_logs]):
            doc.submit()


def get_timesheet(name):
    """Returns a timesheet document"""
    doctype = "Timesheet"
    return frappe.get_doc(doctype, name)
