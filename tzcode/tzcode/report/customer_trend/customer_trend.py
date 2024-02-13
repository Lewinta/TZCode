# Copyright (c) 2024, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import Case, Criterion, functions as fn
from frappe.query_builder.functions import Function

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	return [
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 250
		},
		{
			"fieldname": "january",
			"label": _("January"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "february",
			"label": _("February"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "march",
			"label": _("March"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "april",
			"label": _("April"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "may",
			"label": _("May"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "june",
			"label": _("June"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "july",
			"label": _("July"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "august",
			"label": _("August"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "september",
			"label": _("September"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "october",
			"label": _("October"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "november",
			"label": _("November"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "december",
			"label": _("December"),
			"fieldtype": "Currency",
			"width": 120	
		},
		{
			"fieldname": "total",
			"label": _("Total"),
			"fieldtype": "Currency",
			"width": 120	
		},
	]

def get_data(filters):
	# Let's define Math function as it's not available in frappe.query_builder.functions
	class Month(Function):
		def __init__(self, term):
			super().__init__('MONTH', term)

	SI = frappe.qb.DocType("Sales Invoice")
	conditions = [
		SI.docstatus == 1,
		SI.posting_date >= filters.get("from_date"), 
		SI.posting_date <= filters.get("to_date")
	]
	return frappe.qb.from_(SI).select(
		SI.customer,
		fn.Sum(Case().when(Month(SI.posting_date) == 1, SI.base_net_total)).as_("january"),
		fn.Sum(Case().when(Month(SI.posting_date) == 2, SI.base_net_total)).as_("february"),
		fn.Sum(Case().when(Month(SI.posting_date) == 3, SI.base_net_total)).as_("march"),
		fn.Sum(Case().when(Month(SI.posting_date) == 4, SI.base_net_total)).as_("april"),
		fn.Sum(Case().when(Month(SI.posting_date) == 5, SI.base_net_total)).as_("may"),
		fn.Sum(Case().when(Month(SI.posting_date) == 6, SI.base_net_total)).as_("june"),
		fn.Sum(Case().when(Month(SI.posting_date) == 7, SI.base_net_total)).as_("july"),
		fn.Sum(Case().when(Month(SI.posting_date) == 8, SI.base_net_total)).as_("august"),
		fn.Sum(Case().when(Month(SI.posting_date) == 9, SI.base_net_total)).as_("september"),
		fn.Sum(Case().when(Month(SI.posting_date) == 10, SI.base_net_total)).as_("october"),
		fn.Sum(Case().when(Month(SI.posting_date) == 11, SI.base_net_total)).as_("november"),
		fn.Sum(Case().when(Month(SI.posting_date) == 12, SI.base_net_total)).as_("december"),
		fn.Sum(SI.base_net_total).as_("total")
	).where( Criterion.all(conditions) ).groupby( SI.customer ).run(as_dict=True)