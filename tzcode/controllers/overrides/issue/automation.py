# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe

class UnknownError(Exception):
	...


def mark_issue_as_seen_in_meeting():
    try:
        _mark_issue_as_seen_in_meeting()
    except UnknownError:
        frappe.db.rollback()
        frappe.log_error()
        frappe.db.commit()


def _mark_issue_as_seen_in_meeting():
	if not is_it_friday():
		return # only for fridays

	frappe.db.sql(
		"""
			Update
				`tabIssue`
			Set
				seen_in_meeting = CURDATE()
			Where
				workflow_state In (
					"Viewed But Yikes",
					"No code to Review",
					"Code Quality Passed",
					"Awaiting Customer",
					"Acceptance Criteria Met",
					"Deploying in Production",
					"Completed"
				) 
				And delivered_for_qa Is Not Null
				And IfNull(seen_in_meeting, "") = ""
				And assignation_date >= "2024-06-01" -- introduction date
		"""
	)


def is_it_friday():
    return frappe.utils.getdate().weekday() == 4


# def is_later_than_10_am():
#     return frappe.utils.now_datetime().hour > 10