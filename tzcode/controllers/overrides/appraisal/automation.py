# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe

__all__ = ("create_developer_appraisals", "submit_all_draft_appraisals", )

class AppraisalCycleNotFound(Exception):
    pass


def create_developer_appraisals():
    try:
        _create_developer_appraisals()
    except AppraisalCycleNotFound:
        frappe.db.rollback()
        frappe.log_error()
        frappe.db.commit()


def _create_developer_appraisals():
    """Run via scheduler events hourly.
    Create appraisals for all developers that are not in the appraisal cycle.
    """

    # run only on fridays
    if not is_it_friday():
        return # only for fridays

    # get the appraisal cycle for the current week
    cycles = get_current_appraisal_cycles()
    try:
        cycle = cycles[0]
    except IndexError:
        raise AppraisalCycleNotFound("No appraisal cycle found for the current week")

    doc = get_appraisal_cycle(cycle)

    try:
        doc.create_appraisals()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error()
        frappe.db.commit()


def get_appraisal_cycle(name):
    doctype = "Appraisal Cycle"
    return frappe.get_doc(doctype, name)


def get_current_appraisal_cycles():
    """Get the current appraisal cycle for the current week
        Which is also marked as is_weekly = 1
    """

    query = """
        Select
            name
        From
            `tabAppraisal Cycle`
        Where
            is_weekly = 1
            And start_date <= CurDate()
            And end_date >= CurDate()
    """

    return frappe.db.sql_list(query)


def submit_all_draft_appraisals():
    """Run via scheduler events hourly.
    Submit all draft appraisals that are past their due date.
    """

    # run only on mondays
    if not is_it_monday():
        return # only for mondays

    # wait up to 10 am to submit appraisals
    if is_later_than_10_am():
        doclist = get_doclist()
        submit_all_appraisals(doclist)


def is_it_monday():
    return frappe.utils.getdate().weekday() == 0

def is_it_friday():
    return frappe.utils.getdate().weekday() == 4


def is_later_than_10_am():
    return frappe.utils.now_datetime().hour > 10


def get_doclist():
    query = """
        Select
            appraisal.name
        From
            `tabAppraisal` As appraisal
        Inner Join
            `tabAppraisal Cycle` As cycle
            On appraisal.appraisal_cycle = cycle.name
        Where
            appraisal.docstatus = 0
            And appraisal.department = 'Desarrollo - TZ'
            And cycle.end_date < CurDate()

    """

    return [d for d in frappe.db.sql_list(query)]

def get_appraisal(docname):
    doctype = "Appraisal"
    return frappe.get_doc(doctype, docname)


def submit_all_appraisals(doclist):
    for docname in doclist:
        doc = get_appraisal(docname)

        doc.status = "Draft"

        try:
            doc.submit()
        except Exception as e:
            frappe.db.rollback()
            frappe.log_error()
            frappe.db.commit()
            continue
        else:
            frappe.db.commit()
            print(f"Appraisal {docname} submitted successfully")
