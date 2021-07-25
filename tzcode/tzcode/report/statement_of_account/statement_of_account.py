# Copyright (c) 2013, Lewin Villar and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	"""return columns based on filters"""
	columns = [
		_("Invoice") 			+ ":Link/Sales Invoice:120",
		_("Date") 				+ ":Date:100",
		_("Customer") 			+ ":Data:200",
		_("Reference") 			+ ":Data:180",
		_("Neto")		 		+ ":Currency/currency:100",
		_("Dias")	 			+ ":Data:60",
		_("%")	 				+ ":Data:60",
		_("Descuento")	 		+ ":Currency/currency:90",
		_("ITBIS")	 			+ ":Currency/currency:90",
		_("Bruto")	 	+ ":Currency/currency:100",
		_("Pagado")	 	+ ":Currency/currency:100",
		_("Pendiente")	+ ":Currency/currency:100",
	]
	
	return columns

def get_conditions(filters):
	
	conditions = "`viewStatement`.docstatus = 1 AND `viewStatement`.status != 'Closed'"
	
	if filters.get("from_date"):
		conditions += " and `viewStatement`.posting_date >= '{}'".format(filters.get("from_date"))
	if filters.get("to_date"):
		conditions += " and `viewStatement`.posting_date <= '{}'".format(filters.get("to_date"))
	if filters.get("customer"):
		conditions += " and `viewStatement`.customer = '{}'".format(filters.get("customer"))
	if filters.get("unpaid"):
		conditions += " and `viewStatement`.outstanding_amount > 0"
			
	return conditions

def get_data(filters):
	results = []
	data = []
	if filters.get("currency") == "Company Currency":
		data =  frappe.db.sql("""
			SELECT 
				`viewStatement`.name,
				`viewStatement`.posting_date,
				`viewStatement`.customer,
				`viewStatement`.remarks,
				`viewStatement`.base_total,
				DATEDIFF(`viewStatement`.posting_date, CURDATE() ) as days,
				`	`.discount_amount,
				`viewStatement`.base_total_taxes_and_charges as taxes,
				`viewStatement`.additional_discount_percentage,
				`viewStatement`.base_grand_total as grand_total,
				`viewStatement`.paid_amount,
				`viewStatement`.outstanding_amount
			FROM
				`viewStatement`
			WHERE
				{conditions}
			ORDER BY 
				`viewStatement`.posting_date
		""".format(conditions=get_conditions(filters)), as_dict=True, debug=False)
	
	elif filters.get("currency") == "Invoice Currency":
		data = frappe.db.sql("""
			SELECT 
				`viewStatement`.name,
				`viewStatement`.posting_date,
				`viewStatement`.customer,
				`viewStatement`.remarks,
				`viewStatement`.total as base_total,
				DATEDIFF(`viewStatement`.posting_date, CURDATE() ) as days,
				`viewStatement`.discount_amount,
				`viewStatement`.total_taxes_and_charges as taxes,
				`viewStatement`.additional_discount_percentage,
				`viewStatement`.grand_total,
				`viewStatement`.grand_total - `viewStatement`.outstanding_amount as paid_amount,
				`viewStatement`.outstanding_amount
			FROM
				`viewStatement`
			WHERE
				{conditions}
			ORDER BY 
				`viewStatement`.posting_date
		""".format(conditions=get_conditions(filters)), as_dict=True, debug=False)

	for row in data:
			discount, rate = get_discount_rate(row)
			results.append(
				(
					row.name,
					row.posting_date,
					row.customer,
					row.remarks,
					row.base_total,
					row.days,
					"{}%".format(rate),
					discount,
					(row.base_total - discount) * 0.18,
					row.grand_total if row.additional_discount_percentage else row.grand_total - discount,
					row.paid_amount,
					row.outstanding_amount if row.additional_discount_percentage else row.outstanding_amount - discount,
				)
			)

	return results

def get_discount_rate(row): 
	if row.additional_discount_percentage:
		rate = row.additional_discount_percentage
		return flt(row.base_total * rate / 100.0, 2), rate
	rate = .00
	if row.days > 29:
		rate = 4.33
	if row.days > 59:
		rate = 8.67
	if row.days > 89:
		rate = 13.00
	# frappe.errprint("{} * {} / 100 = {}".format(row.base_total, rate, row.base_total * rate / 100.0))
	return flt(row.base_total * rate / 100.0, 2) or flt(row.discount), rate

