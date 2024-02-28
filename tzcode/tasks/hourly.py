# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe

from tzcode.controllers.overrides.appraisal.automation import (
    submit_all_draft_appraisals,
)

from tzcode.controllers.overrides.timesheet.automation import (
    submit_previous_draft_timesheets,
)

def execute():
    try:
        submit_all_draft_appraisals()
    except Exception as e:
        frappe.log_error(e)
        frappe.db.rollback()
        raise e
    else:
        frappe.db.commit()

    try:
        submit_previous_draft_timesheets()
    except Exception as e:
        frappe.log_error(e)
        frappe.db.rollback()
        raise e
    else:
        frappe.db.commit()        
