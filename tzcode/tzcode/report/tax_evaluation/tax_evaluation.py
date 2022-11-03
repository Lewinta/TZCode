# Copyright (c) 2013, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	return [
		"Total ITBIS Compra:Currency:200",
		"Total ITBIS Venta:Currency:200",
		"Difference:Currency:200",
	]

def get_data(filters):
	data = []
	result = frappe.db.sql("""
	SELECT (
		SELECT
			SUM(base_total_taxes_and_charges)
		FROM
			`tabPurchase Invoice`
		WHERE
			%(filters)s
	) AS `ITBIS_compra`,
	(
		SELECT
			SUM(base_total_taxes_and_charges) 
		FROM
			`tabSales Invoice`
		WHERE
			%(filters)s
	) AS `ITBIS_venta`
	""" % { "filters": get_filters(filters) }, filters, as_dict=True)
	for row in result:
		append_to_data(row, data)
	return data

def get_filters(filters):
	query = [" docstatus = 1"]
		
	if filters.get("from_date"):
		query.append("posting_date >= %(from_date)s")	

	if filters.get("to_date"):
		query.append("posting_date <= %(to_date)s")	

	return " AND ".join(query)

def append_to_data(row, data):
	data.append([
		row.ITBIS_compra,
		row.ITBIS_venta,
		flt(row.ITBIS_venta) - flt(row.ITBIS_compra)
	])
