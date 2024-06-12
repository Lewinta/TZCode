# Copyright (c) 2024, Lewin Villar and contributors
# For license information, please see license.txt

import frappe

from frappe.model.document import Document

class NotWorkflowFoundError(Exception):
	pass

class TzSettings(Document):
	def validate(self):
		self.validate_allow_timesheets_against_states()

	def validate_allow_timesheets_against_states(self):
		valid_states = self.get_issue_workflow_states()
		for state in self.allow_timesheets_against_states:
			if state.state not in valid_states:
				frappe.throw(f"State '{state.state}' is not a valid state for Issue Workflow")

	def get_issue_workflow(self):
		doctype = "Workflow"
		filters = {
			"document_type": "Issue"
		}

		if name := frappe.db.exists(doctype, filters):
			return frappe.get_doc(doctype, name)

		raise NotWorkflowFoundError(f"No Workflow found for Issue")

	@frappe.whitelist()
	def get_issue_workflow_states(self):
		try:
			workflow = self.get_issue_workflow()
		except NotWorkflowFoundError:
			frappe.throw("It seems like there's no Workflow for Issue and we need it to proceed")

		return [d.state for d in workflow.states]

	@frappe.whitelist()
	def get_valid_issue_states(self):
		return set(
			d.state for d in self.allow_timesheets_against_states
		)
	
	