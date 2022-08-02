# Copyright (c) 2022, Yefri Tavarez and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import db as database

from frappe.utils import cstr


@frappe.whitelist(allow_guest=True)
def validate_token(token=None, scope=None):
	validate_args(token, scope)

	doctype = "Foreign Sites"
	filters = {
		"enabled": True,
		"encryption_key": token,
	}

	# first line of defense... if it does not exist
	# then return False
	if database.exists(doctype, filters):
		# let's narrow by the scope
		scope = cstr(scope).strip()
		
		doc = frappe.get_doc(doctype, filters)

		for csope in doc.scope.split("\n"):
			if cstr(csope).strip() == scope:
				return True

	return False


def validate_args(token, scope):
	if not cstr(token).strip():
		frappe.throw("Missing Token")

	if not cstr(scope).strip():
		frappe.throw("Missing Scope")
