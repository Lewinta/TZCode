# Copyright (c) 2013, Lewin Villar and contributors
# For license information, please see license.txt

import frappe, json
from frappe import _
from frappe.utils import cstr


def execute(filters={}):
	return get_columns(filters), get_data(filters)


def get_formatted_column(label, fieldtype, width):
	# [label]:[fieldtype/Options]:width
	parts = (
		_(label),
		fieldtype,
		cstr(width)
	)
	return ":".join(parts)


def get_columns(filters):
	if filters.get("summarized"):
		columns = (
			(_("Related Entity"), "Data", 160),
			(_("Paid Amount"), "Currency", 150),
			(_("Received Amount"), "Currency", 150),
			(_("Balance"), "Currency", 150),
		)
	else:
		columns = (
			(_("Document"), "Link/Journal Entry", 170),
			(_("Date"), "Date", 110),
			(_("Related Entity"), "Data", 160),
			(_("Paid DOP"), "Currency", 150),
			(_("Paid USD"), "Currency", 150),
			(_("Received DOP"), "Currency", 150),
			(_("Received USD"), "Currency", 150),
			(_("Balance DOP"), "Currency", 150),
			(_("Balance USD"), "Currency", 150),
			(_("Remarks"), "Data", 460),
		)

	formatted_columns = []

	for label, fieldtype, width in columns:
		formatted_columns.append(
			get_formatted_column(_(label), fieldtype, width)
		)

	return formatted_columns


def get_field(args):
	if len(args) == 2:
		doctype, fieldname = args
	else:
		return args if isinstance(args, str) \
			else " ".join(args)

	sql_field = "`tab{doctype}`.`{fieldname}`" \
		.format(doctype=doctype, fieldname=fieldname)

	return sql_field


def get_fields(filters):
	"""
		Return sql fields ready to be used on a query
	"""
	if filters.get("summarized"):
		fields = (
			("Journal Entry Account", "party"),
			("SUM(`tabJournal Entry Account`.`debit_in_account_currency`)"),
			("SUM(`tabJournal Entry Account`.`credit_in_account_currency`) * -1"),
			("SUM(`tabJournal Entry Account`.debit_in_account_currency - `tabJournal Entry Account`.credit_in_account_currency)"),
		)

	else:
		fields = (
			("Journal Entry Account", "parent"),
			("Journal Entry", "posting_date"),
			("Journal Entry Account", "party"),
			("Journal Entry Account", "debit"),
			("Journal Entry Account", "debit_in_account_currency"),
			("IF(`tabJournal Entry Account`.account_currency = 'DOP',`tabJournal Entry Account`.`credit` * -1, 0)"),
			("IF(`tabJournal Entry Account`.account_currency != 'DOP',`tabJournal Entry Account`.`credit_in_account_currency` * -1, 0)"),
			("IF(`tabJournal Entry Account`.account_currency = 'DOP',`tabJournal Entry Account`.debit - `tabJournal Entry Account`.credit, 0)"),
			("IF(`tabJournal Entry Account`.account_currency != 'DOP',`tabJournal Entry Account`.debit_in_account_currency - `tabJournal Entry Account`.credit_in_account_currency, 0)"),
			("Journal Entry", "remark"),
		)

	sql_fields = []

	for args in fields:
		sql_field = get_field(args)

		sql_fields.append(sql_field)

	return ", ".join(sql_fields)


def get_data(filters):
	fields = get_fields(filters)
	conditions = get_conditions(filters)
	extra_cond = "GROUP BY `tabJournal Entry Account`.`party`" if filters.get("summarized") else ""
	return frappe.db.sql("""
		SELECT
			{fields}
		FROM
			`tabJournal Entry`
		JOIN
			`tabJournal Entry Account`
		ON
			`tabJournal Entry`.name = `tabJournal Entry Account`.parent
		WHERE	
			{conditions}
		AND
			`tabJournal Entry Account`.party_type = 'Related Entity'
		{extra_cond}
		ORDER BY 
			`tabJournal Entry`.posting_date
		""".format(fields=fields, extra_cond=extra_cond, conditions=conditions or "1 = 1"),
		filters, debug=True
	)

def get_conditions(filters):
	conditions = [
		("Journal Entry Account", "docstatus", "=" , 1),
	]
	if filters.get('related_entity'):
		conditions.append(
			("Journal Entry Account", "party", "=", "%(related_entity)s")
		)

	sql_conditions = []

	for doctype, fieldname, compare, value in conditions:
		sql_condition = " `tab{doctype}`.`{fieldname}` {compare} {value}" \
            .format(doctype=doctype, fieldname=fieldname, compare=compare,
                    value=value)

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
