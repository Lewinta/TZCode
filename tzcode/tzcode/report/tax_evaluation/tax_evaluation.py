# Copyright (c) 2013, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	filters = filters or {}
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	
	if filters.get("summary"):
		return [
			{"label": _("Total ITBIS Compra"), "fieldname": "itbis_compra", "fieldtype": "Currency", "width": 200},
			{"label": _("Total ITBIS Venta"),  "fieldname": "itbis_venta",  "fieldtype": "Currency", "width": 200},
			{"label": _("Difference"),         "fieldname": "difference",   "fieldtype": "Currency", "width": 200},
		]
	return [
		{"label": _("Invoice"),     "fieldname": "name",         "fieldtype": "Link",     "options": "Purchase Invoice", "width": 180},
		{"label": _("Date"),        "fieldname": "posting_date", "fieldtype": "Date",     "width": 100},
		{"label": _("Tax ID"),      "fieldname": "tax_id",       "fieldtype": "Data",     "width": 140},
		{"label": _("Supplier"),    "fieldname": "supplier",     "fieldtype": "Link",     "options": "Supplier", "width": 220},
		{"label": _("Net Total"),   "fieldname": "net_total",    "fieldtype": "Currency", "width": 140},
		{"label": _("ITBIS"),       "fieldname": "itbis",        "fieldtype": "Currency", "width": 140},
		{"label": _("Grand Total"), "fieldname": "grand_total",  "fieldtype": "Currency", "width": 140},
	]

def get_data(filters):
	if filters.get("summary"):
		return get_summary_data(filters)
	return get_detail_data(filters)

def get_summary_data(filters):
	result = frappe.db.sql("""
	SELECT (
		SELECT
			SUM(base_total_taxes_and_charges)
		FROM
			`tabPurchase Invoice`
		WHERE
			%(filters)s
	) AS `itbis_compra`,
	(
		SELECT
			SUM(base_total_taxes_and_charges)
		FROM
			`tabSales Invoice`
		WHERE
			%(filters)s
	) AS `itbis_venta`
	""" % { "filters": get_filters(filters) }, filters, as_dict=True)

	data = []
	for row in result:
		data.append({
			"itbis_compra": row.itbis_compra,
			"itbis_venta":  row.itbis_venta,
			"difference":   flt(row.itbis_venta) - flt(row.itbis_compra),
		})
	return data

def get_detail_data(filters):
	rows = frappe.db.sql("""
		SELECT
			pi.name              AS name,
			pi.posting_date      AS posting_date,
			pi.tax_id            AS tax_id,
			pi.supplier          AS supplier,
			pi.base_net_total    AS net_total,
			pi.base_total_taxes_and_charges AS itbis,
			pi.base_grand_total  AS grand_total
		FROM
			`tabPurchase Invoice` pi
		WHERE
			{conditions}
		ORDER BY
			pi.posting_date DESC, pi.name DESC
	""".format(conditions=get_filters(filters, alias="pi")), filters, as_dict=True)

	if rows:
		rows.append({
			"name":        _("Total"),
			"net_total":   sum(flt(r.net_total)   for r in rows),
			"itbis":       sum(flt(r.itbis)       for r in rows),
			"grand_total": sum(flt(r.grand_total) for r in rows),
		})

	return rows

def get_filters(filters, alias=None):
	prefix = "{}.".format(alias) if alias else ""
	query = ["{}docstatus = 1".format(prefix)]

	if filters.get("from_date"):
		query.append("{}posting_date >= %(from_date)s".format(prefix))

	if filters.get("to_date"):
		query.append("{}posting_date <= %(to_date)s".format(prefix))

	return " AND ".join(query)
