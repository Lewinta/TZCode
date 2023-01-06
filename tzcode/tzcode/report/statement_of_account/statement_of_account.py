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
		_("Invoice") 			+ ":Link/Sales Invoice:180",
		_("Date") 				+ ":Date:95",
		_("Customer") 			+ ":Data:150",
		_("NCF") 				+ ":Data:110",
		_("Reference") 			+ ":Data:180",
		_("Neto")		 		+ ":Currency/currency:100",
		# _("Dias")	 			+ ":Data:60",
		# _("%")	 				+ ":Data:60",
		# _("Descuento")	 		+ ":Currency/currency:90",
		_("Tax Amt.")	 			+ ":Currency/currency:90",
		_("Gross Amt.")	 	+ ":Currency/currency:100",
		_("Paid Amt.")	 	+ ":Currency/currency:100",
		_("Pending Amt.")	+ ":Currency/Currency:120",
		_("Last. Pymt")	 	+ ":Date:95",
		_("Document")	 	+ ":Link/Payment Entry:180",
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
				`viewStatement`.ncf,
				`viewStatement`.remarks,
				`viewStatement`.base_net_total as net_total,
				DATEDIFF(`viewStatement`.posting_date, CURDATE() ) as days,
				0 as discount_amount,
				`viewStatement`.base_total_taxes_and_charges as taxes,
				`viewStatement`.additional_discount_percentage,
				`viewStatement`.base_grand_total as grand_total,
				`viewStatement`.doctype,
				`viewReceipts`.document,
				`viewReceipts`.paid_amount,
				MAX(`viewReceipts`.posting_date) as last_payment,
				MAX(`viewReceipts`.reference_name) as reference_name,
				`viewStatement`.base_outstanding_amount as outstanding_amount 
			FROM
				`viewStatement`
			JOIN
				`tabSales Invoice`
			ON
				`viewStatement`.name = `tabSales Invoice`.name
			LEFT JOIN
				`viewReceipts`
			ON
				`viewStatement`.doctype = `viewReceipts`.reference_doctype
			AND	
				`viewStatement`.name = `viewReceipts`.reference_name
			WHERE
				{conditions}
			GROUP BY 
				`viewStatement`.name
			ORDER BY 
				`viewStatement`.posting_date desc
		""".format(conditions=get_conditions(filters)), as_dict=True, debug=True)
	
	elif filters.get("currency") == "Invoice Currency":
		data = frappe.db.sql("""
			SELECT 
				`viewStatement`.name,
				`viewStatement`.posting_date,
				`viewStatement`.customer,
				`viewStatement`.ncf,
				`viewStatement`.remarks,
				`viewStatement`.net_total,
				DATEDIFF(`viewStatement`.posting_date, CURDATE() ) as days,
				`viewStatement`.discount_amount,
				`viewStatement`.total_taxes_and_charges as taxes,
				`viewStatement`.additional_discount_percentage,
				`viewStatement`.grand_total,
				`viewStatement`.doctype,
				`tabJournal Entry`.total_debit as paid_amount,
				MAX(`tabJournal Entry`.posting_date) as last_payment,
				MAX(`tabJournal Entry`.name) as document,
				`viewStatement`.outstanding_amount
			FROM
				`viewStatement`
			JOIN
				`tabSales Invoice`
			ON
				`viewStatement`.name = `tabSales Invoice`.name
			LEFT JOIN
				`tabJournal Entry Account`
			ON
				`tabJournal Entry Account`.reference_type = `viewStatement`.doctype
			AND
				`tabJournal Entry Account`.reference_name = `viewStatement`.name
			LEFT JOIN
				`tabJournal Entry`
			ON
				`tabJournal Entry`.name = `tabJournal Entry Account`.parent
			AND	
				`tabJournal Entry`.docstatus = 1
			WHERE
				{conditions}
			GROUP BY 
				`viewStatement`.name
			ORDER BY 
				`tabSales Invoice`.custom_idx desc
		""".format(conditions=get_conditions(filters)), as_dict=True, debug=False)

	for row in data:
			discount, rate = get_discount_rate(row)
			itbis = (row.net_total - discount) * 0.18
			gross_amount = row.grand_total if row.additional_discount_percentage else row.grand_total - discount
			results.append(
				(
					row.name,
					row.posting_date,
					row.customer,
					row.ncf,
					row.remarks,
					row.net_total,
					# row.days,
					# "{}%".format(rate),
					# discount,
					itbis,
					gross_amount,
					# row.paid_amount,
					# gross_amount - row.outstanding_amount,
					row.paid_amount if flt(row.paid_amount) <= flt(row.outstanding_amount) else gross_amount,
					row.outstanding_amount ,
					row.last_payment,
					row.document,
				)
			)

	return results

def get_discount_rate(row): 
	if row.additional_discount_percentage:
		rate = row.additional_discount_percentage
		return flt(row.net_total * rate / 100.0, 2), rate
	rate = .00
	if row.days > 29:
		rate = 4.33
	if row.days > 59:
		rate = 8.67
	if row.days > 89:
		rate = 13.00
	# frappe.errprint("{} * {} / 100 = {}".format(row.base_total, rate, row.base_total * rate / 100.0))
	return flt(row.net_total * rate / 100.0, 2) or flt(row.discount), rate

