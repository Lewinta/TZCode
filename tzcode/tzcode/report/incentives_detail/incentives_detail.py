# Copyright (c) 2024, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import Criterion, functions as fn


def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	default_columns =  [
		{
			"fieldname": "appraisal",
			"label": "Appraisal",
			"fieldtype": "Link",
			"options": "Appraisal",
			"width": 160
		},
		{
			"fieldname": "start_date",
			"label": "Start Date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "end_date",
			"label": "End Date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "employee",
			"label": "Employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 290
		},
		{
			"fieldname": "employee_name",
			"label": "Employee Name",
			"fieldtype": "Data",
			"width": 260,
			"hidden": 1
		},
		{
			"fieldname": "total_score",
			"label": "Total Score",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "max_score",
			"label": "Max Score",
			"fieldtype": "Float",
			"width": 120
		},

	]

	if filters.get("summary"):
		# Let's add the Percentage column
		default_columns.append(
			{
				"fieldname": "percentage",
				"label": "% Earned",
				"fieldtype": "Float",
				"width": 120
			}
		)
	return  default_columns

def get_data(filters):
	A = frappe.qb.DocType("Appraisal")
	conditions = [A.docstatus == 1]
	
	if filters.get("employee"):
		conditions.append(A.employee == filters.get("employee"))
	if filters.get("start_date"):
		conditions.append(A.start_date >= filters.get("start_date"))
	if filters.get("end_date"):
		conditions.append(A.start_date <= filters.get("end_date"))
	
	if filters.get("summary"):
		return frappe.qb.from_(A).select(
			A.name.as_("appraisal"),
			fn.Min(A.start_date).as_("start_date"),
			fn.Max(A.end_date).as_("end_date"),
			A.employee,
			A.employee_name,
			fn.Sum(A.total_score).as_("total_score"),
			fn.Sum(5 * A.docstatus).as_("max_score"),
			fn.Avg(A.total_score / 5.00 * 100.00 ).as_("percentage")
		).where(
			Criterion.all(conditions)
		).groupby(A.Employee).run(as_dict=True)
	else:
		return frappe.qb.from_(A).select(
			A.name.as_("appraisal"),
			A.start_date,
			A.end_date,
			A.employee,
			A.employee_name,
			A.total_score,
			(5 * A.docstatus).as_("max_score"),
			(A.total_score / 5.00 * 100.00 ).as_("percentage")
		).where(
			Criterion.all(conditions)
		).run(as_dict=True)