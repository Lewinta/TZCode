import frappe
from tzcode.hook.accounts_controller import cancel_gl_entries, delete_gl_entries

def on_submit(doc, method):
    autoclose_so()

def on_cancel(doc, method):
    reopen_so()
    cancel_gl_entries(doc)

def on_trash(doc, method):
    delete_gl_entries(doc)

def autoclose_so():
	filters = {
		"docstatus": 1,
		"per_billed": 100,
		"status": ["!=", "closed"],
	}
	for name, in frappe.get_list("Sales Order", filters, as_list=True):
		so = frappe.get_doc("Sales Order", name)
		so.status = "Closed"
		so.db_update()
		frappe.db.commit()

def reopen_so():
	filters = {
		"docstatus": 1,
		"per_billed": ["<", 100],
		"status": "closed",
	}
	for name, in frappe.get_list("Sales Order", filters, as_list=True):
		so = frappe.get_doc("Sales Order", name)
		so.status = "To Bill"
		so.db_update()
		frappe.db.commit()