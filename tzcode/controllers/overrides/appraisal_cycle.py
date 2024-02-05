# Copyright (c) 2023, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe
from frappe import _

from hrms.hr.doctype.appraisal_cycle import appraisal_cycle

from . import overrides

class AppraisalCycle(appraisal_cycle.AppraisalCycle):
	@frappe.whitelist()
	def create_appraisals(self):
		self.check_permission("write")
		if not self.appraisees:
			frappe.throw(
				_("Please select employees to create appraisals for"), title=_("No Employees Selected")
			)

		if not all(appraisee.appraisal_template for appraisee in self.appraisees):
			self.show_missing_template_message(raise_exception=True)

		if len(self.appraisees) > 30:
			frappe.enqueue(
				create_appraisals_for_cycle,
				queue="long",
				timeout=600,
				appraisal_cycle=self,
			)
			frappe.msgprint(
				_("Appraisal creation is queued. It may take a few minutes."),
				alert=True,
				indicator="blue",
			)
		else:
			create_appraisals_for_cycle(self, publish_progress=True)
			# since this method is called via frm.call this doc needs to be updated manually
			self.reload()


@overrides
def create_appraisals_for_cycle(appraisal_cycle: AppraisalCycle, publish_progress: bool = False):
	"""
	Creates appraisals for employees in the appraisee list of appraisal cycle,
	if not already created
	"""
	count = 0

	for employee in appraisal_cycle.appraisees:
		try:
			appraisal = frappe.new_doc("Appraisal")
			appraisal.update({
				"appraisal_template": employee.appraisal_template,
				"employee": employee.employee,
				"appraisal_cycle": appraisal_cycle.name,
				"from_appraisal_cycle": 1,
			})

			appraisal.rate_goals_manually = (
				1 if appraisal_cycle.kra_evaluation_method == "Manual Rating" else 0
			)
			appraisal.set_kras_and_rating_criteria()
			appraisal.insert()

			if publish_progress:
				count += 1
				frappe.publish_progress(
					count * 100 / len(appraisal_cycle.appraisees), title=_("Creating Appraisals") + "..."
				)
		except frappe.DuplicateEntryError:
			# already exists
			pass
