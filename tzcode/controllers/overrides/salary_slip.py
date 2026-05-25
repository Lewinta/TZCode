import frappe

from hrms.payroll.doctype.salary_slip.salary_slip import (
	SALARY_COMPONENT_VALUES,
	SalarySlip as HRMSSalarySlip,
)


class SalarySlip(HRMSSalarySlip):
	def get_data_for_eval(self):
		"""Build formula context with aggregated values per component abbr.

		HRMS can add multiple rows with the same abbr (for example, structure row
		plus non-overwrite Additional Salary). Aggregate those values so formula-
		based deductions consider the full component amount.
		"""
		data = frappe._dict()
		employee = frappe.get_cached_doc("Employee", self.employee).as_dict()

		if not hasattr(self, "_salary_structure_assignment"):
			self.set_salary_structure_assignment()

		data.update(self._salary_structure_assignment)
		data.update(employee)
		data.update(self.as_dict())
		data.update(self.get_component_abbr_map())

		# Shallow copy to store default values without payment-day adjustments.
		default_data = data.copy()

		for key in ("earnings", "deductions"):
			for row in self.get(key):
				abbr = row.abbr
				if not abbr:
					continue

				default_data[abbr] = (default_data.get(abbr) or 0) + (row.default_amount or 0)
				data[abbr] = (data.get(abbr) or 0) + (row.amount or 0)

		return data, default_data

	def get_component_abbr_map(self):
		def _fetch_component_values():
			return {
				component_abbr: 0
				for component_abbr in frappe.get_all("Salary Component", pluck="salary_component_abbr")
			}

		return frappe.cache().get_value(SALARY_COMPONENT_VALUES, generator=_fetch_component_values)
