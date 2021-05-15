import frappe

import frappe
from tzcode.hook.accounts_controller import cancel_gl_entries, delete_gl_entries

def on_cancel(doc, method):
    cancel_gl_entries(doc)

def on_trash(doc, method):
    delete_gl_entries(doc)