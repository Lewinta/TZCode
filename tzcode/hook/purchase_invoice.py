import frappe
from tzcode.hook.accounts_controller import cancel_gl_entries, delete_gl_entries

def validate(doc, method):
    set_cost_center(doc)

def on_cancel(doc, method):
    cancel_gl_entries(doc)

def on_trash(doc, method):
    delete_gl_entries(doc)

def set_cost_center(doc):
    for item in doc.items + doc.taxes:
        item.cost_center = doc.cost_center