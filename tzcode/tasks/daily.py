# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe

from tzcode.controllers.overrides.appraisal.automation import (
    create_developer_appraisals,
)

from tzcode.controllers.overrides.timesheet.automation import (
    submit_draft_timesheets,
)


def execute():
    try:
        create_developer_appraisals()
    except Exception as e:
        frappe.log_error(e)
        frappe.db.rollback()
        raise e
    else:
        frappe.db.commit()

    # I have a feeling that for some reason this should be
    # executed before the create_developer_appraisals method
    # but, it was added later, so it was placed after the
    # create_developer_appraisals method.
    try:
        submit_draft_timesheets()
    except Exception as e:
        frappe.log_error(e)
        frappe.db.rollback()
        raise e
    else:
        frappe.db.commit()
