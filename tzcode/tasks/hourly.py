# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe

from tzcode.controllers.overrides.appraisal.automation import (
    submit_all_draft_appraisals,
)


def execute():
    try:
        submit_all_draft_appraisals()
    except Exception as e:
        frappe.log_error(e)
        frappe.db.rollback()
        raise e
