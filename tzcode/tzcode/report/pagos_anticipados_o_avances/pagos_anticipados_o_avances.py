# Copyright (c) 2013, Lewin Villar and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr


def execute(filters={}):
	return get_columns(), get_data(filters)


def get_columns():
	columns = (
		("ID", "Link/Payment Entry", 140),
		("Fecha", "Date",90),
		("Beneficiario", "Data", 220),
		("Neto Pagado", "Currency", 120),
		("Bruto Pagado", "Currency", 120),
		("Observaciones",  "Data", 180),
	)

	formatted_columns = []

	for label, fieldtype, width in columns:
		formatted_columns.append(
			get_formatted_column(_(label), fieldtype, width)
		)

	return formatted_columns


def get_data(filters):
	fields = get_fields(filters)
	conditions = get_conditions(filters)

	return frappe.db.sql("""
		Select
			{fields}
		From
			`tabPayment Entry`
		Where
			{conditions}
		Order By
			`tabPayment Entry`.posting_date
		""".format(fields=fields, conditions=conditions or "1 = 1"),
            filters, debug=False)


def get_conditions(filters):
	conditions = [
		("Payment Entry", "docstatus", "=", 1),
		("Payment Entry", "name", "not in ", "(SELECT parent from `tabPayment Entry Reference` WHERE docstatus = 1)"),
	]
	if filters.get('from_date'):
		conditions.append(
			("Payment Entry", "posting_date", ">=", "%(from_date)s")
		)

	if filters.get('to_date'):
		conditions.append(
			("Payment Entry", "posting_date", "<=", "%(to_date)s")
		)

	sql_conditions = []

	for doctype, fieldname, compare, value in conditions:
		sql_condition = "`tab{doctype}`.`{fieldname}` {compare} {value}".format(doctype=doctype, fieldname=fieldname, compare=compare, value=value)
		sql_conditions.append(sql_condition)

	return " And ".join(sql_conditions)


def get_formatted_column(label, fieldtype, width):
	# [label]:[fieldtype/Options]:width
	parts = (
		_(label),
		fieldtype,
		cstr(width)
	)
	return ":".join(parts)


def get_fields(filters):
	"""
		Return sql fields ready to be used on a query
	"""

	fields = (
		("Payment Entry", "name"),
		("Payment Entry", "posting_date"),
		("Payment Entry", "cost_center"),
		("Payment Entry", "party_name"),
		("`tabPayment Entry`.paid_amount / 1.18"),
		("Payment Entry", "paid_amount"),
		("Payment Entry", "remarks"),
	)

	sql_fields = []

	for args in fields:
		sql_field = get_field(args)

		sql_fields.append(sql_field)

	return ", ".join(sql_fields)


def get_field(args):
	if len(args) == 2:
		doctype, fieldname = args
	else:
		return args if isinstance(args, str) \
			else " ".join(args)

	sql_field = "`tab{doctype}`.`{fieldname}`" \
		.format(doctype=doctype, fieldname=fieldname)

	return sql_field
